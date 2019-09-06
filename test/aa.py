import telnetlib
import time

import logging

from baremetal.common import locking as sw_lock, exceptions, utils, jsonobject, http
from baremetal.conductor import models

logger = logging.getLogger(__name__)


class HuaweiConfiguration(models.ModelBase):

    def __init__(self, username, password, host, port=23, timeout=10):
        super(HuaweiConfiguration, self).__init__()
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.sw_internal_cfg = {
            "sw_ssh_connect_timeout": 60,
            "sw_ssh_connect_interval": 10,
            "sw_max_connections": CONF.sw_coordination.max_connections
        }

        self.locker = None
        self.session_id = None
        if CONF.sw_coordination.backend_url:
            self.locker = coordination.get_coordinator(
                CONF.sw_coordination.backend_url,
                ('switch-' + self.config['ip']).encode('ascii'))
            self.locker.start()
            self.session_id = hex(self.locker._coord.client_id[0])
            logger.debug("zookeeper client connection[session_id:%s] opened." % self.session_id)

        self.lock_kwargs = {
            'locks_pool_size': int(self.sw_internal_cfg['sw_max_connections']),
            'locks_prefix': self.config['ip'],
            'timeout': CONF.sw_coordination.acquire_lock_timeout}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.locker:
            self.locker.stop()
            logger.debug("zookeeper client connection[session_id:%s] closed." % self.session_id)

    @contextlib.contextmanager
    def _get_connection(self):
        """Context manager providing a netmiko SSH connection object.

        This function hides the complexities of gracefully handling retrying
        failed connection attempts.
        """
        retry_exc_types = (paramiko.SSHException, EOFError, IndexError)

        # Use tenacity to handle retrying.
        @tenacity.retry(
            # Log a message after each failed attempt.
            after=tenacity.after_log(logger, logging.DEBUG),
            # Reraise exceptions if our final attempt fails.
            reraise=True,
            # Retry on SSH connection errors.
            retry=tenacity.retry_if_exception_type(retry_exc_types),
            # Stop after the configured timeout.
            stop=tenacity.stop_after_delay(
                int(self.sw_internal_cfg['sw_ssh_connect_timeout'])),
            # Wait for the configured interval between attempts.
            wait=tenacity.wait_fixed(
                int(self.sw_internal_cfg['sw_ssh_connect_interval'])),
        )
        def _create_connection():
            return telnetlib.Telnet(self.host, self.port, self.timeout)

        # First, create a connection.
        try:
            net_connect = _create_connection()
        except tenacity.RetryError as e:
            logger.error("Reached maximum SSH connection attempts, not retrying")
            raise exceptions.SwitchConnectionError(ip=self.config['ip'], error=e)
        except Exception as e:
            logger.error("Unexpected exception during SSH connection")
            logger.error(traceback.format_exc())
            raise exceptions.SwitchConnectionError(ip=self.config['ip'], error=e)

        # Now yield the connection to the caller.
        with net_connect:
            yield net_connect

    def _execute(self, command):
        logger.debug("command:%s" % command)
        session = None
        result = ""
        try:
            with sw_lock.PoolLock(self.locker, **self.lock_kwargs):
                with self._get_connection() as net_connect:

                    net_connect.read_until("Username:")
                    net_connect.write(self.username + '\n')
                    net_connect.read_until('Password:')
                    net_connect.write(self.password + '\n')
                    for i in command:
                        net_connect.write(i + '\n')
                    error_msg = net_connect.read_until("Error", timeout=2)
                    if "Error" in error_msg:
                        result = net_connect.read_very_eager()
                        logger.debug("execute command failed.error msg:%s" % result)
                        raise exceptions.ConfigSwitchError(command=command, error=result)
                    session.write('y' + '\n')
                    count = 0
                    while count < 60:
                        result += net_connect.read_very_eager()
                        if 'successfully' in result:
                            logger.debug("config switch end..")
                            break
                        else:
                            count += 1
                            time.sleep(1)
        finally:
            logger.debug("session close.")
            session.close()

        return result

    def set_vlan(self, ports):
        cmd = ['system-view']
        for port in ports:
            set_vlan_cmd = "port default vlan " + port.vlan_id
            cmd += ["interface " + port.port_name, set_vlan_cmd,
                    'port link-type access', 'commit', 'q']
        command = cmd + ['q', 'save']
        logger.debug("set vlan command:%s" % command)
        return self._execute(command)

    def unset_vlan(self, ports):
        cmd = ['system-view']
        unset_vlan_cmd = 'undo port default vlan'
        for port in ports:
            cmd += ["interface " + port, unset_vlan_cmd,
                    'undo port link-type', 'commit', 'q']
        command = cmd + ['q', 'save']
        logger.debug("unset vlan command:%s" % command)
        return self._execute(cmd + ['q', 'save'])

    def set_limit(self, limit_infos):
        enter_cmd = ['system-view']
        inbound_cmd = []
        outbound_cmd = []
        for info in limit_infos:
            template_name = info.template_name
            inbound_cmd += ["interface " + info.inbound_port,
                            "qos car inbound %s" % template_name, "commit", "q"]
            for port in info.outbound_ports:
                cir = int(info.bandwidth) * 1024
                cbs = min(524288, cir * 2)
                cmd1 = "qos lr cir %s kbps cbs %s kbytes outbound" % (cir, cbs)
                outbound_cmd += ["interface " + port, cmd1, "commit", "q"]

        command = enter_cmd + inbound_cmd + outbound_cmd + ['q', 'save']
        logger.debug("set limit command:%s" % command)
        return self._execute(command)

    def unset_limit(self, inbound_ports, outbound_ports):
        enter_cmd = ['system-view']
        inbound_cmd = []
        for port in inbound_ports:
            inbound_cmd += ["interface " + port, "undo qos car inbound", "commit", "q"]
        outbound_cmd = []
        for port in outbound_ports:
            outbound_cmd += ["interface " + port, "undo qos lr outbound", "commit", "q"]

        command = enter_cmd + inbound_cmd + outbound_cmd + ["q", "save"]
        logger.debug("unset limit command:%s" % command)
        return self._execute(command)

    def create_limit_template(self, templates):
        enter_cmd = ['system-view']
        create_command = []
        for template in templates:
            cir = int(template.bandwidth * 1.62 * 1024)
            qos_cmd = "qos car %s cir %s kbps" % (template.name, cir)
            create_command += [qos_cmd, 'commit']
        command = enter_cmd + create_command + ['q', 'save']
        logger.debug("create template command:%s" % command)
        return self._execute(command)

    def delete_limit_template(self, templates):
        enter_cmd = ['system-view']
        delete_command = []
        for template in templates:
            undo_cmd = 'undo qos car ' + template
            delete_command += [undo_cmd, 'commit']
        command = enter_cmd + delete_command + ['q', 'save']
        logger.debug("delete template command:%s" % command)
        return self._execute(command)

    def open_port(self, ports):
        enter_cmd = ['system-view']
        open_cmd = []
        for port in ports:
            open_cmd += ["interface " + port, "undo shutdown", "commit", "q"]
        command = enter_cmd + open_cmd + ["q", "save"]
        logger.debug("open ports command:%s" % command)
        return self._execute(command)

    def close_port(self, ports):
        enter_cmd = ['system-view']
        open_cmd = []
        for port in ports:
            open_cmd += ["interface " + port, "shutdown", "commit", "q"]
        command = enter_cmd + open_cmd + ["q", "save"]
        logger.debug("close ports command:%s" % command)
        return self._execute(command)

    def init_all_config(self, ports):
        enter_cmd = ['system-view']

        all_ports_cmd = []
        for port in ports:
            # 1. create limit template
            bandwidth = int(port.template_name.split('-')[-1])
            cir = int(bandwidth) * 1024
            create_template_cmd = ["qos car %s cir %s kbps" % (port.template_name, cir), "commit"]

            # 2. set vlan
            set_vlan_cmd = ["interface " + port.name,
                            "port default vlan " + port.vlan_id,
                            "port link-type access"]

            # 3. set limit
            inbound_cmd = ["qos car inbound %s" % port.template_name]
            cir = int(bandwidth) * 1024
            cbs = min(524288, cir * 2)
            outbound_cmd = []

            phy_port_cmds = []
            if port.phy_ports:
                for phy_port in port.phy_ports:
                    phy_port_outbound = ["interface " + phy_port,
                                         "qos lr cir %s kbps cbs %s kbytes outbound" % (cir, cbs)]
                    open_phy_port = ["undo shutdown", "q"]
                    phy_port_cmds += phy_port_outbound + open_phy_port
            else:
                outbound_cmd = ["qos lr cir %s kbps cbs %s kbytes outbound" % (cir, cbs)]

            open_port_cmd = ["undo shutdown", "q"]

            port_per_cmd = create_template_cmd + set_vlan_cmd \
                           + inbound_cmd + outbound_cmd \
                           + open_port_cmd + phy_port_cmds

            all_ports_cmd += port_per_cmd

        commands = enter_cmd + all_ports_cmd + ['commit', 'q', 'save']
        return self._execute(commands)

    def clean_all_config(self, ports):
        all_ports_cmd = []
        enter_cmd = ['system-view']
        for port in ports:
            # 1. unset vlan
            unset_vlan_cmd = ["interface " + port.name,
                              "undo port default vlan",
                              "undo port link-type"]

            # 2. unset limit
            phy_port_cmds = []
            if port.phy_ports:
                unset_limit_cmd = ["undo qos car inbound", "q"]
                for phy_port in port.phy_ports:
                    phy_port_outbound = ["interface " + phy_port, "undo qos lr outbound"]
                    open_phy_port = ["undo shutdown", "q"]
                    phy_port_cmds += phy_port_outbound + open_phy_port
            else:
                unset_limit_cmd = ["undo qos car inbound", "undo qos lr outbound", "q"]

            # 3. delete limit template
            delete_limit_template = ["undo qos car %s" % port.template_name]

            port_per_cmd = unset_vlan_cmd + unset_limit_cmd + delete_limit_template + phy_port_cmds
            all_ports_cmd += port_per_cmd

        commands = enter_cmd + all_ports_cmd + ['commit', 'q', 'save']

        return self._execute(commands)


class SwitchPlugin(object):

    @utils.replyerror
    def set_vlan(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.SetSwitchResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.set_vlan(body.ports)
        if "successfully" in result:
            for port in body.ports:
                logger.debug("set vlan %s for port %s successfully."
                             % (port.vlan_id, port.port_name))
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def unset_vlan(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.SetSwitchResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.unset_vlan(body.ports)
        if "successfully" in result:
            for port in body.ports:
                logger.debug("unset vlan for port %s successfully."
                             % ("Eth-Trunk %s" % port))
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def set_limit(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.SetSwitchResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.set_limit(body.limit_infos)
        if "successfully" in result:
            for info in body.limit_infos:
                logger.debug("set limit for port %s successfully." % info.inbound_port)
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def unset_limit(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.SetSwitchResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.unset_limit(body.inbound_ports, body.outbound_ports)
        if "successfully" in result:
            for port in body.inbound_ports:
                logger.debug("unset limit for port %s successfully." % port)
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def create_limit_template(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.SetSwitchResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.create_limit_template(body.templates)
        if "successfully" in result:
            for template in body.templates:
                logger.debug("create limit template %s successfully."
                             % template.name)
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def delete_limit_template(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.SetSwitchResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.delete_limit_template(body.templates)
        if "successfully" in result:
            for template in body.templates:
                logger.debug("delete limit template %s successfully."
                             % template)
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def open_port(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.AgentResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.open_port(body.ports)
        if "successfully" in result:
            for port in body.ports:
                logger.debug("open port %s successfully." % port)
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def close_port(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.AgentResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        result = my_telnet.open_port(body.ports)
        if "successfully" in result:
            for port in body.ports:
                logger.debug("close port %s successfully." % port)
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def init_all_config(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.AgentResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        if body.is_bound:
            result = my_telnet.init_all_config(body.bond_group.ports)
        else:
            result = my_telnet.init_all_config(body.port_group.ports)
        if "successfully" in result:
            logger.debug("init port config successfully.")
        return jsonobject.dumps(rsp)

    @utils.replyerror
    def clean_all_config(self, req):
        body = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = models.AgentResponse()
        my_telnet = SwitchConfiguration(
            body.username, body.password, body.host)
        if body.is_bound:
            result = my_telnet.clean_all_config(body.bond_group.ports)
        else:
            result = my_telnet.clean_all_config(body.port_group.ports)
        if "successfully" in result:
            logger.debug("clean port config successfully.")
        return jsonobject.dumps(rsp)


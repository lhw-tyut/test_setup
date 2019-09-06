import telnetlib
import time

import logging
logger = logging.getLogger(__name__)

class SwitchConfiguration():

    def __init__(self, username, password, host, port=23, timeout=10):
        super(SwitchConfiguration, self).__init__()
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout

    def _execute(self, command):
        logger.debug("command:%s" % command)
        session = None
        result = ""
        try:
            session = telnetlib.Telnet(self.host, self.port, self.timeout)
            session.read_until("Username:")
            session.write(self.username + '\n')
            session.read_until('Password:')
            session.write(self.password + '\n')
            session.read_until('[Y/N]:')
            for i in command:
                session.write(i + '\n')
            error_msg = session.read_until("Error", timeout=2)
            if "Error" in error_msg:
                result = session.read_very_eager()
                logger.debug("execute command failed.error msg:%s" % result)
                #raise exceptions.ConfigSwitchError(command=command, error=result)
            session.write('y' + '\n')
            count = 0
            while count < 60:
                result += session.read_very_eager()
                if result.count('successfully') == 2:
                    logger.debug("config switch end..")
                    break
                else:
                    count += 1
                    time.sleep(1)
        finally:
            logger.debug("session close.")
            session.close()

        return result

    def create_limit_template(self, templates):
        enter_cmd = ['n', 'system-view']
        create_command = []
        for template in templates:
            cir = int(template["bandwidth"] * 1.62 * 1024)
            qos_cmd = "qos car %s cir %s kbps" % (template["name"], cir)
            create_command += [qos_cmd, 'commit']
        command = enter_cmd + create_command + ['q', 'save']
        logger.debug("create template command:%s" % command)
        return self._execute(command)

    def delete_limit_template(self, templates):
        enter_cmd = ['n', 'system-view']
        delete_command = []
        for template in templates:
            undo_cmd = 'undo qos car ' + template
            delete_command += [undo_cmd, 'commit']
        command = enter_cmd + delete_command + ['q', 'save']
        logger.debug("delete template command:%s" % command)
        return self._execute(command)


def create_limit_template():
    username = "admin-ssh"
    password = "CDS-china1"
    host = "10.177.178.241"

    templates = [
        {
            "name": "public_test",
            "bandwidth": 20
        },
        {
            "name": "private_test",
            "bandwidth": 100
        }

    ]



    my_telnet = SwitchConfiguration(
        username, password, host)
    my_telnet.create_limit_template(templates)
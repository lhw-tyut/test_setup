import uuid

def gen_init_images(interfaces=[], bonds=[], vlans=[], dns=[]):
    body = {
        "uuid": str(uuid.uuid4()),
        "username": "root",
        "password": "cds-china",
        "os_type": "linux",
        "networks": {
            "interfaces": interfaces,
            "bonds": bonds,
            "vlans": vlans,
            "dns": dns
        },
    }
    return body

class NetworkMetadata(object):
    def __init__(self, interfaces=None, interfaces_vlan=None, bonds=None, bonds_vlan=None):
        self.interfaces = interfaces
        self.interfaces_vlan = interfaces_vlan
        self.bonds = bonds
        self.bonds_vlan = bonds_vlan

    def _get_interfaces(self):
        if self.interfaces:
            return []
        else:
            for interface in self.interfaces:

        links = []
        # put all physical nic information into links

        count = 0
        # scenario 1: just set ip on physical nic
        if networks.interfaces:
            for iface in networks.interfaces:
                link = {
                    "id": "NIC" + str(count),
                    'ethernet_mac_address': iface.mac,
                    'type': "phy"
                }
                count = count + 1
                links.append(link)

        # scenario 2: do bonding on two physical nic
        if networks.bonds:
            for group in networks.bonds:
                bond_links = []
                for nic in group.bond_nics:
                    link = {
                        "id": "NIC" + str(count),
                        "ethernet_mac_address": nic,
                        "type": "phy"
                    }
                    count = count + 1
                    links.append(link)
                    bond_links.append(link['id'])

                # put bonds into links
                bond = {
                    "id": group.id,
                    "type": "bond",
                    "bond_mode": constants.BOND_MODE.get(group.bond_mode)
                }
                bond.update({"bond_links": bond_links})
                if os_type in ["windows"]:
                    bond.update({"ethernet_mac_address": (group.bond_nics)[0]})
                links.append(bond)

        # scenario 3: set vlan on physical nic or bond nic
        if networks.vlans:
            for group in networks.vlans:
                vlan = {
                    "id": group.id,
                    "type": "vlan",
                    "vlan_id": int(group.vlan_id)
                }
                # set vlan on physical nic, eg: eno1.1000
                if common_utils.is_valid_mac(group.vlan_nic):
                    link = {
                        "id": "NIC" + str(count),
                        "ethernet_mac_address": group.vlan_nic,
                        "type": "phy"
                    }
                    count = count + 1
                    links.append(link)
                    vlan.update({"vlan_link": link["id"]})
                    vlan.update({"vlan_mac_address": group.vlan_nic})
                # set vlan on bond nic, eg: bond0.1000
                else:
                    vlan.update({"vlan_link": group.vlan_nic})
                    for bond in networks.bonds:
                        if group.vlan_nic == bond.id:
                            vlan.update({"vlan_mac_address": (bond.bond_nics)[0]})

                links.append(vlan)

        return links

    def _get_network(self, groups, links=None):
        nets = []
        for group in groups:
            if group.ipaddr:
                network = {
                    "ip_address": group.ipaddr,
                    "link": group.id,
                    "netmask": group.netmask,
                    "type": "ipv4"
                }
                if group.gateway:
                    routes = [{
                        "network": "0.0.0.0",
                        "netmask": "0.0.0.0",
                        "gateway": group.gateway
                    }]
                    network.update({"routes": routes})
                if group.dns:
                    if "window" in self.os_type:
                        services = []
                        for dns_ip in group.dns:
                            services.append({
                                "address": dns_ip,
                                "type": "dns"
                            })
                        network.update({"services": services})
                    else:
                        network.update({"dns_nameservers": group.dns})
                if group.id:
                    network.update({"link": group.id})
                else:
                    for link in links:
                        if link["ethernet_mac_address"] == group.mac:
                            network.update({"link": link["id"]})
                            break

                nets.append(network)
        return nets

    def _get_networks(self, networks, links):
        nets = []
        if networks.interfaces:
            nets += self._get_network(networks.interfaces, links)

        if networks.bonds:
            nets += self._get_network(networks.bonds)

        if networks.vlans:
            nets += self._get_network(networks.vlans)

        return nets

    def get_network_metadata(self):
        network_meta = self.network_info
        links = self._get_links(network_meta, self.os_type)
        networks = self._get_networks(network_meta, links)
        services = [{"address": dns, "type": "dns"} for dns in network_meta.dns]
        network_data = {
            "links": links,
            "networks": networks,
            "services": services
        }
        logger.debug("network_data for baremetal[uuid:%s]:%s" % (self.uuid, network_data))
        return network_data
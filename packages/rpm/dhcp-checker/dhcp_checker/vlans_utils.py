#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from dhcp_checker import utils
import re


class VlansContext(object):

    def __init__(self, iface, vlans, delete=False):
        """
        @ifaces - list or tuple of (iface, vlan) pairs
        """
        self.vlans = [Vlan(iface, vlan) for vlan in vlans]
        self.delete = delete

    def start(self):
        for vlan in self.vlans:
            vlan.up()

    def end(self):
        for vlan in self.vlans:
            vlan.down(delete=self.delete)

    def __enter__(self):
        self.start()
        return self.vlans

    def __exit__(self, type, value, traceback):
        self.end()


class Vlan(object):

    def __init__(self, iface, number, vlan_config=None):
        """
        """
        self.iface = iface
        self.number = number
        self.config = vlan_config if vlan_config else {}

    @property
    def ident(self):
        return '{0}.{1}'.format(self.iface, self.number)

    @property
    def state(self):
        state = utils.command_util('ip', 'link', 'show', self.ident)
        response = re.search(r'state (?P<state>[A-Z]*)', state.stdout.read())
        if response:
            return response.groupdict()['state']
        else:
            return None

    def create(self):
        return utils.command_util("ip", "link", "add", "link", self.iface,
            "name", self.ident, "type", "vlan", "id", self.number)

    def link_up(self):
        return utils.command_util('ip', 'link', 'set',
                                  'dev', self.ident, 'up')

    def delete(self):
        return utils.command_util("ip", "link", "del", "dev", self.ident)

    def link_down(self):
        return utils.command_util('ip', 'link', 'set',
                                  'dev', self.ident, 'down')

    def up(self):
        self.create()
        self.link_up()

    def down(self, delete=False):
        if delete:
            self.link_down()
            self.delete()

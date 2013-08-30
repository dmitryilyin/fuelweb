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


@utils.coroutine
def links_manager():
    def up(config):
        utils.command_util('ifconfig', self.config['vlan_id'], 'up')
    def down(config):
        utils.command_util('ifconfig', self.config['vlan_id'], 'down')

    while True:
        command, config = (yield)


@utils.coroutine
def vconfig_manager():
    def create():
        pass
    def delete():
        pass

    while True:
        command, config = (yield)


@utils.coroutine
def sysconfig_manager():
    def create():
        pass
    def delete():
        pass
        while True:
            command, config = (yield)


class VlansContext(object):

    def __init__(self, vlans):
        """
        @ifaces - list or tuple of (iface, vlan) pairs
        """
        self.vlans = vlans

    def __enter__(self):
        for vlan in self.vlans:
            vlan.up()

    def __exit__(self, type, value, traceback):
        for vlan in self.vlans:
            vlan.down(delete=True)


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

    def up(self):
        up = lambda: utils.command_util('ifconfig', self.ident, 'up')
        create = lambda: utils.command_util('vconfig', 'add',
                                            self.iface, self.number)
        state = self.state
        if state == None:
            create()
            up()
        elif state == 'DOWN':
            up()

    def down(self, delete=False):
        state = self.state
        if state != None:
            utils.command_util('ifconfig', self.ident, 'down')
            if delete:
                utils.command_util('vconfig', 'rem', self.ident)
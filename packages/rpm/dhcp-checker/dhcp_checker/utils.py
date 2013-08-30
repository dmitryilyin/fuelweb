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
import subprocess
import functools


def command_util(*command):
    """object with stderr and stdout
    """
    return subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def _check_vconfig():
    """Check vconfig installed or not
    """
    return not command_util('which', 'vconfig').stderr.read()


def check_iface_exist(iface):
    """Check provided interface exists
    """
    return not command_utils("ip","link", "show", iface).stderr.read()



def coroutine(func):
    @functools.wraps(func)
    def starter(*args, **kwargs):
        coro = func(*args, **kwargs)
        coro.next()
        return coro
    return starter


def manager_fabric():
    return vconfig_manager()


@coroutine
def vconfig_manager():
    while True:
        command, config = (yield)
        if command == 'create':
            command_util(
            'vconfig', 'add', config['iface'], config['number'])
            cmd = ['ifconfig', config['vlan_id']]
            cmd += config['ip']
            command_util('ifconfig', config['vlan_id'], 'up')
        if command == 'delete':
            command_util('ifconfig', config['vlan_id'], 'down')
            command_util('vconfig', 'rem', config['vlan_id'])


class WithVlans(object):

    def __init__(self, ifaces):
        """
        @ifaces - list of ifaces
        """
        self.ifaces = ifaces if isinstance(ifaces, (tuple, list)) \
            else [ifaces]
        self.vlans = []


    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


class Vlan(object):

    path_template = '/etc/sysconfig/network-scripts/ifcfg-{0}.{1}'

    manager = manager_fabric()

    def __init__(self, iface, number, vlan_config=None):
        """
        """
        self.iface = iface
        self.number = number
        self.config = vlan_config if vlan_config else {}
        self.config['vlan_id'] = '{0}.{1}'.format(self.iface, self.number)
        self.config['iface'] = self.iface
        self.config['number'] = self.number
        self.status = None

    def up(self):
        self.manager.send(('create', self.config))
        self.status = True

    def down(self):
        self.manager.send(('delete', self.config))
        self.status = False




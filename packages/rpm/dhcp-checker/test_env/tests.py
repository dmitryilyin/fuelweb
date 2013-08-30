#!/usr/bin/python
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
import json
import unittest

from dhcp_checker import utils
from dhcp_checker import vlans
from dhcp_checker import api


class TestDhcpServers(unittest.TestCase):
    pass


class VlanCreationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vlan = vlans.Vlan('eth0', '100')

    def test_vlan_creation(self):
        self.vlan.up()
        self.assertTrue(self.vlan.state)

    def test_vlan_deletion(self):
        self.assertTrue(self.vlan.state)
        self.vlan.down()


class VlanCreationWithExistingTestCase(unittest.TestCase):


    def test_check_vlan_down_status(self):
        self.vlan_down = vlans.Vlan('eth0', '110')
        self.vlan_down.create()
        self.assertEqual(self.vlan_down.state, 'DOWN')
        self.vlan_down.delete()

    def test_repeat_created_vlan(self):
        self.vlan_up = vlans.Vlan('eth0', '112')
        self.vlan_up.up()
        self.assertEqual(self.vlan_up.state, 'UP')
        self.vlan_up.delete()


class WithVlanDecoratorTestCase(unittest.TestCase):


    def setUp(self):
        fixtures = [('eth0', '101'), ('eth0', '102')]
        self.vlans = (vlans.Vlan(item[0], item[1]) for item in fixtures)

    def test_with_vlan_enter(self):
        with vlans.VlansContext(self.vlans):
            for v in self.vlans:
                self.assertEqual('UP', v.state)
        for v in self.vlans:
            self.assertEqual(None, v.state)

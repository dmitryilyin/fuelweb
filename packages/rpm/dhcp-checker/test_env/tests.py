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


def test_check_roque_dhcp_all():
    expected = {"eth2": [["08:00:27:66:44:3c", "10.10.0.8"],
                         ["08:00:27:b5:26:9c", "10.10.0.4"]],
                "eth1": [["08:00:27:89:d7:f9", "192.168.0.5"]],
                "eth0": [["52:54:00:12:35:02", "10.0.2.2"]]}
    resp = subprocess.Popen(['sudo', 'dhcp-check'],
                            stdout=subprocess.PIPE)
    data = json.loads(resp.stdout.read())
    assert data == expected


def test_check_one_eth():
    eth = 'eth1'
    expected = {"eth1": [["08:00:27:89:d7:f9", "192.168.0.5"]]}
    resp = subprocess.Popen(['sudo', 'dhcp-check', '--eth=%s' % eth],
                            stdout=subprocess.PIPE)
    data = json.loads(resp.stdout.read())
    assert data == expected

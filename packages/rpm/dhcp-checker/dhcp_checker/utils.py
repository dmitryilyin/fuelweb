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
    # will be used later
    @functools.wraps(func)
    def starter(*args, **kwargs):
        coro = func(*args, **kwargs)
        coro.next()
        return coro
    return starter








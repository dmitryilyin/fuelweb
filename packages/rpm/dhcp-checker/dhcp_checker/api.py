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

from scapy.all import *
import itertools
import multiprocessing
import functools


def pick_ip(range_start, range_end):
    """Given start_range, end_range generate list of ips
        >>> next(pick_ip('192.168.1.10','192.168.1.13'))
        '192.168.1.10'
    """
    split_address = lambda ip_address: \
        [int(item) for item in ip_address.split('.')]
    range_start = split_address(range_start)
    range_end = split_address(range_end)
    i = 0
    # ipv4 subnet cant be longer that 4 items
    while i < 4:
        # 255 - end of subnet
        if not range_start[i] == range_end[i] and range_start[i] < 255:
            yield '.'.join([str(item) for item in range_start])
            range_start[i] += 1
        else:
            i += 1


def format_options(options):
    """Util for serializing dhcp options
    @options = [1,2,3]
    return '\x01\x02\x03'
    """
    return "".join((chr(item) for item in options))

def single_format(func):
    """All request formatting logic lies here
    """
    @functools.wraps(func)
    def formatter(*args, **kwargs):
        iface = args[0]
        ans = func(*args, **kwargs)
        columns = ('iface', 'mac', 'server_ip', 'server_id', 'gateway',
               'dport', 'message', 'yiaddr')
        data = []
        #scapy stores all sequence of requests
        #so ans[0][1] would be response to first request
        for response in ans:
            dhcp_options = dict((option for option in
                                 response[1][DHCP].options[:-1]
                                 if isinstance(option, tuple)))

            results = (
                iface, response[1][Ether].src, response[1][IP].src,
                dhcp_options['server_id'], response[1][BOOTP].giaddr,response[1][UDP].sport,
                DHCPTypes[dhcp_options['message-type']], response[1][BOOTP].yiaddr)
            data.append(dict(zip(columns, results)))
        return data
    return formatter


def multiproc_map(func):
    # multiproc map could not work with format *args
    @functools.wraps(func)
    def workaround(*args, **kwargs):
        args = args[0] if isinstance(args[0], (tuple, list)) else args
        return func(*args, **kwargs)
    return workaround


@multiproc_map
@single_format
def check_dhcp_on_eth(iface, timeout):
    """Check if there is roque dhcp server in network on given iface
        @eth - name of the ethernet interface
        >>> check_dhcp_on_eth('eth1')
    """

    conf.iface = iface

    conf.checkIPaddr = False
    dhcp_options = [("message-type", "discover"),
                    ("param_req_list", format_options([1, 2, 3, 4, 5, 6, 11, 12, 13, 15, 16, 17, 18, 22, 23,
                        28, 40, 41, 42, 43, 50, 51, 54, 58, 59, 60, 66, 67])),
                    "end"]

    fam, hw = get_if_raw_hwaddr(iface)
    dhcp_discover = (
        Ether(src=hw, dst="ff:ff:ff:ff:ff:ff") /
        IP(src="0.0.0.0", dst="255.255.255.255") /
        UDP(sport=68, dport=67) /
        BOOTP(chaddr=hw) /
        DHCP(options=dhcp_options))
    ans, unans = srp(dhcp_discover, multi=True,
                     nofilter=1, timeout=timeout, verbose=0)
    return ans


def check_dhcp(ifaces, timeout=5):
    """Given list of ifaces. Process them in separate processes
        >>> check_dhcp(['eth1', 'eth2'])
    """
    pool = multiprocessing.Pool(len(ifaces))
    return itertools.chain(*pool.map(check_dhcp_on_eth,
        ((iface, timeout) for iface in ifaces)))


@single_format
def check_dhcp_request(iface, server, range_start, range_end, timeout=5):
    """Provide interface, server endpoint and pool of ip adresses
        Should be used after offer received
        >>> check_assignment('eth1','10.10.0.5','10.10.0.10','10.10.0.15')
    """

    conf.iface = iface

    conf.checkIPaddr = False

    fam, hw = get_if_raw_hwaddr(iface)



    ip_address = next(pick_ip(range_start, range_end))

    # note lxc dhcp server does not respond to unicast
    dhcp_request = (Ether(src=hw, dst="ff:ff:ff:ff:ff:ff") /
                    IP(src="0.0.0.0", dst="255.255.255.255") /
                    UDP(sport=68, dport=67) /
                    BOOTP(chaddr=hw) /
                    DHCP(options=[("message-type", "request"),
                                  ("server_id", server),
                                  ("requested_addr", ip_address), "end"]))
    ans, unans = srp(dhcp_request, nofilter=1, multi=True,
                     timeout=timeout, verbose=0)
    return ans

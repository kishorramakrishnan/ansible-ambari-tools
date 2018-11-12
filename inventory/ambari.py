#!/usr/bin/env python
# Copyright 2018, Hortonworks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2018, Gabor Lekeny <glekeny@hortonworks.com>

"""
Ambari inventory script for Ansible
"""

# Standard libraries
import collections
import json
import os
import sys

try:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:
    from configparser import ConfigParser

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

# 3rd party libraries
from ambariclient.client import Ambari

# helper script fetching component configs
from ambari_tools.fetch_configs import get_all_configs
from ambari_tools.stack_versions import get_stack_versions


def get_ambari_config():
    """
    We expect to have only one Ambari cluster configured
    """
    path = os.path.join(os.getcwd(), 'ambari.cfg')
    config = ConfigParser()
    config.read(path)

    url = config.get('default', 'url')
    user = config.get('default', 'user')
    password = config.get('default', 'password')

    ansible_vars = {
        'ambari_url': url,
        'ambari_user': user,
        'ambari_password': password,
    }

    return ansible_vars


def get_node_props(node):
    """
    Set IP address for hostname
    """
    return {
        'ansible_host': node.ip
    }


def list_running_hosts(config):
    """
    Use new style inventory script (_meta) available from 1.3 as it has
    performance improvement not running inventory script for each node.
    """
    parser = urlparse(config['ambari_url'])
    client = Ambari(host=parser.hostname, port=parser.port,
                    protocol=parser.scheme,
                    username=config['ambari_user'], password=config['ambari_password'],
                    validate_ssl=False)
    cluster = next(client.clusters)

    inventory = collections.defaultdict(
        lambda: {'hosts': []},
        _meta={'hostvars': {}},
        all={}
    )

    # hostvars
    ambari_host = parser.hostname
    for host in cluster.hosts:
        inventory['_meta']['hostvars'][host.host_name] = get_node_props(host)
        if ambari_host == host.ip:
            ambari_host = host.host_name

    # groups
    for comp in cluster.host_components:
        inventory[comp.component_name]['hosts'].append(comp.host_name)

    # configs for all the components
    component_configs = get_all_configs(parser.scheme,
                                        parser.hostname,
                                        parser.port,
                                        parser.path,
                                        config['ambari_user'],
                                        config['ambari_password'],
                                        cluster.cluster_name)
    # stack versions

    stack, version = get_stack_versions(parser.scheme,
                                        parser.hostname,
                                        parser.port,
                                        parser.path,
                                        config['ambari_user'],
                                        config['ambari_password'],
                                        cluster.cluster_name)
    # group_vars
    inventory['all']['vars'] = {
        'ambari_cluster_name': cluster.cluster_name,
        'ambari_host': ambari_host,
        'ambari_password': config['ambari_password'],
        'ambari_url': config['ambari_url'],
        'ambari_user': config['ambari_user'],
        'ambari_component_configs': component_configs,
        'host_stack': stack,
        'host_stack_version': version
    }


    return inventory


def main():
    """
    Main entry point
    """
    config = get_ambari_config()
    inventory = list_running_hosts(config)
    json.dump(inventory, sys.stdout)


if __name__ == '__main__':
    main()

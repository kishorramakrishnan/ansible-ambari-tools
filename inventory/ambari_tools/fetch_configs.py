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
# (c) 2018, Endre Kovacs <ekovacs@hortonworks.com>

"""
Helper script for populating the inventory with all the component configs.
"""

# Standard libraries
import json
import logging
from .common  import get_ambari_url, \
                   get, \
                   assert_return_code, \
                   parse_config


def get_config_types(ambari_url, user, password, cluster_name, connection_timeout):
    r = get(ambari_url, user, password,
            '/api/v1/clusters/{0}?fields=Clusters/desired_configs'.format(cluster_name),
            connection_timeout)
    assert_return_code(r, 200, 'cluster config types')
    config = json.loads(r.content)
    config_types = parse_config(r,
                                config,
                                lambda conf: conf['Clusters']['desired_configs'] is not None,
                                lambda conf: conf['Clusters']['desired_configs'])
    return config_types


def get_cluster_config(ambari_url, user, password, cluster_name, config_type, config_tag, connection_timeout):
    r = get(ambari_url, user, password,
            '/api/v1/clusters/{0}/configurations?type={1}&tag={2}'.format(cluster_name, config_type, config_tag),
            connection_timeout)
    assert_return_code(r, 200, 'cluster configurations')
    config = json.loads(r.content)
    # skip config items without required property
    if 'properties' not in config['items'][0]:
        return ""
    return parse_config(r,
                        config,
                        lambda config: config['items'][0]['properties'] is not None,
                        lambda config: config['items'][0])


def escape_values(confs):
    from ansible.template import Templar
    helper = Templar(None)

    for k in confs:
        value = confs[k]
        if helper._contains_vars(value):
            confs[k] = '{% raw %}' + value + '{% endraw %}'

    return confs


def get_all_configs(protocol, host, port, context_path, username, password, cluster_name, connection_timeout=10):
    ambari_url = get_ambari_url(protocol, host, port, context_path)
    try:
        # Get config using the effective tag
        config_types = get_config_types(ambari_url, username, password, cluster_name, connection_timeout)
        ambari_cluster_config_facts = {}
        for config_type in config_types:
            config = get_cluster_config(ambari_url, username, password, cluster_name, config_type, config_types[config_type]['tag'], connection_timeout)
            # skip config items without required property
            if not config:
                continue
            safe_confs = escape_values(config['properties'])
            ambari_cluster_config_facts[config_type] = safe_confs

        return ambari_cluster_config_facts
    except Exception as e:
        logging.error("An exception occurred while connecting to Ambari.")
        raise e

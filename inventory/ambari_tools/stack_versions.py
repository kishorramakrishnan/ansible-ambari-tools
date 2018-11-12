import json
from .common import get_ambari_url, get, assert_return_code, parse_config


def get_stack_versions(protocol, host, port, context_path, username, password, cluster_name, connection_timeout=10):
    ambari_url = get_ambari_url(protocol, host, port, context_path)
    path = '/api/v1/clusters/{0}/stack_versions/1'.format(cluster_name)
    resp = get(ambari_url, username, password, path, connection_timeout)
    assert_return_code(resp, 200, 'cluster stack versions')
    config = json.loads(resp.content)
    stack_version = parse_config(resp,
                                 config,
                                 lambda conf: conf['ClusterStackVersions'] is not None,
                                 lambda conf: conf['ClusterStackVersions'])
    return stack_version['stack'], stack_version['version']

def to_node_identity_xml(groups_to_render):
    i = 1
    xml_result = ""
    for group in groups_to_render:
        for host in group['cn']:
            xml_result += '<property name="Node Identity {0}">CN={1}, OU={2}</property>'.format(i, host, group['ou'])
            i += 1
    return xml_result


class FilterModule(object):
    def filters(self):
        return {
            'to_node_identity_xml': to_node_identity_xml
        }
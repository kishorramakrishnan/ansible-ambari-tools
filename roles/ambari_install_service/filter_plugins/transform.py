
def group_by_config_types(service_conf_response):
    '''
    Process ambari response for /api/v1/stacks/$stack/versions/$stack_version/services/$serviceName?fields=*,configurations/StackConfigurations/*
    :param service_conf_response:
    :return: a dict with such datastructure: { config_type1: { key1: value1, key2: value2 }, config_type2: { key3: value3, key4: value4} }
    '''
    configs = service_conf_response['json']['configurations']
    result_dict = {}
    for config in configs:
        prop_key = config['StackConfigurations']['property_name']
        prop_value = config['StackConfigurations']['property_value']
        entry_map = {prop_key: prop_value}
        type = config['StackConfigurations']['type'].split(".")[0]
        configs_for_type = result_dict.get(type, {})
        configs_for_type.update(entry_map)
        result_dict.update({type: configs_for_type})
    return result_dict


def to_initial_conf_request(confs_grouped_by_conf_types, initial_tag='INITIAL_TAG', version=1):
    results = []
    for k in confs_grouped_by_conf_types:
        results.append({'type': k, 'tag': initial_tag, 'version': version, 'properties': confs_grouped_by_conf_types[k]})
    return results


def filter_existing_tags(initial_conf_list, existing_configtype_tags_response):
    result_list = []
    existing_tags_list = existing_configtype_tags_response['json']['items']
    # pre process existing configtypes list
    configtypes_tag_map = {}
    for existing_tag in existing_tags_list:
        type = existing_tag['type']
        tags_for_type = configtypes_tag_map.get(type, [])
        if existing_tag['tag'] not in tags_for_type:
            tags_for_type.append(existing_tag['tag'])
            configtypes_tag_map.update({type: tags_for_type})

    for conf_to_post in initial_conf_list:
        conf_type = conf_to_post['type']
        conf_tag = conf_to_post['tag']

        if not configtypes_tag_map.get(conf_type) or conf_tag not in configtypes_tag_map.get(conf_type):
            result_list.append(conf_to_post)
    return result_list

class FilterModule(object):
    def filters(self):
        return {
            'group_by_config_types': group_by_config_types,
            'to_initial_conf_request': to_initial_conf_request,
            'filter_existing_tags': filter_existing_tags,
        }
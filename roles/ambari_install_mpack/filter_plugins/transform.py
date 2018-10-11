def to_repository_version_update(repository_version_response, mpack_stack_name, base_url, latest_build):
    # result = {}
    my_dict = repository_version_response['json']
    my_dict.pop('href', None)
    repo_list = my_dict['operating_systems'][0]['repositories']
    for repo in repo_list:
        if mpack_stack_name in repo['Repositories']['repo_name']:
            replacement = base_url + '/' + latest_build
            repo['Repositories'].update({'base_url': replacement})
    return my_dict


class FilterModule(object):
    def filters(self):
        return {
            'to_repository_version_update': to_repository_version_update
        }
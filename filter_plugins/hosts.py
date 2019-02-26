import re

def get_all_hosts(unbound_file):
    all_hosts = []
    with open(unbound_file) as ub_file:
        content = ub_file.read()
        regex = r'([\"a-z0-9]: *) +"+([0-9.  ]*) ([a-z-0-9]+)'
        matches = re.findall(regex, content)
        for match in matches:
            all_hosts.append(match[2])
    return all_hosts



class FilterModule(object):
    def filters(self):
        return {
            'get_all_hosts': get_all_hosts
        }
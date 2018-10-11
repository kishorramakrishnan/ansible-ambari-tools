import requests


def get(ambari_url, user, password, path, connection_timeout):
    headers = {'X-Requested-By': 'ambari'}
    r = requests.get(ambari_url + path, auth=(user, password),
                     headers=headers, timeout=connection_timeout)
    return r


def get_ambari_url(protocol, host, port, context_path=''):
    return '{0}://{1}:{2}{3}'.format(protocol, host, port, context_path)


def assert_return_code(request, expected_code, target_message=''):
    try:
        request.status_code == expected_code
    except AssertionError as e:
        e.message = 'Could not get {0}: ' \
                    'request code {1}, ' \
                    'request message {2}'.format(target_message, request.status_code, request.content)
        raise


def parse_config(request, config, assertor, selector):
    try:
        assert assertor(config)
        return selector(config)
    except (KeyError, AssertionError) as e:
        e.message = 'Could not find the right properties key, ' \
                    'request code {0}, ' \
                    'possibly having a wrong tag, ' \
                    'response content is: {1}'.format(request.status_code, request.content)
        raise
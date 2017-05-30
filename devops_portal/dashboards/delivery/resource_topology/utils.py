import socket

from devops_portal.api.salt import salt_client


def _is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False
    return True


def _is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:
        return False
    return True


def guess_minion_id(host, domain):
    '''
    Guess minion ID from given host and domain arguments. Host argument can contain
    hostname, FQDN, IPv4 or IPv6 addresses.
 
    Example:
        >>> print guess_minion_id('172.16.1.176', 'my_domain.local')
        >>> web01.my_domain.local
        ---
        >>> print guess_minion_id('fe80::a00:27ff:febf:f55', 'my_domain.local')
        >>> web01.my_domain.local
        ---
        >>> print guess_minion_id('web01', 'my_domain.local')
        >>> web01.my_domain.local
        ---
        >>> print guess_minion_id('web01.my_domain.local', 'my_domain.local')
        >>> web01.my_domain.local
        ---
    '''
    if _is_valid_ipv4_address(host):
        tgt = 'ipv4:%s' % host
    elif _is_valid_ipv6_address(host):
        tgt = 'ipv6:%s' % host
    elif host.endswith(domain):
        tgt = 'fqdn:%s' % host
    else:
        tgt = 'fqdn:%s.%s' % (host, domain)

    wrapped_res = salt_client.low([{'client': 'local', 'tgt': tgt, 'expr_form': 'grain', 'fun': 'grains.item', 'arg': 'id'}])
    res = wrapped_res.get('return', [{'': ''}])[0].values()[0]

    return res.get('id', '')


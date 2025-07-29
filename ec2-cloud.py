#!/usr/bin/env python

import subprocess
import configparser
import sys
from os import path
from cloudflare import Cloudflare

config = configparser.ConfigParser()
configfile = path.expanduser("~/.cloudflare/my-script.ini")
config.read(configfile)

# config example
# [domain.com]
# zone_name = domain.com
# zone_id = (cloudflare zone id) (optional)
# subdomains = foo bar
# ipv6 = False
# token = (Cloudflare api token)
# prox-domains = @ bar ( any subdomains you want proxied )


def getdns():
    dname = subprocess.run(
        [
            "aws",
            "ec2",
            "describe-instances",
            "--query",
            "Reservations[0].Instances[0].PublicDnsName",
            "--output",
            "text",
        ],
        capture_output=True,
        universal_newlines=True,
    )
    return dname.stdout.strip('"\n')


def main():
    dname = getdns()
    if dname is None or dname == "":
      sys.exit("No instance found!")
    for section in config.sections():
        myconfig = config[section]
        zone_name = myconfig["zone_name"]
        try:
            ttl = int(myconfig["ttl"])
        except KeyError:
            ttl = 1  # Fallback to auto
        cf = Cloudflare(api_token=myconfig["token"])

        try:
            zone_id = myconfig["zone_id"]
        except KeyError:
            print("zone_id not specified, querying the api")
            #            params = {"name": zone_name}
            search = cf.zones.list(name=zone_name)
            zone_id = search.result[0].id
        dns_records = [
            {
                "name": "keep." + zone_name,
                "type": "CNAME",
                "content": dname,
                "ttl": ttl,
            },
        ]
        #        if "@" in myconfig["prox-domains"]:
        #            dns_records[0]["proxied"] = True
        #        else:
        dns_records[0]["proxied"] = False

        def getrecord(name, ipv):
            record = cf.dns.records.list(zone_id=zone_id, name=name, type=ipv)
            return record

        def getrecordid(name, ipv):
            record = getrecord(name, ipv)
            record = record.result[0]
            return record.id

        print("zone id: " + zone_id)

        for mrecord in dns_records:
            # print(ip4)
            print("record: ", end="")
            print(mrecord)
            record_id = getrecordid(mrecord["name"], mrecord["type"])
            print("record id: " + record_id)
            r = cf.dns.records.update(
                zone_id=zone_id,
                dns_record_id=record_id,
                name=mrecord["name"],
                type=mrecord["type"],
                content=mrecord["content"],
                ttl=mrecord["ttl"],
            )
            print(r)
    exit(0)


if __name__ == "__main__":
    main()

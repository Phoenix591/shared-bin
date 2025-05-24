#!/usr/bin/env python

import subprocess
import configparser
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


def getip(type):
    ip = subprocess.run(
        ["dig", type, "+short", "TXT", "o-o.myaddr.l.google.com", "@ns1.google.com"],
        capture_output=True,
        universal_newlines=True,
    )
    return ip.stdout.strip('"\n')


def main():
    ip4 = getip("-4")
    for section in config.sections():
        myconfig = config[section]
        zone_name = myconfig["zone_name"]
        cf = Cloudflare(api_token=myconfig["token"])
        try:
            ttl = int(myconfig["ttl"])
        except KeyError:
            ttl = 1  # Fallback to auto
        try:
            zone_id = myconfig["zone_id"]
        except KeyError:
            print("zone_id not specified, querying the api")
            search = cf.zones.list(name=zone_name)
            zone_id = search.result[0].id
        doip6 = myconfig.getboolean("ipv6")

        dns_records = [
            {"name": zone_name, "type": "A", "content": ip4},
        ]
        if "@" in myconfig["prox-domains"]:
            dns_records[0]["proxied"] = True
        else:
            dns_records[0]["proxied"] = False

        if doip6 is True:
            ip6 = getip("-6")
            v6_records = [
                {
                    "name": zone_name,
                    "type": "AAAA",
                    "content": ip6,
                    "proxied": dns_records[0]["proxied"],
                }
            ]
            dns_records.extend(v6_records)
        subdomains = myconfig["subdomains"].split()
        for subdomain in subdomains:
            subd_record = [
                {
                    "name": subdomain + "." + zone_name,
                    "type": "A",
                    "content": ip4,
                }
            ]
            if subdomain in myconfig["prox-domains"]:
                subd_record[0]["proxied"] = True
            else:
                subd_record[0]["proxied"] = False
            print(subd_record)
            if doip6 is True:
                subd_record.append(
                    {
                        "name": subdomain + "." + zone_name,
                        "type": "AAAA",
                        "content": ip6,
                        "proxied": subd_record[0]["proxied"],
                    }
                )
            dns_records.extend(subd_record)

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
                proxied=mrecord["proxied"],
                content=mrecord["content"],
                ttl=ttl,
            )
            print(r)
    exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python

import CloudFlare
import subprocess
import configparser
from os import path


config = configparser.ConfigParser()
configfile = path.expanduser("~/.cloudflare/my-script.ini")
config.read(configfile)

# config example
# [domain.com]
# zone_name = domain.com
# zone_id = (cloudflare zone id)
# subdomains = foo bar
# ipv6 = false


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
        cf = CloudFlare.CloudFlare(profile=zone_name)

        try:
            zone_id = myconfig["zone_id"]
        except KeyError:
            print("zone_id not specified, querying the api")
            params = {"name": zone_name}
            zone = cf.zones.get(params=params)
            zone_id = zone[0]["id"]
        doip6 = myconfig.getboolean("ipv6")

        dns_records = [
            {"name": zone_name, "type": "A", "content": ip4},
        ]

        if doip6 is True:
            ip6 = getip("-6")
            v6_records = [{"name": zone_name, "type": "AAAA", "content": ip6}]
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
            if doip6 is True:
                subd_record = subd_record + [
                    {
                        "name": subdomain + "." + zone_name,
                        "type": "AAAA",
                        "content": ip6,
                    }
                ]
            dns_records.extend(subd_record)

        def getrecord(name, ipv):
            record = cf.zones.dns_records.get(
                zone_id, params={"name": name, "type": ipv}
            )
            return record

        def getrecordid(name, ipv):
            record = getrecord(name, ipv)
            record = record[0]
            return record["id"]

        print("zone id: " + zone_id)

        for dns_record in dns_records:
            # print(ip4)
            print("record: ", end="")
            print(dns_record)
            record_id = getrecordid(dns_record["name"], dns_record["type"])
            print("record id: " + record_id)
            r = cf.zones.dns_records.put(zone_id, record_id, data=dns_record)
            print(r)
    exit(0)


if __name__ == "__main__":
    main()

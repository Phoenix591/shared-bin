#!/usr/bin/env python3
import sys
import CloudFlare
import  subprocess
import configparser
import os
import code
config = configparser.ConfigParser()
configfile = os.path.expanduser('~/.cloudflare/my-script.ini')
config.read(configfile)
for section in config.sections():
	myconfig = config[section]
	zone_name = myconfig['zone_name']
	print('shell for '+myconfig['zone_name'])
	cf = CloudFlare.CloudFlare(profile=myconfig['zone_name'])
	code.interact(local=locals())

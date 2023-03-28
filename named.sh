#!/bin/sh
mount --bind /run/credentials/named.service /chroot/dns/run/credentials/named.service
exec /usr/sbin/named -4 -f -u named -t /chroot/dns

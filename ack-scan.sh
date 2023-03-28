#!/bin/bash
shopt -s extglob # enable special !(pattern-list) syntax
set -e # exit if any fail
DIR="~/acknowledged_scanners"
cd ${DIR}
git pull
nft flush set inet main ack-scanner4
for ip4 in $(grep -rhv : $DIR/data/*/ips.txt | iprange -J -); do
	nft add element inet main ack-scanner4 {${ip4}}
done
nft flush set inet main ack-scanner6
for ip6 in $(grep -rh : $DIR/data/*/ips.txt | grep -v ' '); do
	nft add element inet main ack-scanner6 {${ip6}}
done

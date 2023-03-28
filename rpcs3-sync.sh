#!/bin/bash
unset DISPLAY
PIDIR="/mnt/pi/ps3-games/rpcs3"
WINDIR="/mnt/c/Users/Kyle/rpcs3"
sudo /usr/local/bin/mount-network.sh || exit -2
unison -auto -batch "${PIDIR}/dev_hdd0" "${WINDIR}/dev_hdd0"
unison -auto -batch "${PIDIR}/custom_configs" "${WINDIR}/custom_configs"

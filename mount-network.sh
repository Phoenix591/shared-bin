#!/bin/bash
for x in /var/db/repos /usr/portage /var/cache/distfiles /mnt/pi; do
	mount $x
done

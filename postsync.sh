#!/bin/bash
emerge -pvuDU world >/tmp/post-sync
if ! grep -q "0 packages" /tmp/post-sync; then
	(cat /srv/general/portage.txt; cat /tmp/post-sync) |sendmail $1
fi

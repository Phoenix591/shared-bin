#!/bin/bash
emerge -pvuDU world 2>&1 | tee /tmp/post-sync
cat /usr/portage/metadata/timestamp.chk >>/tmp/post-sync
if ! grep -q "0 packages" /tmp/post-sync; then
	(cat /srv/general/portage.txt; cat /tmp/post-sync) |sendmail $1 && \
	echo "Mail sent"
fi

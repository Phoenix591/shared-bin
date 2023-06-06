#!/bin/bash
if [ -z "${CHOST}" ]; then
	export $(awk '/^CHOST/ && gsub("\"","")' /etc/portage/make.conf)
fi
if [ -z "${CHOST}" ]; then
	echo "Failed to get CHOST!"
	exit -1
fi

#!/bin/bash
if [ -z "${CHOST}" ]; then
	export CHOST="$(portageq  envvar CHOST)"
fi
if [ -z "${CHOST}" ]; then
	echo "Failed to get CHOST!"
	exit -1
fi

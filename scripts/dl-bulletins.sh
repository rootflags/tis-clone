#!/bin/sh
#
# Download a vehicle's service bulletins, tech tips and service campaigns (see dl-ref.sh)
#

exec `dirname $0`/dl-ref.sh --bulletins "$@"

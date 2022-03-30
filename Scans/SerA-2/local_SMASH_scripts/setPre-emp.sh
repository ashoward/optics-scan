#!/bin/bash

source /root/smash/setup.sh
/root/smash/core/bin/smash.exe -c '/root/smash/serenity/etc/serenity/base/a1.0/*' "N:3:Rx Pre-emphasis 0-11 ${1}dB"

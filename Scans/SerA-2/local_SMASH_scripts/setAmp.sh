#!/bin/bash

source /root/smash/setup.sh
/root/smash/core/bin/smash.exe -c '/root/smash/serenity/etc/serenity/base/a1.0/*' "N:3:Rx Amplitude 0-11 $1"

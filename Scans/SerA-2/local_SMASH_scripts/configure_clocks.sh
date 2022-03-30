#!/bin/bash

source /root/smash/setup.sh
sleep 1
/root/smash/core/bin/smash.exe -c '/root/smash/serenity/etc/serenity/base/a1.0/*' "U:1001 Configure /root/optical_eval/Si5397-RevA_320MHz-Registers_B14.txt"
sleep 5
/root/smash/core/bin/smash.exe -c '/root/smash/serenity/etc/serenity/base/a1.0/*' "U:1002 Configure /root/optical_eval/Si5397-RevA_320MHz-Registers_B14.txt"

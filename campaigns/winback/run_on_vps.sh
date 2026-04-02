#!/bin/bash
nohup python3 campaigns/winback/send_winback.py > /root/winback.log 2>&1 &
echo "Campaign started. PID: $!"
tail -f /root/winback.log

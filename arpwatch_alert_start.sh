#!/bin/bash
IFACE="$1"
USER="$2"
FIFO="$3"

/usr/bin/arpwatch -f /var/lib/arpwatch/${IFACE}.dat -i ${IFACE} -d > $FIFO &
sudo -u $USER ./arpwatch_alert.py -c notify-send -a '-t 86400 -a arpwatch -u critical "<title>" "<descr>"' -s'-a arpwatch -u low "<title>" "<descr>"' -e'-a arpwatch -u critical "<title>" "<descr>"' $FIFO

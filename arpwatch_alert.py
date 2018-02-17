#!/usr/bin/env python3
import sys
import os
import fileinput
import argparse
import logging
import subprocess
import signal

args = None

def notify_event(title, description="", cmd=None, args=None):
  logging.info("EMIT %s: %s" % (title, description))

  if cmd:
    args = args or ""
    args = args.replace("<title>", title).replace("<descr>", description)
    full_cmd = "%s %s" % (cmd, args)
    logging.debug("CMD %s" % full_cmd)
    subprocess.call(full_cmd, shell=True)

def notify_prog_start():
  if args.cmd and args.s_args:
    notify_event("Arpwatch Started", "Arpwatch is running", cmd=args.cmd, args=args.s_args)

def notify_prog_end(exc_info=None):
  if args.cmd and args.e_args:
    notify_event("Arpwatch Terminated", str(exc_info[0].__name__) if exc_info else "Arpwatch has stopped", cmd=args.cmd, args=args.e_args)

def handle_metadata(metadata):
  events_of_interest = [
    "changed ethernet address",
    "flip flop"
  ]

  for event in events_of_interest:
    if event in metadata["Subject"]:
      title = metadata["Subject"].title()
      description = "ARP spoofing detected for %s!\nMAC before: %s (%s)\nMAC after: %s (%s)" % (metadata["ip address"],
                metadata["ethernet address"], metadata["ethernet vendor"],
                metadata["old ethernet address"], metadata["old ethernet vendor"])
      notify_event(title, description, cmd=args.cmd, args=args.a_args)
      break

def parse_arpwatch_output_loop():
  metadata = None
  read_event = False
  skip_newline = True

  for line in fileinput.input(files=args.arpwatch_file):
    line = line.strip()

    if not line:
      if skip_newline:
        skip_newline = False
      else:
        read_event = False
    elif line.startswith("From:"):
      metadata = {}
      read_event = True
      skip_newline = True
    elif read_event:
      if ":" in line:
        k, v = line.split(":", maxsplit=1)
        k = k.strip()
        v = v.strip()
        metadata[k] = v
        logging.debug("%s --> %s" % (k, v))

        if k == "delta":
          # End of message
          read_event = False
          handle_metadata(metadata)

def sig_handler(signum, frame):
  notify_prog_end()
  os._exit(0)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    prog="arpwatch_alert",
    description="Generate arpwatch alerts by parsing arpwatch output",
    formatter_class=argparse.RawTextHelpFormatter,
    epilog='''The following substitutions will be performed in the alert-args parameter:
 <title>: the alert title
 <descr>: the alert description

example:
 sudo /usr/bin/arpwatch -f /var/lib/arpwatch/wlan0.dat -i wlan0 -d | ./arpwatch_alert.py -c notify-send -a '-u critical "<title>" "<descr>"' - ''')

  parser.add_argument("--command", "-c", dest = "cmd",
    help="Command to execute to generate the alert", type=str)
  parser.add_argument("--alert-args", "-a", dest = "a_args",
    help="Arguments to be passed to the alerts generation command.", type=str)
  parser.add_argument("--start-args", "-s", dest="s_args",
    help="Arguments for start up notification (useful to verify that the service\nactually works)", type=str)
  parser.add_argument("--end-args", "-e", dest="e_args",
    help="Arguments for termination notification (to detect unexpected program end)", type=str)
  parser.add_argument("--verbose", "-v", dest="verbose",
    help="Enable verbose logging", action='store_true')
  parser.add_argument("arpwatch_file",
    help="Arpwatch output file to read. Use - to read from stdin.")

  args = parser.parse_args()
  signal.signal(signal.SIGTERM, sig_handler)
  signal.signal(signal.SIGHUP, sig_handler)
  notify_prog_start()

  logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG if args.verbose else logging.INFO)

  try:
    logging.info("Starting arpwatch interpreter loop")
    parse_arpwatch_output_loop()
  except:
    exc_info = sys.exc_info()
    notify_prog_end(exc_info)
    raise

  notify_prog_end()

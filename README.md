# Arpwatch Alert

Generate (desktop) arpwatch alerts by parsing arpwatch output.

A generic script can be run with custom parameters after arpwatch reports issues
in ethernet/ip address pairings.

The arpwatch system tool should be installed in order to run this.

## Command line arguments
```
usage: arpwatch_alert [-h] [--command CMD] [--alert-args A_ARGS]
                      [--start-args S_ARGS] [--end-args E_ARGS] [--verbose]
                      arpwatch_file

Generate arpwatch alerts by parsing arpwatch output

positional arguments:
  arpwatch_file         Arpwatch output file to read. Use - to read from stdin.

optional arguments:
  -h, --help            show this help message and exit
  --command CMD, -c CMD
                        Command to execute to generate the alert
  --alert-args A_ARGS, -a A_ARGS
                        Arguments to be passed to the alerts generation command.
  --start-args S_ARGS, -s S_ARGS
                        Arguments for start up notification (useful to verify that the service
                        actually works)
  --end-args E_ARGS, -e E_ARGS
                        Arguments for termination notification (to detect unexpected program end)
  --verbose, -v         Enable verbose logging

The following substitutions will be performed in the alert-args parameter:
 <title>: the alert title
 <descr>: the alert description
```

Example usage to send a desktop notifications:

```
sudo /usr/bin/arpwatch -f /var/lib/arpwatch/wlan0.dat -i wlan0 -d | ./arpwatch_alert.py -c notify-send -a '-u critical "<title>" "<descr>"' - ''') -
```

## Running as a service at boot
The provided `arpwatch_alert@.service` systemd service can be used to run the service
at boot. It will generate desktop notifications when issues are detected. During every boot a notification is executed to ensure the service has started successfully.

It should be customized in the following points:

- user `emanuele` should be replaced with the actual user name running xorg
- the `WorkingDirectory` should be changed to point to the actual arpwatch_alert dir

After performing the modifications above, the service should be copied to the systemd
directory and enabled:

```
sudo cp arpwatch_alert@.service /usr/lib/systemd/system
sudo systemctl enable arpwatch_alert@wlan0
sudo systemctl start arpwatch_alert@wlan0
```

This assumes `wlan0` is the system interface to monitor with arpwatch.

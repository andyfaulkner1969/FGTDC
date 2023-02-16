# FGTDC - FortiGate Diagnostics Collector
This script is desgined to run on a cron job from a mac/linux and it will run any commands you define to 
collect diagsostic information on a FortiGate Firewall.

There are three files needed.

fgtdc.py - Primary python script.  Wrote for python 3.0 and NOT tested in Windows.
fgtdc_config.yml - configuraiton file for the script itself.  Must be in the same directory
fgtdc_commands.txt - list of commands you wish to run (extensive list is already provided modify as needed.)

When the script runs it will do the following...

1. Check to see if log directory exsists. If not creates it.
2. Check to see if log file is present. If not create it.
3. Check to see if log directory is larger than size defined in yaml if so will exit.  If not moves forward.  
    *This is a safe guard to prevent the script from over runnning the file system.
4. Check to see if the log file is larger than your file limit size defined in yaml.  If yes it will move the current file to a new date stamped file.
5. Log into the FGT and modify the consle settings to turn off the MORE function.
6. Run through the list of commands defined in the fgtdc_commands.txt file.
7. Log all to the log file.

***** BE VERY cautious of what commands you put in the file ***** Because it will blindly execute them.

I highly suggest you only use "get" and "diag" commands.

I used the following cron to run...

This will run every minute, you can of course change that interval.

> * * * * * cd /home/username/fgtdc && /home/username/fgtdc.py

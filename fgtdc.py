#!/usr/bin/env python3

import paramiko
import time
import os
import shutil
from datetime import datetime
import yaml
import logging
from pathlib import Path
import pathlib

# Fortigate information collection tool.
#  This script will run the commands you list in fgtdc_commands.txt (should be in the same directory)
#  This list can ge changed as needed.
#  Configuration is done in the fgtdc_config.yml file for your specfic Fortigate.
#  It will log into the FGT via SSH and run each command logging to file.
#  If logs directory is missing it will be created
""""
 ________         ____     _ __  ___           __              __
/_  __/ /  ___   / __/  __(_) / / _ )___ ____ / /____ ________/ /
 / / / _ \/ -_) / _/| |/ / / / / _  / _ `(_-</ __/ _ `/ __/ _  /
/_/ /_//_/\__/ /___/|___/_/_/ /____/\_,_/___/\__/\_,_/_/  \_,_/
afaulkner@fortinet.com 
"""

now = datetime.now()
current_time = now.strftime("Date-%m-%d-%Y-Time-%H%M%S")

# Opening config file
with open('fgtdc_config.yml', 'r') as file:
	config = yaml.safe_load(file)

# Opening command list file
cmd_file = open('fgtdc_commands.txt', 'r')

# Setting up file usage (added for windows support)
log_dir = Path(config['script_file_cfg']['log_path'])
log_file = Path(log_dir,config['script_file_cfg']['log_file'])
debug_path = Path(config['debug_config']['debug_path'])
debug_file = Path(debug_path,config['debug_config']['debug_file'] )

# Looking for log directory if not there create
if os.path.isdir(log_dir):
    pass
else:
	logging.info("Missing logs directory...creating it now.")
	os.makedirs(log_dir)

# Setting up debug
def debug_setup():
	logging_flag = config['debug_config']['debug_log_flag']
	if config['debug_config']['debug_flag'] == "DEBUG":
		debug_flag = logging.DEBUG
	if config['debug_config']['debug_flag'] == "INFO":
		debug_flag = logging.INFO
	if config['debug_config']['debug_flag'] == "NOTSET":
		debug_flag = logging.NOTSET
	if logging_flag == "N":
		logging.basicConfig(level=debug_flag,format='%(asctime)s:%(levelname)s:%(message)s')
	if logging_flag == "Y":
		logging.basicConfig(filename=debug_file,level=debug_flag,format='%(asctime)s:%(levelname)s:%(message)s')
	logging.info("***** Start of FGTDC Script. *****")

# Checking to see if log file exsist, if not creating.
def check_file():
	logging.info("Start of check_file function.")
	if os.path.isfile(log_file):
		pass
	else:
		fout = open(log_file,'wb')
		logging.info("1st time run creating log file.")
		fout.close()

# Checking directory size, this is a safe guard to prevent the script from filling
# the file system.
def dir_size_limit():
	logging.info("Start of dir_size_limit function")
	for root, dirs, files in os.walk(log_dir):
		dir_size = 0
		for fn in files:
			path = os.path.join(root, fn)
			size = os.stat(path).st_size # in bytes
			logging.debug("directory size = " + str(size))
			dir_size = dir_size + size
	if dir_size > int(config['script_file_cfg']['dir_limit']):
		logging.info("Directory Limit Reached!  Clean out directory and start again.")
		exit()
	else:
		logging.info("Directory size good... moving to next step")
			
# Checking to see if log file has got too large, if yes move it with date stamp.
		# File limit set in yaml file.
def log_file_rotation():
	logging.info("Start of log_file_rotation function")
	file_size = os.path.getsize(log_file)
	logging.info("Log file Size is :" + str(file_size) + "bytes")
	if file_size > int(config['script_file_cfg']['file_limit']): 
		logging.info("File size exceeds limit....moving..")
		old_path =os.getcwd()
		os.chdir(log_dir)
		new_name = current_time + ".log" 
		os.rename(config['script_file_cfg']['log_file'],new_name)
		fout = open(config['script_file_cfg']['log_file'],'wb')
		logging.info("Creating new primary log file.")
		fout.close()
		os.chdir(old_path)
	else:
		pass

# Turning off MORE for the console otherwise script hangs.
def console_set():
	logging.info("Start of console_set function")
	host = config['fgtconfig']['fgt_ip']
	port = config['fgtconfig']['fgt_port']
	username = config['fgtconfig']['fgt_admin']
	password = config['fgtconfig']['fgt_password']
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, port, username, password)
	cmd = "config system console" "\n" "set output standard" "\n" "end" "\n"
	stdin, stdout, stderr = ssh.exec_command(cmd)
	output = stdout.read().decode('utf-8').strip("\n")
	logging.debug(output)
	ssh.close()

# Running commands against FGT taken from commands file.
def run_command():
	logging.info("Start of run_command function")
	# Opening log file
	fout = open(log_file,'a')
	host = config['fgtconfig']['fgt_ip']
	port = config['fgtconfig']['fgt_port']
	username = config['fgtconfig']['fgt_admin']
	password = config['fgtconfig']['fgt_password']
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, port, username, password)	
	fout.write(current_time)
	fout.write('\n\r')
	fout.write("***** Start of commands *****")
	fout.write('\n\r')
	
	for cmd in cmd_file:
		if cmd.startswith('#'):
			pass
		else:
			stdin, stdout, stderr = ssh.exec_command(cmd)
			fout.write('\n\r')
			fout.write("Running: " + cmd)
			fout.write('\n\r')
			output = stdout.read().decode('utf-8').strip("\n")
			logging.debug(output)
			time.sleep(.5)
			fout.write('\n\r')
			fout.write(output)
			time.sleep(.5)
	fout.write('\n\r')
	fout.write("***** End of commands *****")
	fout.write('\n\r')
	fout.close()
	cmd_file.close()
	ssh.close()

debug_setup()
dir_size_limit()
check_file()
log_file_rotation()
console_set()
run_command()
logging.info("***** END of FGTDC Script. *****")
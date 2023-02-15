#!/usr/bin/env python3

import paramiko
import time
import sys
import time
import os
import shutil
from datetime import datetime
import yaml

# Fortigate information collection tool.
#  This script will run the commands you list in fgt_commands.txt (should be in the same directory)
#  This list can ge changed as needed.
#  Configuration is done in the fgt_stat_check_config.yml file for your specfic Fortigate.
#  It will log into the FGT via SSH and run each command logging to file.
#  Create a sub dir call "logs"
#  Created by Andy Faulkner afaulkner@fortinet.com a.k.a The Evil Bastard


now = datetime.now()
current_time = now.strftime("Date-%m-%d-%Y---Time-%H%M%S")

# Opening config file

with open('fgt_stat_check_config.yml', 'r') as file:
	config = yaml.safe_load(file)

# Opening command list file
cmd_file = open('fgt_commands.txt', 'r')

# Opening log file
fout = open(config['script_file_cfg']['log_path'] + config['script_file_cfg']['log_file'],'a')

# Checking to see if log file exsist, if not creating.
def check_file():
	if os.path.isfile(config['script_file_cfg']['log_path'] + config['script_file_cfg']['log_file']):
		pass
	else:
		fout = open(config['script_file_cfg']['log_path'] + config['script_file_cfg']['log_file'],'wb')
		fout.close()

# in progress directory limit check
def dir_size_limit():
	for root, dirs, files in os.walk("/Users/andyfaulkner/Downloads/"):
		dir_size = 0
		for fn in files:
			path = os.path.join(root, fn)
			size = os.stat(path).st_size # in bytes
			#print(size)
			dir_size = dir_size + size
			
	print(dir_size)

# Checking to see if log file has got too large, if yes move it with date stamp.
		# File limit set in yaml file.
def log_file_rotation():
	file_size = os.path.getsize(config['script_file_cfg']['log_path'] + config['script_file_cfg']['log_file'])
	
	print("Log file Size is :", file_size, "bytes")
	if file_size > int(config['script_file_cfg']['file_limit']): 
		print("File size exceeds limit....moving..")
		new_log = open(config['script_file_cfg']['log_path'] + current_time + "_log.txt",'wb')
		new_log.close()
		shutil.move(config['script_file_cfg']['log_path'] + config['script_file_cfg']['log_file'], config['script_file_cfg']['log_path'] + current_time + "_log.txt")
	else:
		pass

# Turning off MORE for the console otherwise script hangs.
def console_set():
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
#	print(output)
	ssh.close()

# Running commands against FGT taken from commands file.
def run_command():

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
			#print(output)
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

log_file_rotation()
check_file()
console_set()
run_command()
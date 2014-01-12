#!/usr/bin/env python
	
# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python testdaemon.py start

#standard python libs
import logging
import time, os

#third party libs
from daemon import runner


#local libs
import digit

class App():
	
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path =  '/var/run/digit/digit.pid'
		if not os.path.exists('/var/run/digit'):
			os.makedirs('/var/run/digit')
		self.pidfile_timeout = 5
		
		
	def run(self):
		while True:
			logger.info("------------------------------------")
			#Main code goes here ...
			digit.do_main_program()


app = App()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s: %(message)s")
handler = logging.FileHandler('digit.log')
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()
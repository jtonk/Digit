#!/usr/bin/env python
import time, atexit
import logging
logger = logging.getLogger(__name__)
from apscheduler.scheduler import Scheduler
import config
import inetServer
import scheduleData
from threading import Thread
import contextlib
import daemon
from BaseHTTPServer import (HTTPServer, BaseHTTPRequestHandler)


def do_main_program():
	
	do_scheduler()

	# read config and init sensors
	
	global sensors
	sensors = config.readConfig()
	
	logger.debug(sensors.keys())

	
	
	
	threadHTTP = Thread(target=inetServer.threadHTTP)
	threadHTTP.setDaemon(True)
	threadHTTP.start()

	
	while 1:
		try:
			time.sleep(0.1)
		except KeyboardInterrupt:
			print >> sys.stderr, '\nExiting by user request.\n'
			sys.exit(0)



def do_scheduler():
	config.sched = Scheduler(daemon=True)
	atexit.register(lambda: sched.shutdown(wait=False))
	config.sched.start()
	

if __name__ == '__main__':
    do_main_program()
    
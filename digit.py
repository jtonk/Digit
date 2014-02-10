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
	# read config and init sensors
	
	global distrib,sensors
	
	distrib,sensors = config.readConfig()
	
	logger.debug(distrib.keys())
	logger.debug(sensors.keys())

	
	do_scheduler()
	
#	threadHTTP = Thread(target=inetServer.threadHTTP)
#	threadHTTP.setDaemon(True)
#	threadHTTP.start()

	while 1:
		try:
			time.sleep(0.1)
		except KeyboardInterrupt:
			print >> sys.stderr, '\nExiting by user request.\n'
			sys.exit(0)



def do_scheduler():
	sched = Scheduler(daemon=True)
	atexit.register(lambda: sched.shutdown(wait=False))
	sched.start()
	
	#to disable immediate measuring comment the next line
	scheduleData.sched_measure()
	sched.add_cron_job(scheduleData.sched_measure, minute="*/10")




if __name__ == '__main__':
    do_main_program()
    
#!/usr/bin/env python
import time, os
import logging
logger = logging.getLogger(__name__)
import config

def sched_measure():
	logger.info("fetching sensors")
	for keys,value in sorted(config.sensors.items()):
			value.measure()
			value.updateRRD()
			for function in value.sensorFunctions:
				if getattr(value, function + "_setPoint") == True:
					value.check(function)
	logger.info("-----------finished sched_measure()-----------")

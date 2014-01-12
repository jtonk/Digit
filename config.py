#!/usr/bin/env python
import os, time
import ConfigParser
import logging
logger = logging.getLogger(__name__)

#local libs
from sensorData import sensorData
from onlineData import onlineData
from distributorData import distributorData

#main code
dataPrefix = ""
sensors = {}
online = {}
distrib = {}

def readConfig(configFile):
	now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
	logger.info('reading configuration from {0}'.format(configFile, now))
	config = ConfigParser.RawConfigParser()
	config.read(configFile)
	
	sections = config.sections()
	
	global dataPrefix
	dataPrefix = config.get('setup',"dataPrefix")
	
	#read shift pins
	ssSER_PIN = config.getint('setup',"SER_PIN")
	RCLK_PIN = config.getint('setup',"RCLK_PIN")
	SRCLK_PIN = config.getint('setup',"SRCLK_PIN")
	#shiftpi.pinsSetup(ser = SER_PIN, rclk = RCLK_PIN, srclk = SRCLK_PIN)

	global sensors
	global online
	global distrib
	
	for section in sorted(config.sections()):
		if section.find('sensor') != -1:
			sensors[section] = sensorData(config.get(section,"name"),
				config.get(section,"sensorID"), 
				config.get(section,"sensorType"), 
				config.get(section,"dist"), 
				config.get(section,"valves").split(','), 
				config.get(section,"temp_set"), 
				config.get(section,"hum_set"),
				config.get(section,"delta"),
				config.get(section,"color"))
		if section.find('online') != -1:
			online[section] = onlineData(config.get(section,"service"), 
				config.get(section,"location"))
		if section.find('dist') != -1:
			distrib[section] = distributorData(config.get(section,"name"), config.get(section,"nr"))
	return distrib,sensors,online
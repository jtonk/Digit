#!/usr/bin/env python
import os, time
import ConfigParser
import logging
logger = logging.getLogger(__name__)
import shiftpi

#local libs
from sensorData import sensorData
from onlineData import onlineData
from distributorData import distributorData

#main code
dataPrefix = ""
sensors = {}
online = {}
distrib = {}
configFile = '/home/jasper/Digit/settings.ini'

def readConfig():
	now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
	logger.info('reading configuration from {0}'.format(configFile, now))
	config = ConfigParser.RawConfigParser()
	config.read(configFile)
	
	sections = config.sections()
	
	global dataPrefix
	dataPrefix = config.get('setup',"dataPrefix")
	
	global relayTest 
	relayTest = config.getboolean('setup',"relayTest")
	
	#read shift pins
	SER_PIN = config.getint('setup',"SER_PIN")
	RCLK_PIN = config.getint('setup',"RCLK_PIN")
	SRCLK_PIN = config.getint('setup',"SRCLK_PIN")
	shiftpi.pinsSetup(ser = SER_PIN, rclk = RCLK_PIN, srclk = SRCLK_PIN)

	global sensors
	global distrib
	
	for section in sorted(config.sections()):
		if section.find('sensor') != -1:

			functions = config.get(section,"sensorFunctions").split(',')

			setPoint = False

			settings = [section,
				config.get(section,"name"),
				config.get(section,"sensorID"), 
				config.get(section,"sensorType"),
				config.get(section,"sensorFunctions").split(','),
				config.get(section,"color")]
			try:
				config.get(section,'relays')
				settings.append({'relays':config.get(section,"relays").split(',')})
				settings.append({'setPoints':True})
				setPoint = True
			except:
				settings.append({'setPoints':False})

			if "temperature" in functions and setPoint:
				settings.append({'temp_set':config.get(section,"temp_set")})
			if "humidity" in functions and setPoint:
				settings.append({'hum_set':config.get(section,"hum_set")})

			sensors[section] = sensorData(*settings)
		if section.find('dist') != -1:
			distrib[section] = distributorData(config.get(section,"name"), config.get(section,"nr"))
	return distrib,sensors
	
def writeConfig(section, key, value):
	config = ConfigParser.RawConfigParser()
	config.read(configFile)
	config.set(section, key, value)
	with open(configFile, 'wb') as configfile:
		config.write(configfile)
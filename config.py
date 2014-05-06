#!/usr/bin/env python
import os, time
import ConfigParser
import logging
logger = logging.getLogger(__name__)
import shiftpi

#local libs
from sensorData import sensorData

#main code
dataPrefix = ""
sensors = {}
configFile = '/home/jasper/Digit/settings.ini'
sched = {}

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
	
	global temp_unit
	temp_unit = config.get('setup',"temp_unit")
	
	global hum_unit
	hum_unit = config.get('setup',"hum_unit")
	
	#read shift pins
	SER_PIN = config.getint('setup',"SER_PIN")
	RCLK_PIN = config.getint('setup',"RCLK_PIN")
	SRCLK_PIN = config.getint('setup',"SRCLK_PIN")
	shiftpi.pinsSetup(ser = SER_PIN, rclk = RCLK_PIN, srclk = SRCLK_PIN)

	global sensors
	
	for section in sorted(config.sections()):
		if section.find('sensor') != -1:

			functions = config.get(section,"sensorFunctions").split(',')

			setPoint = False

			settings = [section,
				config.get(section,"name"),
				config.get(section,"sensorID"), 
				config.get(section,"sensorType"),
				config.get(section,"sensorFunctions").split(','),
				config.get(section,"color"),
				config.get(section,"color2"),
				config.get(section,"interval")]
			
			if "temp" in functions:
				settings.append({'temp':0})
				settings.append({'temp_unit':temp_unit})
				try:
					config.get(section,'temp_relays')
					
					settings.append({'temp_relays':config.get(section,"temp_relays").split(',')})
					settings.append({'temp_set':config.get(section,"temp_set")})
					settings.append({'temp_setPoint':True})
				except:
					settings.append({'temp_setPoint':False})
					pass
					
			if "hum" in functions:
				settings.append({'hum':0})
				settings.append({'hum_unit':hum_unit})
				try:
					config.get(section,'hum_relays')
					settings.append({'hum_relays':config.get(section,"hum_relays").split(',')})
					settings.append({'hum_set':config.get(section,"hum_set")})
					settings.append({'hum_setPoint':True})
				except:
					settings.append({'hum_setPoint':False})
					pass

			sensors[section] = sensorData(*settings)

	return sensors
	
def writeConfig(section, key, value):
	config = ConfigParser.RawConfigParser()
	config.read(configFile)
	config.set(section, key, value)
	with open(configFile, 'wb') as configfile:
		config.write(configfile)
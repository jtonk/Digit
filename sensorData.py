import dhtreader
import requests, time, os
from bs4 import BeautifulSoup
import rrdtool
import config
import logging
logger = logging.getLogger(__name__)

class sensorData:
	def __init__(self,name,sensorID,sensorType,dist,valves,temp_set,hum_set,delta,color): 
		self.name = name
		self.sensorID = sensorID
		self.sensorType = sensorType
		self.dist = dist
		self.valves = valves
		self.temp_set = round(float(temp_set),1)
		self.hum_set = hum_set
		self.temperature = "NaN"
		self.humidity = "NaN"
		self.db = config.dataPrefix + "/RRD/" + self.name + ".rrd"
		self.color = color
		self.createRRD()

	def measure(self):
	#read data for DHT compatible
		if self.sensorType in ("DHT11","DHT23","AM2302"):
			count = 0
			sType = 0
			dhtreader.init()
			if self.sensorType == "DHT11":
				sType = 11
			if self.sensorType == "DHT22":
				sType = 22
			if self.sensorType == "AM2302":
				sType == 2302
			
			while(count < 10):
				try:
					t, h = dhtreader.read(int(sType), int(self.sensorID))
				except TypeError:
					logging.info("Failed to read from sensor '"+ self.name +"' on attempt "+ str(count+1))
					count = count + 1
					time.sleep(2)
				else:
					self.temperature = round(float('{0}'.format(t, h)),1)
					self.humidity = round(float('{1}'.format(t, h)),1)
					break		
		#read data for 1-wire
		if self.sensorType == "1-wire":
			count = 0
			while(count < 10):
				try:
					f = open('/sys/bus/w1/devices/' + self.sensorID + '/w1_slave', 'r')
					lines = f.readlines()
					f.close()
					if lines[0].strip()[-3:] != 'YES':
						raise lines
					else:
						equals_pos = lines[1].find('t=')
						if equals_pos != -1:
							temp_string = lines[1][equals_pos+2:]
				except:
					logging.warning("Failed to read from sensor '"+ self.name +"' on attempt "+ str(count+1))
					count = count + 1
					time.sleep(0.2)
				else:
					self.temperature = round(float(temp_string) / 1000.0,1)
					self.humidity = "NaN"
					break

		logging.info("{0}: {1}'C / {2}%".format(self.name, self.temperature, self.humidity))
		

	def updateRRD(self):
		rrdtool.update(self.db, '{0}:{1}:{2}:{3}:{4}'.format(int(time.time()), self.temperature, self.temp_set, self.humidity, self.hum_set))
		logging.info("writing log for '{0}'".format(self.name))

	def setTemp(self, value):
		self.temp_set = round(value,1)
		logging.info("new min temp. '{0}' to {1}'C".format(self.name,self.temp_set))

	def setHum(self, value):
		self.hum_set = value
		logging.info("new min hum. '{0}' to {1}%".format(self.name,self.hum_set))

	def tempCheck(self):
		logging.info("check temp. '{0}' current/min: {2}/{1}'C".format(self.name, self.temp_set, self.temperature))
		if float(self.temp_set) > float(self.temperature):
			self.dist.changeValve(self.valves,True)
			return False;
		else:
			return True;

	def createRRD(self):
		if os.path.isfile(self.db) == False:
			RRD = rrdtool.create(self.db, "--step", "600", "--start", '0',
			"DS:" + self.name + "_t:GAUGE:1800:U:U",
			"DS:" + self.name + "_ts:GAUGE:1800:U:U",
			"DS:" + self.name + "_h:GAUGE:1800:U:U",
			"DS:" + self.name + "_hs:GAUGE:1800:U:U",
			"RRA:AVERAGE:0.5:1:288",
			"RRA:AVERAGE:0.5:3:336",
			"RRA:AVERAGE:0.5:6:672",
			"RRA:AVERAGE:0.5:144:1825")
			logger.info("RRD not found, created '" + self.db +"' for logging")
		else:
			logger.info("using '" + self.db + "' for logging")
			return True

	
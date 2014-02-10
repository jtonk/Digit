import dhtreader
import requests, time, os
from bs4 import BeautifulSoup
import rrdtool
import config
import logging
logger = logging.getLogger(__name__)

class sensorData:
	def __init__(self,section,name,sensorID,sensorType,sensorFunctions,color,*args,**kwargs): 
		self.section = section
		self.name = name
		self.sensorID = sensorID
		self.sensorType = sensorType
		self.sensorFunctions = sensorFunctions
		self.db = config.dataPrefix + "/RRD/" + self.section + ".rrd"
		self.color = color
		for item in args:
			for key, value in item.iteritems():
				setattr(self, key, value)

		self.createRRD()
		logging.info("initialized sensor '"+ self.section +"'")

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
					self.temperature = round(float('{0}'.format(t, h)),1)
					self.humidity = round(float('{1}'.format(t, h)),1)
					
				except TypeError:
					logging.info("Failed to read from sensor '"+ self.section +"' on attempt "+ str(count+1))
					count = count + 1
					time.sleep(2)
					self.temperature = None
					self.humidity = None
				else:
					logging.info("{0}: {1}'C / {2}%".format(self.name, self.temperature, self.humidity))
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
					self.temperature = round(float(temp_string) / 1000.0,1)
					
				except:
					logging.warning("Failed to read from sensor '"+ self.section +"' on attempt "+ str(count+1))
					count = count + 1
					time.sleep(0.2)
					self.temperature = None
				else:
					logging.info("{0}: {1}'C".format(self.name, self.temperature))
					break

		#read data online from KNMI
		if self.sensorType == "KNMI":
			try:
				data = requests.get("http://m.knmi.nl/index.php?i=Actueel&s=tabel_10min_data").text
				soup = BeautifulSoup(data)
				for row in soup.find('table').findAll('tr'):
					cols = row.findAll('td')
					if not cols:
						continue
					if cols[0].get_text() == self.sensorID:
						self.temperature = float(cols[2].get_text().replace('&nbsp;', '').strip())
						self.humidity = float(cols[4].get_text().replace('&nbsp;', '').strip())
				logger.info("{0}: {1}'C / {2}%".format(self.sensorType + "_" + self.sensorID, self.temperature, self.humidity))
			except:
				self.temperature = None
				self.humidity = None

	def updateRRD(self):
		if self.temperature != None or self.humidity != None:
			data = str(int(time.time()))
			if "temperature" in self.sensorFunctions:
				data = data + ":" + str(self.temperature)
				if self.setPoints:
					data = data + ":" + str(self.temp_set)
			if "humidity" in self.sensorFunctions:
				data = data + ":" + str(self.humidity)
				if self.setPoints:
					data = data + ":" + str(self.hum_set)

			rrdUpdateOptions = []
			rrdtool.update(self.db, data)
			logging.info("writing log for '{0}'".format(self.section))
		else:
			logging.info("writing log for '{0}' failed, invalid data".format(self.section))
			return False

	def setValue(self, variable, value):
		### todo set variable instead of only temp
		self.temp_set = round(value,1)
		logging.info("new min temp. '{0}' to {1}'C".format(self.name,self.temp_set))
		config.writeConfig(self.section, 'temp_set', str(self.temp_set))
		self.tempCheck()

	def tempCheck(self):
		logging.info("check temp. '{0}' current/min: {2}/{1}'C".format(self.name, self.temp_set, self.temperature))
		if float(self.temp_set) >= float(self.temperature):
			self.dist.changeValve(self.valves,True)
		else:
			self.dist.changeValve(self.valves,False)

	def createRRD(self):
		rrdCreateOptions = [self.db,"--step",'600',"--start",'0']
		
		if "temperature" in self.sensorFunctions:
			rrdCreateOptions.extend(["DS:temp:GAUGE:1800:U:U"])
			if self.setPoints:
				rrdCreateOptions.extend(["DS:temp_set:GAUGE:1800:U:U"])
		
		if "humidity" in self.sensorFunctions:
			rrdCreateOptions.extend(["DS:hum:GAUGE:1800:U:U"])
			if self.setPoints:
				rrdCreateOptions.extend(["DS:hum_set:GAUGE:1800:U:U"])
		
		rrdCreateOptions.extend(["RRA:AVERAGE:0.5:1:288","RRA:AVERAGE:0.5:3:336","RRA:AVERAGE:0.5:6:672","RRA:AVERAGE:0.5:144:1825"])
		
		if os.path.isfile(self.db) == False:
			RRD = rrdtool.create(*rrdCreateOptions)
			logger.info("RRD not found, created '" + self.db +"' for logging")
		else:
			logger.info("using '" + self.db + "' for logging")
			return True

	
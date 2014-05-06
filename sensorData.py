import dhtreader
import requests, time, os
from bs4 import BeautifulSoup
import rrdtool
import config
import logging
import shiftpi
logger = logging.getLogger(__name__)
import scheduleData

class sensorData:
	def __init__(self,section,name,sensorID,sensorType,sensorFunctions,color,color2,interval,*args,**kwargs): 
		self.section = section
		self.name = name
		self.sensorID = sensorID
		self.sensorType = sensorType
		self.sensorFunctions = sensorFunctions
		self.db = config.dataPrefix + "/RRD/" + self.section + ".rrd"
		self.color = color
		self.color2 = color2
		self.interval = interval
		for item in args:
			for key, value in item.iteritems():
				setattr(self, key, value)
		
		###
		###insert init for relay check here
		###

		self.createRRD()
		
		logging.info("adding " + self.section +" for interval checks'"+ self.section +"'")
		config.sched.add_cron_job(self.schedule, name=self.section, minute="*/"+self.interval, max_instances=1, misfire_grace_time=60)
		
		logging.info("initialized sensor '"+ self.section +"'")

	def measure(self):
	#read data for DHT compatible
		if self.sensorType in ("DHT11","DHT23","AM2302"):
			count = 0
			sType = 0
			dhtreader.init()
			if self.sensorType == "DHT11":
				sType = 11
			elif self.sensorType == "DHT22":
				sType = 22
			elif self.sensorType == "AM2302":
				sType == 2302
			else:
				print("invalid type, only 11, 22 and 2302 are supported for now!")
				return false
			
			while(count < 10):
				try:
					t, h = dhtreader.read(int(sType), int(self.sensorID))
					logger.debug("t,h =  {0},{1} (error in dhtreader.so?)".format(t, h))
					self.temp = round(float('{0}'.format(t, h)),1)
					self.hum = round(float('{1}'.format(t, h)),1)
					
				except TypeError:
					logging.info("Failed to read from sensor '"+ self.section +"' on attempt "+ str(count+1))
					count = count + 1
					time.sleep(3)
					self.temp = None
					self.hum = None
				else:
					logging.info("{0}: {1}'C / {2}%".format(self.name, self.temp, self.hum))
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
					self.temp = round(float(temp_string) / 1000,1)
					
				except:
					logging.warning("Failed to read from sensor '"+ self.section +"' on attempt "+ str(count+1))
					count = count + 1
					time.sleep(0.2)
					self.temp = None
				else:
					logging.info("{0}: {1}'C".format(self.name, self.temp))
					break

		#read data online from KNMI
		if self.sensorType == "KNMI":
			count = 0
			while(count < 10):
				try:
					data = requests.get("http://m.knmi.nl/index.php?i=Actueel&s=tabel_10min_data").text
					soup = BeautifulSoup(data)
					for row in soup.find('table').findAll('tr'):
						cols = row.findAll('td')
						if not cols:
							continue
						if cols[0].get_text() == self.sensorID:
							self.temp = float(cols[2].get_text().replace('&nbsp;', '').strip())
							self.hum = float(cols[3].get_text().replace('&nbsp;', '').strip())
					
				except:
					logger.info("error fetching data from {0} (website offline?)".format(self.sensorType + "_" + self.sensorID))
					count = count + 1
					time.sleep(0.2)
					self.temp = None
					self.hum = None
				else:
					logger.info("{0}: {1}'C / {2}%".format(self.sensorType + "_" + self.sensorID, self.temp, self.hum))
					break

		#read data for internal CPU
		if self.sensorType == "system":
			count = 0
			while(count < 10):
				try:
					
					f = open(self.sensorID, 'r')
					lines = f.read().strip()
					f.close()
					self.temp = round(float(lines) / 1000,1)
				except:
					logging.warning("Failed to read from sensor '"+ self.section +"' on attempt "+ str(count+1))
					count = count + 1
					time.sleep(0.2)
					self.temp = None
				else:
					logging.info("{0}: {1}'C".format(self.name, self.temp))
					break



	def setValue(self, key, value):
		### set new value
		setKey = key + "_set"
		value = round(value,1)

		if hasattr(self, setKey) and isinstance(value, float):
			setattr(self, setKey, value)
			config.writeConfig(self.section, setKey, str(value))
			logging.info("new min {0} for '{1}' to {2}".format(key,self.name,value))
			self.check(key)
			return self.section,key,value
		else:
			logging.info("attribute {0} does not exist for '{1}'".format(key,self.name))
			return False



	def check(self, key):
		valueSet = float(getattr(self, key + "_set"))
		valueMeasured = float(getattr(self, key))
		logging.info("check {0} '{1}' current/set: {2}/{3}'C".format(key, self.name, valueMeasured, valueSet))
		if valueSet >= valueMeasured:
			logger.info("setting relays {0}/{1} to OPEN".format(self.section, getattr(self, key + "_relays")))
			for i in range(len(getattr(self, key + "_relays"))):
				relay = int(getattr(self, key + "_relays")[i])
				shiftpi.digitalWrite(relay, shiftpi.HIGH)
				#time.sleep(0.1)
		else:
			logger.info("setting relays {0}/{1} to CLOSE".format(self.section, getattr(self, key + "_relays")))
			for i in range(len(getattr(self, key + "_relays"))):
				relay = int(getattr(self, key + "_relays")[i])
				shiftpi.digitalWrite(relay, shiftpi.LOW)
				#time.sleep(0.1)
	
	def schedule(self):
		self.measure()
		self.updateRRD()
		for function in self.sensorFunctions:
				if getattr(self, function + "_setPoint") == True:
					self.check(function)
	
	
	def updateRRD(self):
		if self.temp != None or self.hum != None: 
			data = str(int(time.time()))
			if "temp" in self.sensorFunctions:
				data = data + ":" + str(self.temp)
				if self.temp_setPoint:
					data = data + ":" + str(self.temp_set)
			if "hum" in self.sensorFunctions:
				data = data + ":" + str(self.hum)
				if self.hum_setPoint:
					data = data + ":" + str(self.hum_set)

			rrdtool.update(self.db, data)
			logging.info("writing log for '{0}'".format(self.section))


	def fetchRRD(self, sensorFunction, resolution, start, end, *args):
		time, ds, RRDdata = rrdtool.fetch(self.db, 'AVERAGE','-r',str(resolution), '-s', str(start), '-e', str(end) )

		try:
			if "_set" in args:
				dataIndex = ds.index(sensorFunction+"_set")
			else:
				dataIndex = ds.index(sensorFunction)
		except:
			logger.info("error fetching data for {0} - {1}".format(self.section, sensorFunction))
			return False
		
		myList = []
		
		if "_set" in args:
			lastValue = getattr(self, sensorFunction+"_set")
		else:
			lastValue = getattr(self, sensorFunction)
		
		unit = getattr(self, sensorFunction + "_unit")
		
		data = [x[dataIndex] for x in RRDdata]
		i=0
		for item in data:
			date = int((time[0]+(time[2]*i))*1000)
			if item:
				value = round(item,1)
			else:
				value = None
			myList.append([date,value])
			i = i+1
		#date = int(end*1000)
		#value = round(float(lastValue),1)
		#myList.append([date,value])
		
		series = {'section':self.section,
			'seriesFunction':sensorFunction,
			'unit':unit,
			'lastValue':lastValue,
			'data':tuple(myList)}
		if "_set" in args:
			series['linkedTo'] = ':previous'
			series['dashStyle'] = 'Dash'
		return series




	def createRRD(self):
		rrdCreateOptions = [self.db,"--step",'600',"--start",'0']
		
		if "temp" in self.sensorFunctions:
			rrdCreateOptions.extend(["DS:temp:GAUGE:1800:U:U"])
			if self.temp_setPoint:
				rrdCreateOptions.extend(["DS:temp_set:GAUGE:1800:U:U"])
		
		if "hum" in self.sensorFunctions:
			rrdCreateOptions.extend(["DS:hum:GAUGE:1800:U:U"])
			if self.hum_setPoint:
				rrdCreateOptions.extend(["DS:hum_set:GAUGE:1800:U:U"])
		
		rrdCreateOptions.extend(["RRA:AVERAGE:0.5:1:288","RRA:AVERAGE:0.5:3:336","RRA:AVERAGE:0.5:6:672","RRA:AVERAGE:0.5:144:1825"])
		
		if os.path.isfile(self.db) == False:
			RRD = rrdtool.create(*rrdCreateOptions)
			logger.info("RRD not found, created '" + self.db +"' for logging")
		else:
			logger.info("using '" + self.db + "' for logging")
			return True

	
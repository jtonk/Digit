import requests, time, os
from bs4 import BeautifulSoup
import rrdtool
import config
import logging
logger = logging.getLogger('digitLog')


class onlineData:
	def __init__(self, service, location): 
		self.service = str(service)
		self.location = location
		self.temperature = "NaN"
		self.humidity = "NaN"
		self.db = config.dataPrefix + "/RRD/" + self.service+"_"+self.location + ".rrd"
		self.createRRD()
		
	def getOnline(self):
		### read data from KNMI online
		if self.service == "KNMI":
			data = requests.get("http://m.knmi.nl/index.php?i=Actueel&s=tabel_10min_data").text
			soup = BeautifulSoup(data)
			for row in soup.find('table').findAll('tr'):
				cols = row.findAll('td')
				if not cols:
					continue
				if cols[0].get_text() == self.location:
					self.temperature = round(float(cols[2].get_text().replace('&nbsp;', '').strip()),1)
					self.humidity = round(float(cols[4].get_text().replace('&nbsp;', '').strip()),1)
		print "{0}: {1}'C / {2}%".format(self.service+"_"+self.location, self.temperature, self.humidity)
	def createRRD(self):
		if os.path.isfile(self.db) == False:
			RRD = rrdtool.create(self.db, "--step", "600", "--start", '0',
			"DS:" + self.location + "_t:GAUGE:1800:U:U",
			"DS:" + self.location + "_h:GAUGE:1800:U:U",
			"RRA:AVERAGE:0.5:1:288",
			"RRA:AVERAGE:0.5:3:336",
			"RRA:AVERAGE:0.5:6:672",
			"RRA:AVERAGE:0.5:144:1825")
			logger.info("INIT: RRD not found, created '" + self.db +"' for logging")
		else:
			#logger.info("INIT: using '" + self.db + "' for logging")
			return True
	def updateRRD(self):
		rrdtool.update(self.db, 'N:{0}:{1}'.format(self.temperature, self.humidity))
		print "writing log for '{0}'".format(self.service+"_"+self.location)
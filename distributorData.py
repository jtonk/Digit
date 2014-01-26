import shiftpi
import logging
import time
logger = logging.getLogger('digitLog')
class distributorData:
	def __init__(self, name, nr):
		self.name = name
		self.nr = nr
		
		#hardware initialization, 8 cicks on/off
		self.changeValve([0,1,2,3,4,5,6,7], True)
		time.sleep(0.5)
		i=0
		while i<=7:
			self.changeValve([i], False)
			time.sleep(0.1)
			self.changeValve([i], True)
			time.sleep(0.2)
			i=i+1
		logging.info("initialized distributor '"+ self.name +"'")

	def changeValve(self, valves, state):
		for i in range(len(valves)):
			valve = int(valves[i])
			if state == True:
				shiftpi.digitalWrite(valve, shiftpi.HIGH)
				logger.info("setting distributor valve {0}-{1} to OPEN".format(self.name, valve))
			if state == False:
				shiftpi.digitalWrite(valve, shiftpi.LOW)
				logger.info("setting distributor valve {0}-{1} to CLOSE".format(self.name, valve))
			time.sleep(0.1)

import shiftpi
import logging
logger = logging.getLogger('digitLog')
class distributorData:
	def __init__(self, name, nr):
		self.name = name
		self.nr = nr
		shiftpi.digitalWrite(shiftpi.ALL, shiftpi.LOW)
	def changeValve(self, valves, state):
		for i in range(len(valves)):
			valve = int(valves[i])
			if state == True:
				shiftpi.digitalWrite(valve, shiftpi.HIGH)
				logger.info("setting distributor valve {0}-{1} to OPEN".format(self.name, valve))
			if state == False:
				shiftpi.digitalWrite(valve, shiftpi.LOW)
				logger.info("setting distributor valve {0}-{1} to CLOSE".format(self.name, valve))
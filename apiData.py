#!/usr/bin/env python
import rrdtool
import json
import time
import config
import logging
logger = logging.getLogger(__name__)

### apiData
def apiData(dataRequest):
	#apiData|INFO: ['api', 'graph', 'sensor', 'length', 'resolution', 'endNow']
	if dataRequest [1] == 'graph':
		if dataRequest[3]:
			f = jsonGraphData(dataRequest)
	#apiData|INFO: ['api', 'set', 'sensor', 'function', 'value']
	elif dataRequest [1] == 'set':
		sensorFunction = dataRequest[3]
		newValue = float(dataRequest[4])
		for keys,value in sorted(config.sensors.items()):

			if dataRequest[2] == 'all':
				response = value.setValue(sensorFunction,newValue)
			elif dataRequest[2] == value.section:
				response = value.setValue(sensorFunction,newValue)
		f = json.dumps(response, sort_keys=True, indent=4)
	return f

### jsonGraphAllData
def jsonGraphData(dataRequest):
#	try:
	sensorData = []
	data = []
	now = int(time.time())
	length = int(3600*24*float(dataRequest[3]))
	start = now - length
	end = now
	resolution = dataRequest[4]
	
	for key,value in sorted(config.sensors.items()):
		del sensorData[:]
		if dataRequest[2] == 'all':
			for sensorFunction in value.sensorFunctions:
				series = value.fetchRRD(sensorFunction, resolution, start, end)
				sensorData.append(series)
						
				if getattr(value, sensorFunction + "_setPoint"):
					series_setpoint = value.fetchRRD(sensorFunction, resolution, start, end, "_set")
					sensorData.append(series_setpoint)

			section = {'sensor':getattr(value, 'section'),
				'name':getattr(value, 'name'),
				'sensorID':getattr(value, 'sensorID'),
				'sensorType':getattr(value, 'sensorType'),
				'color':getattr(value, 'color'),
				'color2':getattr(value, 'color2'),
				'db':getattr(value,'db'),
				'sensorData':tuple(sensorData)}
			data.append(section)
			
		if dataRequest[2] == value.section:
			for sensorFunction in value.sensorFunctions:
				series = value.fetchRRD(sensorFunction, resolution, start, end)
				sensorData.append(series)
					
				if getattr(value, sensorFunction + "_setPoint"):
					series_setpoint = value.fetchRRD(sensorFunction, resolution, start, end, "_set")
					content.append(series_setpoint)
					
			section = {'sensor':getattr(value, 'section'),
				'name':getattr(value, 'name'),
				'sensorID':getattr(value, 'sensorID'),
				'sensorType':getattr(value, 'sensorType'),
				'color':getattr(value, 'color'),
				'color2':getattr(value, 'color2'),
				'db':getattr(value,'db'),
				'sensorData':tuple(sensorData)}
			data.append(section)

		f = json.dumps(data, sort_keys=True, indent=4)
	return f
	




#!/usr/bin/env python
import rrdtool
import json
import time
import config
import logging
logger = logging.getLogger(__name__)

### apiData
def apiData(dataRequest):
	#apiData|INFO: ['api', 'graph', 'all', 'options']
	if dataRequest [1] == 'graph':
		if dataRequest[3] == 'options':
			f = jsonGraphOptions(dataRequest)
		elif dataRequest[3]:
			f = jsonGraphData(dataRequest)
	elif dataRequest [1] == 'set':
		newTemp = float(dataRequest[3])
		for keys,value in sorted(config.sensors.items()):
			if dataRequest[2] == 'all':
				value.setTemp(newTemp)
			elif dataRequest[2] == value.sensor:
				value.setTemp(newTemp)
		f = jsonGraphOptions(dataRequest)
	return f

### jsonGraphAllData
def jsonGraphData(dataRequest):
#	try:
	myList = []
	myList_setpoint = []
	content = []
	now = int(time.time())
	length = int(3600*24*float(dataRequest[3]))
	start = now - length
	end = now
	for keys,value in sorted(config.sensors.items()):
		def getRRDData(dataRequest,keys,value):
			period, metric, rrdData = rrdtool.fetch(config.dataPrefix + '/RRD/' + value.sensor + '.rrd', 'AVERAGE','-r',str(dataRequest[4]), '-s', str(start), '-e', str(end) )
			i=0
			del myList[:]
			del myList_setpoint[:]
			for item in rrdData:
				date = int((period[0]+(period[2]*i))*1000)
				if item[0]:
					value1 = round(item[0],2)
					value2 = round(item[1],2)
				else:
					if i+1 == len(rrdData) and dataRequest[5] == 'endNow':
						value1 = round(float(value.temperature),2)
						value2 = round(float(value.temp_set),2)
						date = now*1000
					else:
						value1 = None
						value2 = None
				dataList = [date,value1]
				dataList_setpoint = [date,value2]
				myList.append(dataList)
				myList_setpoint.append(dataList_setpoint)
				i = i+1
			series = {'sensor':value.sensor,
				'name':value.name,
				'data':tuple(myList)}
			series_setpoint = {'sensor':value.sensor,
				'name':value.name + '_setpoint',
				'data':tuple(myList_setpoint)}
			return series, series_setpoint
		if dataRequest[2] == 'all':
			series, series_setpoint = getRRDData(dataRequest,keys,value)
			content.append(series)
			content.append(series_setpoint)
		if dataRequest[2] == value.sensor:
			series, series_setpoint = getRRDData(dataRequest,keys,value)
			content.append(series)
			content.append(series_setpoint)
#	except:
#		raise Exception("error")
		f = json.dumps(content)
	return f
	
def jsonGraphOptions(dataRequest):
#	try:
	content = []
	
	for keys,value in sorted(config.sensors.items()):
		def getOptionsData(dataRequest,keys,value):
			series = {'sensor':value.sensor,
				'name':value.name,
				'color':value.color,
				'lastValue':round(float(value.temperature),2),
				'lastSetPointValue':round(float(value.temp_set),2)}
			series_setpoint = {'sensor':value.sensor,
				'name':value.name + '_setpoint',
				'dashStyle':'Dash',
				'color':value.color,
				'linkedTo':':previous',
				'lastValue':round(float(value.temperature),2),
				'lastSetPointValue':round(float(value.temp_set),2)}
			return series, series_setpoint
		if dataRequest[2] == 'all':
			series, series_setpoint = getOptionsData(dataRequest,keys,value)
			content.append(series.copy())
			content.append(series_setpoint.copy())
		if dataRequest[2] == value.sensor:
			series, series_setpoint = getOptionsData(dataRequest,keys,value)
			content.append(series.copy())
			content.append(series_setpoint.copy())
#	except:
#		raise Exception("error")
		f = json.dumps(content)
	return f







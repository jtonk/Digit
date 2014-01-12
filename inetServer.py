#!/usr/bin/env python
 
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import config
import apiData
import logging
logger = logging.getLogger(__name__)
import urlparse
from os import curdir, sep
import shutil
import contextlib
import daemon


#Create custom HTTPRequestHandler class
class customHTTPRequestHandler(BaseHTTPRequestHandler):
	#handle GET command
	def do_GET(self):
		#logging.info(self.headers)
		rootdir = config.dataPrefix + "/www" #file location
		dataRequest = [10]
		try:
			dataRequest = self.path.split("/")
			dataRequest.pop(0)
			if dataRequest[0] == 'api':
				content = apiData.apiData(dataRequest)
				self.send_response(200)
				self.send_header('Content-type','text/json')
				self.end_headers()
				self.wfile.write(content)
			elif self.path.endswith(""):
				if self.path == '/':
					self.path = '/index.html'
				self.send_response(200)
#				self.send_header('Content-type','text/html')
				self.end_headers()
				with open(rootdir + self.path, 'rb') as content:
					shutil.copyfileobj(content, self.wfile)
			return
				
		except IOError:
			self.send_error(404, 'file not found')
		except:
			self.send_error(500, 'Internal Server Error')
	def log_message(self, format, *args):
		pass




def threadHTTP():
	logger.info('http server is starting...')
	server_address = ("", 80)
	server = HTTPServer(server_address, customHTTPRequestHandler)
	logger.info('http server is running...')
	server.serve_forever()





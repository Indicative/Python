#######################################################################
# indicative.py
# Standalone Client Library for Indicative's Input API. Uses a Queue and 
# multiple worker threads to send events to Indicative asynchronously.
# This client is a good choice for small volumes of events in standalone
# projects. 
#
# Note, if you are using Celery as part of your infrastructure, its 
# recommended to use our celery client instead. See the Indicative 
# documentation for more details
#######################################################################
from urlparse import urlparse
from threading import Thread
import httplib, sys
from Queue import Queue
import logging
import time
try:
    import json
except ImportError:
    #Python 2.5 does not come with json module.
    #This is kinda hacky, but it does work for our purposes
    class JSON:
    	def dumps(self, map):
			output = '{'
			addComma = False
			for key, value in map.iteritems():
				if addComma:
					output = ''.join([output,','])
				if isinstance(value, dict):
					output = ''.join([output,'"',str(key).replace('"','\\"'),'":',self.dumps(value)])
				else:
					output = ''.join([output,'"',str(key),'":','"',str(value).replace('"','\\"'),'"'])
				addComma=True
			output = ''.join([output,'}'])	
			print(output)
			return output
    
    json = JSON()

API_URL = 'https://api.indicative.com/service/event'
CONTENT_TYPE = 'application/json'
LOGGER_NAME = __name__

_api_key = None
_initialized = False
_queue = None
_misconfigured_warning = False
_threads=[]
_shutdown = False

class Event:
	def __init__(self, event_name, event_unique_id, api_key, param_dict):
		self.data = {'eventName':event_name, 'apiKey':api_key, 'eventUniqueId':event_unique_id, 
		'eventTime':long(round(time.time()*1000)), 'properties': param_dict}
		
	def json(self):
		return 	json.dumps(self.data)

def _doWork():
    while not _shutdown or not _queue.empty():
        event=_queue.get()
        _sendEvent(event)
        _queue.task_done()
    logging.getLogger(LOGGER_NAME).info('Thread Exit')

def _sendEvent(event):
    try:
        url = urlparse(API_URL)
        conn = httplib.HTTPConnection(url.netloc)
        event_string = json.dumps(event)
        conn.request('POST', url.path, event_string, {'Content-Type':'application/json'})
        res = conn.getresponse()
        if res.status != 200:
        	logging.getLogger(LOGGER_NAME).error(res.read())
    except:
        logging.getLogger(LOGGER_NAME).exception('Encountered exception while sending event.')


""" Sends an event to the Indicative API endpoint.

:param event_name: name of the event
:param event_unique_id: unique identifier for the user associated with the event
:param param_dict: dictionary object containing property names and values
:param api_key: the project's API key
"""
def record(event_name, event_unique_id, param_dict={}, api_key=None):
	global _initialized
	global _misconfigured_warning
	global _shutdown
	global _api_key
	if _shutdown:
		logging.getLogger(LOGGER_NAME).error('record() called after shutdown!')
	if api_key == None:
		if _api_key == None:
			if not _misconfigured_warning:
				return
			logging.getLogger(LOGGER_NAME).error('record() called before init() is called! '+
												'Please call init() first. This message '+
												'will only be logged once.')
			misconfigured_warning = True
			return
		api_key = _api_key
	else:
		if not _initialized:
			init(api_key)
		
		
	event = {'eventName':event_name, 'apiKey':api_key, 'eventUniqueId':event_unique_id, 
		'eventTime':long(round(time.time()*1000)), 'properties': param_dict}
	_queue.put(event)

""" Sets the API key and number of threads to use when recording events.  

:param api_key: the project's API key
:param num_threads: the number of threads to use
"""
def init(api_key, num_threads = 4):
	global _initialized
	global _queue
	global _api_key
	_initialized = True
	_api_key = api_key
	if _queue != None:
		logging.getLogger(LOGGER_NAME).warn('A second initialization attempt was detected. ')
	_queue=Queue()
	for i in range(num_threads):
	    t=Thread(target=_doWork)
	    t.setDaemon(False) #python 2.5 does not support daemon attribute
	    t.start()
	    _threads.append(t)
	    
def shutdown():
	global _shutdown
	_shutdown=True
    	logging.getLogger(LOGGER_NAME).warn('Shutting down the Indicative client. There are still %d events in the queue' % _queue.qsize())

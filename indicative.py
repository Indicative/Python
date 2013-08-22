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
    #Yuck. Python 2.5 does not come with json module
    #This is kinda hacky, but it does work for our purposes
    class JSON:
    	def dumps(self, map):
			output = '{'
			addComma = False
			for key, value in map.iteritems():
				if addComma:
					output = ''.join([output,','])
				if isinstance(value, dict):
					output = ''.join([output,'"',str(key),'":',self.dump(value)])
				else:
					output = ''.join([output,'"',str(key),'":','"',str(value),'"'])
				addComma=True
			output = ''.join([output,'}'])	
			return output
    
    json = JSON()

API_URL = 'https://api.skunkalytics.com/service/event'
CONTENT_TYPE = 'application/json'
LOGGER_NAME = __name__
NUM_THREADS=4

_project_id = None
_initialized = False
_queue = None
_misconfigured_warning = False
_threads=[]
_shutdown = False

class Event:
	def __init__(self, event_name, event_unique_id, project_id, param_dict):
		self.data = {'eventName':event_name, 'projectId':project_id, 'eventUniqueId':event_unique_id, 
		'eventTime':long(round(time.time()*1000)), 'properties': param_dict}
		
	def json(self):
		return 	json.dumps(self.data)

def _doWork():
    while True:
        event=_queue.get()
        _sendEvent(event)
        _queue.task_done()

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



def record(event_name, event_unique_id, project_id=None, param_dict={}):
	global _initialized
	global _misconfigured_warning
	global _shutdown
	if _shutdown:
		logging.getLogger(LOGGER_NAME).error('record() called after shutdown!')
	if project_id == None:
		if PROJECT_ID == None:
			if not _misconfigured_warning:
				return
			logging.getLogger(LOGGER_NAME).error('record() called before init() is called! '+
												'Please call init() first. This message '+
												'will only be logged once.')
			misconfigured_warning = True
			return
		project_id = PROJECT_ID
	else:
		if not _initialized:
			init(project_id)
		
		
	event = {'eventName':event_name, 'projectId':project_id, 'eventUniqueId':event_unique_id, 
		'eventTime':long(round(time.time()*1000)), 'properties': param_dict}
	_queue.put(event)

def init(project_id, num_threads = 10):
	global _initialized
	global _queue
	_initialized = True
	if _queue != None:
		logging.getLogger(LOGGER_NAME).warn('A second initialization attempt was detected. ')
	_queue=Queue()
	for i in range(THREADS):
	    t=Thread(target=_doWork)
	    t.daemon=True
	    t.start()
	    
def shutdown():
	global _shutdown
	
    

#######################################################################
# indicative.py
# Standalone Client Library for Indicative's Input API.  
# This client is SYNCHRONOUS. It's recommended that you use this client
# in the async processing part of your infrastructure.
# This client is a good choice for small volumes of events in standalone
# projects or for testing.
#######################################################################
from urlparse import urlparse
import httplib, sys
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
					output = ''.join([output,'"',str(key).replace('"','\\"'),'":','"',str(value).replace('"','\\"'),'"'])
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
_misconfigured_warning = False


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
	if api_key == None:
		if _api_key == None:
			if _misconfigured_warning:
				return
			logging.getLogger(LOGGER_NAME).error('record() called before init() is called! '+
												'Please call init() first. This message '+
												'will only be logged once.')
			_misconfigured_warning = True
			return
		api_key = _api_key
	else:
		if not _initialized:
			init(api_key)
		
		
	event = {'eventName':event_name, 'apiKey':api_key, 'eventUniqueId':event_unique_id, 
		'eventTime':long(round(time.time()*1000)), 'properties': param_dict}
	_sendEvent(event)

""" Sets the API key and number of threads to use when recording events.  

:param api_key: the project's API key
:param num_threads: the number of threads to use
"""
def init(api_key):
	global _initialized
	global _api_key
	_initialized = True
	_api_key = api_key

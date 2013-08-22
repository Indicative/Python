Python
======

Python Client for Indicative's REST API

Standalone Client Library for Indicative's Input API. Uses a Queue and multiple worker threads to send events to Indicative asynchronously. This client is a good choice for small volumes of events in standalone projects. 

Sample usage: record('Registration', 'user47', 'apiKey', {'Gender': 'Female', 'Age': 23});

For more details, see our documentation at: http://staging.skunkalytics.com/docs/integration.html

Python
======

Python Client for Indicative's REST API

Standalone Client Library for Indicative's Input API. Uses a Queue and multiple worker threads to send events to Indicative asynchronously. This client is a good choice for small volumes of events in standalone projects.  It has no external dependencies, so you'll never have library conflicts, and it should never slow down or break your app.  You should modify and extend this class to your heart's content.  As a best practice, consider adding a method that takes as a parameter the object representing the user, and adds certain default properties based on that user's characteristics (e.g., gender, age, etc.).

Sample usage: 

    record('Registration', 'user47', {'Gender': 'Female', 'Age': 23});

For more details, see our documentation at: http://www.indicative.com/docs/integration.html

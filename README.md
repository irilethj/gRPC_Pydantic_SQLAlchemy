As gRPC is a client-server communication framework, two components had to be implemented -
'reporting_server.py' and 'reporting_client.py'. The server should provide a response-streaming
endpoint, where it receives a set of coordinates, and responds with a stream of Spaceship entries.
As this is currently a test environment, even though every Spaceship should still have all the
parameters mentioned, they could be random. Also, they should be strictly typed, e.g.:

Alignment is an enum
Name is a string
Length is a float
Class is an enum
Size is an integer
Armed status is a bool
Each officer on board should have first name, last name and rank as strings

The number of officers on board is a random number from 0 (for enemy ships only) to 10.
The workflow should go like this:








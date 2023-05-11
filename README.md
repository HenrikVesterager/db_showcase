# db_showcase
Timescale DB with flask interface example
Steps: 
* Install docker on your PC
* Clone repo 
* Start containers
  * docker-compose up --build

## Buld 
 ``docker-compose up --build``
## Access 
Browse to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)to see some basic stats 

## Generate random data from browser
Browse to [http://127.0.0.1:5000/add_sample_data](http://127.0.0.1:5000/add_sample_data)

## Add data using curl: 

 ``
 curl http://localhost:5000/add_data -H "Content-Type: application/json" -H "Authorization: Bearer vYTKxJNCLEh7XsrZOhHHLEUE9MpkzFRxJQvcUXGvip4" -d '{"client_id": "client_123", "hardware_id": "hardware_456", "data": {"temperature": 20.5, "humidity": 52.0}, "timestamp": "2023-05-11T12:00:00Z"}'
 ``
 
 ## Read data using curl:
 ``
 curl -X GET  -H "Content-Type: application/json" -H"Authorization: Bearer vYTKxJNCLEh7XsrZOhHHLEUE9MpkzFRxJQvcUXGvip4"  "http://localhost:5000/get_data?client_id=client_123&hardware_id=hardware_456"
 ``
 
 
This repo contains the resources and code needed to ingest, aggregate, and output weather and weather station data to a Flask API. The code is currently structured to run on a local environment, but the base logic established here can be used to host the output on a server.

The Resources directory contains a SQLite file, hawaii.sqlite, that is used as the primary database for the Flask API. The SQLite database is visually represented via two CSV files; hawaii_measurements.csv and hawaii_stations.csv.

The climate.ipynb file serves as an exploration of precipitation and weather station data housed in the hawaii.sqlite file. SQLAlchemy is leveraged to interact with the SQLite file via python classes.

The app.py file leverages SQLAlchemy and Flask to create an API that allows users to interact with the data in a structured, web-based environment. The app contains both static and dynamic pages, which allows users to ascertain a general understanding of the data as well as search for specific data based on start and end dates.

# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
import datetime as dt
import pandas as pd

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the tables
from sqlalchemy.ext.automap import automap_base
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

def calculate_temp_stats(session, start_date, end_date=None):
    if end_date:
        # Query for start and end date range
        temp_stats = session.query(func.min(Measurement.tobs).label('min_temperature'),
                                   func.avg(Measurement.tobs).label('avg_temperature'),
                                   func.max(Measurement.tobs).label('max_temperature')) \
            .filter(Measurement.date >= start_date, Measurement.date <= end_date) \
            .first()
    else:
        # Query for start date only
        temp_stats = session.query(func.min(Measurement.tobs).label('min_temperature'),
                                   func.avg(Measurement.tobs).label('avg_temperature'),
                                   func.max(Measurement.tobs).label('max_temperature')) \
            .filter(Measurement.date >= start_date) \
            .first()

    return {
        'min_temperature': temp_stats.min_temperature,
        'avg_temperature': temp_stats.avg_temperature,
        'max_temperature': temp_stats.max_temperature
    }

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup and routes
app = Flask(__name__)

@app.route('/')
def home():
    # List of available routes
    routes = [
        '/api/v1.0/precipitation',
        '/api/v1.0/stations',
        '/api/v1.0/tobs',
        '/api/v1.0/<start>',
        '/api/v1.0/<start>/<end>',
        # Add more routes as needed
    ]

    return jsonify({'routes': routes})

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(str(most_recent_date), '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query for precipitation data in the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= one_year_ago) \
        .filter(Measurement.date <= most_recent_date) \
        .all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Define the /api/v1.0/stations route
@app.route('/api/v1.0/stations')
def stations():
    # Query for a list of stations
    station_list = session.query(Station.station).all()

    # Convert the query results to a list
    stations = [station[0] for station in station_list]

    return jsonify({'stations': stations})

# Define the /api/v1.0/tobs route
@app.route('/api/v1.0/tobs')
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station) \
        .group_by(Measurement.station) \
        .order_by(func.count().desc()) \
        .limit(1) \
        .scalar()

    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(str(most_recent_date), '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query for temperature observation data in the last 12 months for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == most_active_station) \
        .filter(Measurement.date >= one_year_ago) \
        .filter(Measurement.date <= most_recent_date) \
        .all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{'date': date, 'tobs': tobs} for date, tobs in temperature_data]

    return jsonify({'temperature_data': temperature_list})

# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temp_stats(start, end=None):
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

        if end:
            end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
        else:
            end_date = None

        result = calculate_temp_stats(session, start_date, end_date)

        return jsonify(result)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
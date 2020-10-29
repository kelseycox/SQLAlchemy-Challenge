# Import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import re

from flask import Flask, jsonify
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Database into New Model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Session link
session = Session(engine)

# Save References to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask
app = Flask(__name__)

# List all routes that are available.


@app.route("/")
def home():
    print("Received request for 'Home' page...")
    return (
        f"Welcome to the Home Page.<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>")

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.


@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= "2016-08-23").filter(Measurement.date <= "2017-08-23").order_by(Measurement.date).all()

    precipitation_dict = dict(precipitation)
    return jsonify(precipitation_dict)

# Return a JSON list of stations from the dataset.


@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name).all()
    stations = list(session.query(Station.stations)).all()
    return jsonify(stations)


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def temperature():

    session = Session(engine)
    last_date_year = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

# Most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.id))\
        .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    most_active = (Measurement.station == 'active_stations')

    temps = session.query(Measurement.station, Measurement.tobs).group_by(Measurement.station)\
        .filter(Measurement.station == 'most active').all()

# Temp over last year for most active station
    temp_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.date >= last_date_year).filter(Measurement.station == most_active).all()
    session.close()


# List of TOBS for previous year

    MDTS = [Measurement.date, Measurement.tobs, Measurement.station]

    tobs_temp = []
    for station, date, tobs in MDTS:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_dict["station"] = station
        tobs_temp.append(temp_dict)
    return jsonify(tobs_temp)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.


@app.route("/api/v1.0/<start>")
def start_date(start):
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= (year_ago)).\
        group_by(Measurement.date).all()
    start_list = list(start_date)
    return jsonify(start_list)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_date_year = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()
    start_end_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= (year_ago)).\
        filter(Measurement.date <= (last_date_year)).\
        group_by(Measurement.date).all()
    # Convert List of Tuples Into Normal List
    start_end_date_list = list(start_end_date)
    # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
    return jsonify(start_end_date_list)


if __name__ == "__main__":
    app.run(debug=True)

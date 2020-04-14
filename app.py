# Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation
    precipitation_results = session.query(Measurement.prcp, Measurement.date).\
        filter(Measurement.date >= '2016-08-23').all()
    
    session.close()

    # Create a dictionary and append to the precip list
    precip = []
    for result in precipitation_results:
        precipitation_dict = {"date":"prcp"}
        precipitation_dict["date"] = result[1]
        precipitation_dict["prcp"] = result[0]
        precip.append(precipitation_dict)
    
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query for list of stations
    station_info = session.query(Station.station).all()
    
    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_info))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query dates and temp observations of the most active station for the last year
    temp_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23', Measurement.station == 'USC00519281').\
        order_by(Measurement.tobs.asc()).all()

     # Convert list of tuples into normal list
    temp_list = list(np.ravel(temp_results))

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_only(start):
    session = Session(engine)

    # Query and return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start
    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    start_temps = []
    for temps in stats:
        temps_dict = {}
        temps_dict["Temp Min"] = temps[0]
        temps_dict["Temp Max"] = temps[2]
        temps_dict["Temp Avg"] = temps[1]
        start_temps.append(temps_dict)
    
    session.close()

    return jsonify(start_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    
    start_end_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter( Measurement.date <= end).all()
    
    start_end_temps = []
    for temps in start_end_stats:
        temps_dict = {}
        temps_dict["Temp Min"] = temps[0]
        temps_dict["Temp Max"] = temps[2]
        temps_dict["Temp Avg"] = temps[1]
        start_end_temps.append(temps_dict)

    return jsonify(start_end_temps)

if __name__ == "__main__":
    app.run(debug=True)
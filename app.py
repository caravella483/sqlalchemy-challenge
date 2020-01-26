import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Station API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/><br/>"
        f"When inputting start or end dates, format it as YYYY-MM-DD where Y is year, M is month, and D is day."
    )


# Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precip():

    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
#   * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    all_prc = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prc.append(prcp_dict)
#   * Return the JSON representation of your dictionary.
    return jsonify(all_prc)



@app.route("/api/v1.0/stations")
def stations():
#   * Return a JSON list of stations from the dataset.
    session = Session(engine)
    results = session.query(Station.name).distinct().all()
    session.close()
    station_list = []
    for station in results:
        station_list.append(station)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs_obs():
#   * query for the dates and temperature observations from a year from the last data point.
    session = Session(engine)
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #convert last date into datetime
    ldt = datetime.strptime(str(lastdate[0]), "%Y-%m-%d")

    # substract one year from last
    query_date = ldt - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prc_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > query_date).all()
    session.close()

#   * Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(prc_results)

@app.route("/api/v1.0/<start>")
def start_only(start):
    session = Session(engine)
#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    s_only = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close() 
    return jsonify(s_only)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    #   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    s_e = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(s_e)



if __name__ == "__main__":
    app.run(debug=True)

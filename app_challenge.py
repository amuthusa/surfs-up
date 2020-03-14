import datetime as dt
import numpy as np
import pandas as pd

#import sqlalchemy related dependency for SQLite connection
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, extract

#add flask realted dependency
from flask import Flask, jsonify

#create database connection
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

#using reflection to get the table details
Base.prepare(engine, reflect=True)

#get the reference to the tables we are interested in
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session to sqlite database
session = Session(engine)

#creating flask application
app = Flask(__name__)

#create route for welcome page
@app.route("/")
def welcome():
    return(
        '''
        Welcome to the Climate Ananlysis API!
        Available Routes:
        /api/v1.0/precipitation
        /api/v1.0/stations
        /api/v1.0/tobs
        /api/v1.0/temp/start/end
        '''
    )

#route for getting percipitation
@app.route("/api/v1.0/precipitation")
def percipitation():
    prev_year = dt.date(2017, 8, 23) -dt.timedelta(days=365)
    percipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    percip = {date: prcp for date, prcp in percipitation}
    return jsonify(percip)

#route for gettig stations
@app.route("/api/v1.0/stations")
def stations():
    results =  session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations)

#route for getting temperature
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) -dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

#route for getting statistics
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date <= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
        
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
    temps = list(np.ravel(results))
    return jsonify(temps)

#route for getting statistical data for june for all stations
@app.route("/api/v1.0/temp/stats/june")
def stats_june():
    stations_temp = get_temp_stats_based_on_month(6)
    return jsonify(stations_temp)

#route for getting statistical data for december for all stations
@app.route("/api/v1.0/temp/stats/december")
def stats_dec():
    stations_temp = get_temp_stats_based_on_month(12)
    return jsonify(stations_temp)

#function to get ll stations available 
#   for each station get the min,max and average tempertur for month of June
def get_temp_stats_based_on_month( month):
    #get all station
    results =  session.query(Station.station).all()
    stations = list(np.ravel(results))
    sel = [Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    stations_temp = dict()
    for station in stations:
        results = session.query(*sel).\
            filter(Measurement.station == station).\
                filter(extract('month', Measurement.date) == month).all()
        temps = np.ravel(results)
        stations_temp[temps[0]] = {"min_temp": temps[1], "max_temp": temps[2], "avg_temp": temps[3]}

    return stations_temp

if __name__ == "__main__":
    # @TODO: Create your app.run statement here
    app.run(port=8070, debug=True)


    
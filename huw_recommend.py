from flask import Flask, request, session, render_template, redirect, url_for, g
from flask_restful import Api, Resource, reqparse
import os
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv
import  thebestsql as bsql


app = Flask(__name__)
api = Api(app)

# We define these variables to (optionally) connect to an external MongoDB
# instance.
envvals = ["MONGODBUSER","MONGODBPASSWORD","MONGODBSERVER"]
dbstring = 'mongodb+srv://{0}:{1}@{2}/test?retryWrites=true&w=majority'

# Since we are asked to pass a class rather than an instance of the class to the
# add_resource method, we open the connection to the database outside of the 
# Recom class.
load_dotenv()
if os.getenv(envvals[0]) is not None:
    envvals = list(map(lambda x: str(os.getenv(x)), envvals))
    client = MongoClient(dbstring.format(*envvals))
else:
    client = MongoClient()
database = client.huwebshop

# Connecting to PostgreSQL
# def SQL_fetch_data(SQL):
#     connection = psycopg2.connect(user="postgres",
#                                   password="Floris09",
#                                   host="localhost",
#                                   port="5432",
#                                   database="huwebshop")
#     cursor = connection.cursor()
#     cursor.execute(SQL)
#     fetched_data = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return fetched_data

class Recom(Resource):
    """ This class represents the REST API that provides the recommendations for
    the webshop. At the moment, the API simply returns a random set of products
    to recommend."""


    def get(self, profileid, count, recommendationtype):
        connection = bsql.get_connection("Floris09", "huwebshop")
        cursor = bsql.get_cursor(connection)
        """ This function represents the handler for GET requests coming in
        through the API. It currently returns a random sample of products. """
        prodids = []
        cat = profileid
        cat = cat.replace("-", " ")
        cat = cat.replace(" en ", " & ")
        print(cat)
        data = bsql.select_data(cursor, f"SELECT * FROM andere_kochten_ook WHERE LOWER(category) = LOWER('{cat}');")
        for row in data:
            print(row)
            prodids = [row[1], row[2], row[3], row[4]]
        print(prodids)

        return prodids, 200
        randcursor = database.products.aggregate([{ '$sample': { 'size': count } }])
        prodids = list(map(lambda x: x['_id'], list(randcursor)))
        return prodids, 200

# This method binds the Recom class to the REST API, to parse specifically
# requests in the format described below.
api.add_resource(Recom, "/<string:profileid>/<int:count>/<string:recommendationtype>")
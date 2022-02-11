from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import urllib.parse
import os
import pyodbc
import pymssql
app = Flask(__name__)
server = '197.189.232.50'
database = 'Thrip'
username = 'sa'
password = 'NewFAsys098!'
driver= '{ODBC Driver 17 for SQL Server}'
conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
db = conn.cursor()
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_POOL_SIZE"] = 10
app.config["SQLALCHEMY_MAX_OVERFLOW"] = 20
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECURITY_PASSWORD_SALT"] = 'my_precious_two'
SQLALCHEMY_TRACK_MODIFICATIONS = False
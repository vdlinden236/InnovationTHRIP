from flask import Flask, Blueprint, render_template,request,session,redirect,url_for
from random import randint
from flask_database import db
from datetime import timedelta
from models import Users, UserRoles
from datetime import datetime
from passlib.hash import sha256_crypt

def generate_pin(length=4):
   upper_limit = 10 ** length
   pin = randint(0, upper_limit-1)
   return "{:0{length}d}".format(pin, length=length)

def check_pin():
    pin = generate_pin()
    user_data = db.engine.execute("""SELECT distinct
                                                 u.UserId, u.UserName, u.IsActive, u.PIN, u.OrgId, r.RoleId, n.RoleName
                                                 FROM Users u
                                                 left join UserRoles r on
                                                 u.UserId=r.UserId
                                                 left join Roles n on
                                                 n.RoleId=r.RoleId
                                                 where u.OrgId = {}
                                                 order by IsActive desc, UserName asc
                                                 """.format(session["OrgId"])).fetchall()
    for i in user_data:
        while i[3] == user_data:
            pin = generate_pin()
    return pin


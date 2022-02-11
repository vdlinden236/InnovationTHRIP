from flask_database import db

class Organisations(db.Model):

    __tablename__ = "Organisations"

    OrgId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(4096))
    IsActive = db.Column(db.Boolean)

class Users(db.Model):

    __tablename__ = "Users"

    UserId = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(4096))
    PIN = db.Column(db.String(4096))
    IsActive = db.Column(db.Integer)
    OrgId = db.Column(db.Integer)

class Roles(db.Model):

    __tablename__ = "Roles"

    RoleId = db.Column(db.Integer, primary_key=True)
    RoleName = db.Column(db.String(4096))

class UserRoles(db.Model):

    __tablename__ = "UserRoles"

    UserId = db.Column(db.Integer, primary_key=True)
    RoleId = db.Column(db.Integer)

class Contracts(db.Model):

    __tablename__ = "Contracts"

    ContractId = db.Column(db.Integer, primary_key=True)
    OrgId = db.Column(db.Integer)
    ContractReference = db.Column(db.String(4096))
    Description = db.Column(db.String(4096))
    DueDate = db.Column(db.DateTime)
    AssignedUserId = db.Column(db.Integer)
    ContactPerson = db.Column(db.String(4096))
    ContactNumber1 = db.Column(db.String(4096))
    ContactNumber2 = db.Column(db.String(4096))
    Notes = db.Column(db.String(4096))
    ActivityStatusId = db.Column(db.Integer)
    Value = db.Column(db.Integer)
    TemplateId = db.Column(db.Integer)
    Timestamp = db.Column(db.DateTime)
    OrderedDate = db.Column(db.DateTime)
class ContractItems(db.Model):

    __tablename__ = "ContractItems"

    ContractItemId = db.Column(db.Integer, primary_key=True)
    ContractId = db.Column(db.Integer)
    OrgId = db.Column(db.Integer)
    LineReferenceNumber = db.Column(db.String(4096))
    Description = db.Column(db.String(4096))
    Value = db.Column(db.String(4096))
    DurationEstMins = db.Column(db.Integer)
    ActivityStatusId = db.Column(db.Integer)
    TimeStamped = db.Column(db.DateTime)
    UserId = db.Column(db.Integer)
    AssignedUserId = db.Column(db.Integer)
    TemplateId = db.Column(db.Integer)

class Activities(db.Model):

    __tablename__ = "Activities"

    OrgId = db.Column(db.Integer, primary_key=True)
    ActivityId = db.Column(db.Integer)
    Activity = db.Column(db.String(4096))
    IsActive = db.Column(db.Boolean)
    Level = db.Column(db.Integer)

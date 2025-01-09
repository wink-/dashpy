from datetime import datetime
from . import db
from .base import BaseModel

# Each table in calsys becomes a class here
class CalibratedBy(BaseModel):
    """Organization performing calibration services"""
    __tablename__ = 'calibratedBy'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    name = db.Column(db.String(50), unique=True)
    
    # Relationships
    calibrations = db.relationship('Calibration', backref='calibrated_by')

class Calibration(BaseModel):
    """Record of all calibrations performed"""
    __tablename__ = 'calibration'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deviceID = db.Column(db.String(15), db.ForeignKey('device.ID'))
    calibratedByID = db.Column(db.String(15), db.ForeignKey('calibratedBy.ID'))
    employeeID = db.Column(db.String(15), db.ForeignKey('employee.ID'))
    calDate = db.Column(db.Date, comment='Date calibration was completed')
    calDue = db.Column(db.Date, comment='Date calibration was completed')
    status = db.Column(db.String(15), db.ForeignKey('status.ID'))
    record = db.Column(db.String(255), comment='Hyper link to scanned copy of calibration report')
    timeStamp = db.Column(db.TIMESTAMP, nullable=False, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # Status relationship
    status_info = db.relationship('Status', backref='calibrations')

class Device(BaseModel):
    """All calibrated devices"""
    __tablename__ = 'device'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), comment='Name for device')
    description = db.Column(db.String(50))
    sourceID = db.Column(db.String(15), db.ForeignKey('source.ID'))
    typeID = db.Column(db.String(15), db.ForeignKey('type.ID'), comment='Type classification of device')
    initDate = db.Column(db.Date)
    period = db.Column(db.String(15), db.ForeignKey('period.ID'), comment='Maximum time between calibrations')
    location = db.Column(db.String(15), db.ForeignKey('location.ID'), comment='location of calibrated device')
    ownerID = db.Column(db.String(15), db.ForeignKey('owner.ID'), comment='entity that owns calibrated device')
    serialNumber = db.Column(db.String(15))
    timeStamp = db.Column(db.TIMESTAMP, nullable=False, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # Relationships
    calibrations = db.relationship('Calibration', backref='device', lazy='dynamic')
    source = db.relationship('Source', backref='devices')
    device_type = db.relationship('Type', backref='devices')
    owner = db.relationship('Owner', backref='devices')
    device_location = db.relationship('Location', backref='devices')
    calibration_period = db.relationship('Period', backref='devices')

class Employee(BaseModel):
    """Employees assigned to devices or that calibrate devices"""
    __tablename__ = 'employee'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    userInit = db.Column(db.String(15))
    name = db.Column(db.String(50))
    
    # Relationships
    calibrations = db.relationship('Calibration', backref='employee', lazy='dynamic')

class Location(BaseModel):
    """All locations that devices can be installed or kept at"""
    __tablename__ = 'location'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    name = db.Column(db.String(50))

class Owner(BaseModel):
    """Organizations that can own calibrated devices"""
    __tablename__ = 'owner'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    name = db.Column(db.String(50), unique=True)

class Period(BaseModel):
    """Frequencies that calibrations must be performed"""
    __tablename__ = 'period'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    name = db.Column(db.String(50))

class Source(BaseModel):
    """Manufactures, vendors or suppliers of calibrated devices"""
    __tablename__ = 'source'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    name = db.Column(db.String(50))

class Status(BaseModel):
    """Possible statuses for calibrated devices"""
    __tablename__ = 'status'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    name = db.Column(db.String(50))

class Type(BaseModel):
    """All device types calibrated"""
    __tablename__ = 'type'
    __bind_key__ = 'calsys'
    
    ID = db.Column(db.String(15), primary_key=True, default='none')
    name = db.Column(db.String(50))
    procLink = db.Column(db.String(255), comment='Hyper link to calibration procedures for device types')

# Helper methods for views
def get_calibration_due(db_session):
    """Recreate the calibrationDue view using SQLAlchemy"""
    from sqlalchemy import text
    return db_session.execute(text("""
        SELECT c.ID, cm.deviceID, cm.name, cm.description, cm.typeID, 
               cm.location, c.status, c.calDate, c.calDue, cm.period
        FROM calibrationMaxID cm
        JOIN calibration c ON c.ID = cm.ID
        WHERE c.calDue > 0
        ORDER BY c.calDue
    """))

def get_cal_export(db_session):
    """Recreate the calExport view using SQLAlchemy"""
    from sqlalchemy import text
    return db_session.execute(text("""
        SELECT d.location, d.name, c.ID, e.userInit, c.employeeID,
               c.calDate, c.calDue, c.status
        FROM calibrationMaxID cm
        JOIN calibration c ON c.ID = cm.ID
        JOIN employee e ON e.ID = c.employeeID
        JOIN device d ON d.ID = c.deviceID
        WHERE c.status = 'Active' OR c.status = 'CalInv'
        ORDER BY d.location, d.name, c.ID
    """))

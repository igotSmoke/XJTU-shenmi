from database import db

class Fleet(db.Model):
    __tablename__ = 'fleet'
    
    fleet_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    # 关系
    vehicles = db.relationship('Vehicle', backref='fleet', lazy=True)
    drivers = db.relationship('Driver', backref='fleet', lazy=True)

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    
    license_plate = db.Column(db.String(20), primary_key=True)
    manufacturer = db.Column(db.String(50))
    production_date = db.Column(db.Date)
    fleet_id = db.Column(db.Integer, db.ForeignKey('fleet.fleet_id'))
    
    # 关系
    drives = db.relationship('Drive', backref='vehicle', lazy=True)

class Driver(db.Model):
    __tablename__ = 'driver'
    
    driver_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    fleet_id = db.Column(db.Integer, db.ForeignKey('fleet.fleet_id'))
    hire_period = db.Column(db.String(50))
    
    # 关系
    drives = db.relationship('Drive', backref='driver', lazy=True)

class Drive(db.Model):
    __tablename__ = 'drive'
    
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.driver_id'), primary_key=True)
    license_plate = db.Column(db.String(20), db.ForeignKey('vehicle.license_plate'), primary_key=True)
    drive_date = db.Column(db.Date, primary_key=True)
    mileage = db.Column(db.Integer) 
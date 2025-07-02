from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date

# Fleet operations
def get_fleet(db: Session, fleet_id: int):
    return db.query(models.Fleet).filter(models.Fleet.fleet_id == fleet_id).first()

def get_fleets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Fleet).offset(skip).limit(limit).all()

def create_fleet(db: Session, fleet: schemas.FleetCreate):
    db_fleet = models.Fleet(name=fleet.name)
    db.add(db_fleet)
    db.commit()
    db.refresh(db_fleet)
    return db_fleet

def update_fleet(db: Session, fleet_id: int, fleet: schemas.FleetCreate):
    db_fleet = get_fleet(db, fleet_id)
    if db_fleet:
        db_fleet.name = fleet.name
        db.commit()
        db.refresh(db_fleet)
    return db_fleet

def delete_fleet(db: Session, fleet_id: int):
    db_fleet = get_fleet(db, fleet_id)
    if db_fleet:
        db.delete(db_fleet)
        db.commit()
    return db_fleet

# Vehicle operations
def get_vehicle(db: Session, license_plate: str):
    return db.query(models.Vehicle).filter(models.Vehicle.license_plate == license_plate).first()

def get_vehicles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vehicle).offset(skip).limit(limit).all()

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate):
    db_vehicle = models.Vehicle(
        license_plate=vehicle.license_plate,
        manufacturer=vehicle.manufacturer,
        production_date=vehicle.production_date,
        fleet_id=vehicle.fleet_id
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, license_plate: str, vehicle: schemas.VehicleCreate):
    db_vehicle = get_vehicle(db, license_plate)
    if db_vehicle:
        db_vehicle.manufacturer = vehicle.manufacturer
        db_vehicle.production_date = vehicle.production_date
        db_vehicle.fleet_id = vehicle.fleet_id
        db.commit()
        db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, license_plate: str):
    db_vehicle = get_vehicle(db, license_plate)
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
    return db_vehicle

# Driver operations
def get_driver(db: Session, driver_id: int):
    return db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()

def get_drivers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Driver).offset(skip).limit(limit).all()

def create_driver(db: Session, driver: schemas.DriverCreate):
    db_driver = models.Driver(
        name=driver.name,
        phone=driver.phone,
        fleet_id=driver.fleet_id,
        hire_period=driver.hire_period
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

def update_driver(db: Session, driver_id: int, driver: schemas.DriverCreate):
    db_driver = get_driver(db, driver_id)
    if db_driver:
        db_driver.name = driver.name
        db_driver.phone = driver.phone
        db_driver.fleet_id = driver.fleet_id
        db_driver.hire_period = driver.hire_period
        db.commit()
        db.refresh(db_driver)
    return db_driver

def delete_driver(db: Session, driver_id: int):
    db_driver = get_driver(db, driver_id)
    if db_driver:
        db.delete(db_driver)
        db.commit()
    return db_driver

# Drive operations
def get_drive(db: Session, driver_id: int, license_plate: str, drive_date: date):
    return db.query(models.Drive).filter(
        models.Drive.driver_id == driver_id,
        models.Drive.license_plate == license_plate,
        models.Drive.drive_date == drive_date
    ).first()

def get_drives(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Drive).offset(skip).limit(limit).all()

def create_drive(db: Session, drive: schemas.DriveCreate):
    db_drive = models.Drive(
        driver_id=drive.driver_id,
        license_plate=drive.license_plate,
        drive_date=drive.drive_date,
        mileage=drive.mileage
    )
    db.add(db_drive)
    db.commit()
    db.refresh(db_drive)
    return db_drive

def update_drive(db: Session, driver_id: int, license_plate: str, drive_date: date, drive: schemas.DriveCreate):
    db_drive = get_drive(db, driver_id, license_plate, drive_date)
    if db_drive:
        db_drive.mileage = drive.mileage
        db.commit()
        db.refresh(db_drive)
    return db_drive

def delete_drive(db: Session, driver_id: int, license_plate: str, drive_date: date):
    db_drive = get_drive(db, driver_id, license_plate, drive_date)
    if db_drive:
        db.delete(db_drive)
        db.commit()
    return db_drive 
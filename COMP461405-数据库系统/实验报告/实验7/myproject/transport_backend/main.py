from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine
from datetime import date

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fleet Endpoints
@app.post("/fleets/", response_model=schemas.Fleet)
def create_fleet(fleet: schemas.FleetCreate, db: Session = Depends(get_db)):
    return crud.create_fleet(db=db, fleet=fleet)

@app.get("/fleets/", response_model=List[schemas.Fleet])
def read_fleets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    fleets = crud.get_fleets(db, skip=skip, limit=limit)
    return fleets

@app.get("/fleets/{fleet_id}", response_model=schemas.Fleet)
def read_fleet(fleet_id: int, db: Session = Depends(get_db)):
    db_fleet = crud.get_fleet(db, fleet_id=fleet_id)
    if db_fleet is None:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return db_fleet

@app.put("/fleets/{fleet_id}", response_model=schemas.Fleet)
def update_fleet(fleet_id: int, fleet: schemas.FleetCreate, db: Session = Depends(get_db)):
    db_fleet = crud.update_fleet(db, fleet_id=fleet_id, fleet=fleet)
    if db_fleet is None:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return db_fleet

@app.delete("/fleets/{fleet_id}", response_model=schemas.Fleet)
def delete_fleet(fleet_id: int, db: Session = Depends(get_db)):
    db_fleet = crud.delete_fleet(db, fleet_id=fleet_id)
    if db_fleet is None:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return db_fleet

# Vehicle Endpoints
@app.post("/vehicles/", response_model=schemas.Vehicle)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    return crud.create_vehicle(db=db, vehicle=vehicle)

@app.get("/vehicles/", response_model=List[schemas.Vehicle])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vehicles = crud.get_vehicles(db, skip=skip, limit=limit)
    return vehicles

@app.get("/vehicles/{license_plate}", response_model=schemas.Vehicle)
def read_vehicle(license_plate: str, db: Session = Depends(get_db)):
    db_vehicle = crud.get_vehicle(db, license_plate=license_plate)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.put("/vehicles/{license_plate}", response_model=schemas.Vehicle)
def update_vehicle(license_plate: str, vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = crud.update_vehicle(db, license_plate=license_plate, vehicle=vehicle)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.delete("/vehicles/{license_plate}", response_model=schemas.Vehicle)
def delete_vehicle(license_plate: str, db: Session = Depends(get_db)):
    db_vehicle = crud.delete_vehicle(db, license_plate=license_plate)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

# Driver Endpoints
@app.post("/drivers/", response_model=schemas.Driver)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    return crud.create_driver(db=db, driver=driver)

@app.get("/drivers/", response_model=List[schemas.Driver])
def read_drivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    drivers = crud.get_drivers(db, skip=skip, limit=limit)
    return drivers

@app.get("/drivers/{driver_id}", response_model=schemas.Driver)
def read_driver(driver_id: int, db: Session = Depends(get_db)):
    db_driver = crud.get_driver(db, driver_id=driver_id)
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_driver

@app.put("/drivers/{driver_id}", response_model=schemas.Driver)
def update_driver(driver_id: int, driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    db_driver = crud.update_driver(db, driver_id=driver_id, driver=driver)
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_driver

@app.delete("/drivers/{driver_id}", response_model=schemas.Driver)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    db_driver = crud.delete_driver(db, driver_id=driver_id)
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_driver

# Drive Endpoints
@app.post("/drives/", response_model=schemas.Drive)
def create_drive(drive: schemas.DriveCreate, db: Session = Depends(get_db)):
    return crud.create_drive(db=db, drive=drive)

@app.get("/drives/", response_model=List[schemas.Drive])
def read_drives(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    drives = crud.get_drives(db, skip=skip, limit=limit)
    return drives

@app.get("/drives/{driver_id}/{license_plate}/{drive_date}", response_model=schemas.Drive)
def read_drive(driver_id: int, license_plate: str, drive_date: date, db: Session = Depends(get_db)):
    db_drive = crud.get_drive(db, driver_id=driver_id, license_plate=license_plate, drive_date=drive_date)
    if db_drive is None:
        raise HTTPException(status_code=404, detail="Drive record not found")
    return db_drive

@app.put("/drives/{driver_id}/{license_plate}/{drive_date}", response_model=schemas.Drive)
def update_drive(driver_id: int, license_plate: str, drive_date: date, drive: schemas.DriveCreate, db: Session = Depends(get_db)):
    db_drive = crud.update_drive(db, driver_id=driver_id, license_plate=license_plate, drive_date=drive_date, drive=drive)
    if db_drive is None:
        raise HTTPException(status_code=404, detail="Drive record not found")
    return db_drive

@app.delete("/drives/{driver_id}/{license_plate}/{drive_date}", response_model=schemas.Drive)
def delete_drive(driver_id: int, license_plate: str, drive_date: date, db: Session = Depends(get_db)):
    db_drive = crud.delete_drive(db, driver_id=driver_id, license_plate=license_plate, drive_date=drive_date)
    if db_drive is None:
        raise HTTPException(status_code=404, detail="Drive record not found")
    return db_drive 
from datetime import date
from pydantic import BaseModel

class FleetBase(BaseModel):
    name: str

class FleetCreate(FleetBase):
    pass

class Fleet(FleetBase):
    fleet_id: int

    class Config:
        orm_mode = True

class VehicleBase(BaseModel):
    license_plate: str
    manufacturer: str | None = None
    production_date: date | None = None
    fleet_id: int | None = None

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    class Config:
        orm_mode = True

class DriverBase(BaseModel):
    name: str | None = None
    phone: str | None = None
    fleet_id: int | None = None
    hire_period: str | None = None

class DriverCreate(DriverBase):
    pass

class Driver(DriverBase):
    driver_id: int

    class Config:
        orm_mode = True

class DriveBase(BaseModel):
    driver_id: int
    license_plate: str
    drive_date: date
    mileage: int | None = None

class DriveCreate(DriveBase):
    pass

class Drive(DriveBase):
    class Config:
        orm_mode = True 
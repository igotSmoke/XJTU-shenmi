from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Fleet(Base):
    __tablename__ = "fleet"

    fleet_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    vehicles = relationship("Vehicle", back_populates="fleet")
    drivers = relationship("Driver", back_populates="fleet")

class Vehicle(Base):
    __tablename__ = "vehicle"

    license_plate = Column(String, primary_key=True, index=True)
    manufacturer = Column(String)
    production_date = Column(Date)
    fleet_id = Column(Integer, ForeignKey("fleet.fleet_id"))

    fleet = relationship("Fleet", back_populates="vehicles")
    drives = relationship("Drive", back_populates="vehicle")

class Driver(Base):
    __tablename__ = "driver"

    driver_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    fleet_id = Column(Integer, ForeignKey("fleet.fleet_id"))
    hire_period = Column(String)

    fleet = relationship("Fleet", back_populates="drivers")
    drives = relationship("Drive", back_populates="driver")

class Drive(Base):
    __tablename__ = "drive"

    driver_id = Column(Integer, ForeignKey("driver.driver_id"), primary_key=True)
    license_plate = Column(String, ForeignKey("vehicle.license_plate"), primary_key=True)
    drive_date = Column(Date, primary_key=True)
    mileage = Column(Integer)

    driver = relationship("Driver", back_populates="drives")
    vehicle = relationship("Vehicle", back_populates="drives") 
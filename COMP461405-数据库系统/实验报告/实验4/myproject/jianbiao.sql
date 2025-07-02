CREATE TABLE fleet (
    fleet_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
CREATE TABLE vehicle (
    license_plate VARCHAR(20) PRIMARY KEY,
    manufacturer VARCHAR(100),
    production_date DATE,
    fleet_id INTEGER REFERENCES fleet(fleet_id)
);

CREATE TABLE driver (
    driver_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    fleet_id INTEGER REFERENCES fleet(fleet_id),
    hire_period VARCHAR(50)
);

CREATE TABLE drive (
    driver_id INTEGER REFERENCES driver(driver_id),
    license_plate VARCHAR(20) REFERENCES vehicle(license_plate),
    drive_date DATE,
    mileage INTEGER,
    PRIMARY KEY (driver_id, license_plate, drive_date)
);


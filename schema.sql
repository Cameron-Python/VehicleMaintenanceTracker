
CREATE DATABASE IF NOT EXISTS VehicleMaintenanceTracker;

USE VehicleMaintenanceTracker;

CREATE TABLE User (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Vehicle (
    VehicleID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Make VARCHAR(50) NOT NULL,
    Model VARCHAR(50) NOT NULL,
    Year INT NOT NULL,
    VIN VARCHAR(17) UNIQUE,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);

CREATE TABLE IF NOT EXISTS ServiceType (
    ServiceTypeID INT AUTO_INCREMENT PRIMARY KEY,
    ServiceName VARCHAR(100) NOT NULL,
    Description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Location (
    LocationID INT AUTO_INCREMENT PRIMARY KEY,
    LocationName VARCHAR(100) NOT NULL,
    Address VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS MaintenanceRecord (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    VehicleID INT NOT NULL,
    ServiceTypeID INT NOT NULL,
    LocationID INT,
    ServiceDate DATE NOT NULL,
    Mileage INT NOT NULL,
    Cost DECIMAL(10,2),

    FOREIGN KEY (VehicleID)
        REFERENCES Vehicle(VehicleID),

    FOREIGN KEY (ServiceTypeID)
        REFERENCES ServiceType(ServiceTypeID),

    FOREIGN KEY (LocationID)
        REFERENCES Location(LocationID)
);

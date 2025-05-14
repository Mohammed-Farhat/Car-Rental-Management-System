CREATE SCHEMA rentalManagementSystem;

CREATE TABLE users
(
    userID INT AUTO_INCREMENT PRIMARY KEY,
    userName VARCHAR(10) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') NOT NULL DEFAULT 'user'
);

CREATE TABLE dealers
(
    dealerID INT AUTO_INCREMENT PRIMARY KEY,
    dealerName VARCHAR(100) NOT NULL,
    phoneNumber VARCHAR(20) NOT NULL
);

CREATE TABLE cars 
(
    carID INT AUTO_INCREMENT PRIMARY KEY,
    carName VARCHAR(100) NOT NULL,
    carModel VARCHAR(100) NOT NULL,
    carModelYear INT NOT NULL,
    carLicensePlate VARCHAR(20) NOT NULL UNIQUE,
    dealerID INT,
    FOREIGN KEY (dealerID) REFERENCES dealers(dealerID) ON DELETE SET NULL
);

CREATE TABLE carInventory 
(
    carID INT NOT NULL,
    inventoryID INT AUTO_INCREMENT PRIMARY KEY,
    pricePerDay DECIMAL(10,2) NOT NULL,
    isAvailable BOOLEAN DEFAULT 1,
    FOREIGN KEY (carID) REFERENCES cars(carID) ON DELETE CASCADE
);

CREATE TABLE rentedCars 
(
    rentalID INT AUTO_INCREMENT PRIMARY KEY,
    renterID INT NOT NULL,
    inventoryID INT NOT NULL,
    rentDate DATE NOT NULL,
    returnDate DATE NOT NULL,
    insuranceType ENUM('basic', 'standard', 'premium') NOT NULL,
    insuranceCost DECIMAL(10,2) NOT NULL,
    rentalCost DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (renterID) REFERENCES users(userID) ON DELETE CASCADE,
    FOREIGN KEY (inventoryID) REFERENCES carInventory(inventoryID) ON DELETE CASCADE
);

CREATE TABLE carSpecs
(
    inventoryID INT NOT NULL,
    horsepower VARCHAR(50),
    seatingCapacity INT,
    fuelEfficiency VARCHAR(50),
    FOREIGN KEY (inventoryID) REFERENCES carInventory(inventoryID) ON DELETE CASCADE
);

CREATE TABLE transactions
(
    transactionID INT AUTO_INCREMENT PRIMARY KEY,
    rentalID INT NOT NULL,
    transactionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rentalID) REFERENCES rentedCars(rentalID) ON DELETE CASCADE
);




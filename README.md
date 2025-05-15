# Car-Rental-Management-System

A full-featured Car Rental Management System developed using **Python** and **MySQL**, featuring a graphical user interface (GUI) built with **Tkinter**.

The system provides separate panels for both users and administrators. Regular users can browse available cars, view specifications, rent vehicles with insurance options, return them, and view their transaction logs. Administrators can manage the car inventory by adding, editing, or removing cars and adjusting rental costs.

Security is a key aspect of the system, with password hashing implemented using **bcrypt**, and role-based access control (admin/user) enforced at login.

## ✨ Features

### 👤 User Features
- Login / Sign Up with validation
- Secure password hashing using bcrypt
- View available cars with model, license, and rental cost
- View detailed car specifications (horsepower, seating, fuel efficiency)
- Rent a car with date and insurance selection
- Return a car and update availability
- View personal transaction history
- Refresh available cars list

### 🛠️ Admin Features
- Add new cars (car info, pricing, specs)
- Remove cars from inventory
- Edit daily rental cost
- View all available inventory
- Role automatically granted if username starts with `admin` and password is `ADMIN2025`

## 🧰 Technologies Used

- **Python 3**
- **Tkinter** (GUI)
- **MySQL** (Database)
- **bcrypt** (Password Hashing)
- **python-dotenv** (Environment Variables)

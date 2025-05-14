import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import bcrypt
from datetime import datetime
from dotenv import load_dotenv
import os

# ------------------ Load Environment Variables ------------------
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_ADMIN_USERNAME = os.getenv("DB_ADMIN_USERNAME")
DB_ADMIN_PASSWORD = os.getenv("DB_ADMIN_PASSWORD")

# ------------------ Utility Functions ------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(input_pw, hashed_pw):
    return bcrypt.checkpw(input_pw.encode('utf-8'), hashed_pw.encode('utf-8'))

# ------------------ Main Application Class ------------------
class CarRentalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Rental System")
        self.geometry("800x600")
        
        # Use ttk themed style for a modern look
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Initialize DB connection
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to DB:\n{err}")
            self.destroy()
            return

        # Container frame to hold all pages
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames for page switching
        self.frames = {}
        for F in (StartPage, LoginPage, SignupPage, AdminPanel, UserPanel):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

# ------------------ Start (Welcome) Page ------------------
class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        title = ttk.Label(self, text="Welcome to the Car Rental System", font=("Arial", 20))
        title.pack(pady=20)
        ttk.Button(self, text="Login", width=20,
                   command=lambda: controller.show_frame("LoginPage")).pack(pady=10)
        ttk.Button(self, text="Sign Up", width=20,
                   command=lambda: controller.show_frame("SignupPage")).pack(pady=10)

# ------------------ Login Page ------------------
class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        title = ttk.Label(self, text="Login", font=("Arial", 20))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Back",
                   command=lambda: controller.show_frame("StartPage")).grid(row=4, column=0, columnspan=2, pady=10)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if len(username) < 3 or len(password) < 5:
            messagebox.showwarning("Validation Error", "Username must be at least 3 characters and password at least 5 characters.")
            return
        try:
            self.controller.cursor.execute("SELECT userID, password, role FROM users WHERE userName = %s", (username,))
            result = self.controller.cursor.fetchone()
            if result:
                userID, hashed_pw, role = result
                if check_password(password, hashed_pw):
                    # Switch to admin or user panel
                    if role == 'admin':
                        self.controller.frames["AdminPanel"].set_admin_details(userID)
                        self.controller.show_frame("AdminPanel")
                    else:
                        self.controller.frames["UserPanel"].set_user_details(userID)
                        self.controller.show_frame("UserPanel")
                else:
                    messagebox.showerror("Login Failed", "Incorrect password.")
            else:
                messagebox.showerror("Login Failed", "User does not exist. Please sign up first.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

# ------------------ Sign Up Page ------------------
class SignupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        title = ttk.Label(self, text="Sign Up", font=("Arial", 20))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Email:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(self, text="Sign Up", command=self.signup).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Back",
                   command=lambda: controller.show_frame("StartPage")).grid(row=5, column=0, columnspan=2, pady=10)
    
    def signup(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if len(username) < 3 or len(password) < 5:
            messagebox.showwarning("Validation Error", "Username must be at least 3 characters and password at least 5 characters.")
            return

        # Give admin role if username/password match admin settings
        role = 'admin' if username.startswith(DB_ADMIN_USERNAME) and password == DB_ADMIN_PASSWORD else 'user'
        hashed = hash_password(password)
        try:
            self.controller.cursor.execute(
                "INSERT INTO users (userName, email, password, role) VALUES (%s, %s, %s, %s)",
                (username, email, hashed, role)
            )
            self.controller.conn.commit()
            messagebox.showinfo("Success", "Account created successfully. Please login.")
            self.controller.show_frame("LoginPage")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

# ------------------ Admin Panel Page ------------------
class AdminPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.admin_id = None
        
        title = ttk.Label(self, text="Admin Panel", font=("Arial", 20))
        title.pack(pady=10)
        
        # Inventory Treeview
        self.tree = ttk.Treeview(self, columns=("Inventory ID", "Car Name", "Model", "Year", "License", "Price/Day"),
                                 show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button frame for admin actions
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Car", command=self.add_car).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Remove Car", command=self.remove_car).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Edit Cost", command=self.edit_cost).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_inventory).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Logout",
                   command=lambda: self.controller.show_frame("StartPage")).grid(row=0, column=4, padx=5)
        
        self.load_inventory()
    
    def set_admin_details(self, admin_id):
        self.admin_id = admin_id
        self.load_inventory()
    
    def load_inventory(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        query = """
            SELECT ci.inventoryID, c.carName, c.carModel, c.carModelYear, c.carLicensePlate, ci.pricePerDay
            FROM carInventory ci
            JOIN cars c ON ci.carID = c.carID
        """
        try:
            self.controller.cursor.execute(query)
            for row in self.controller.cursor.fetchall():
                self.tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
    
    def add_car(self):
        add_win = tk.Toplevel(self)
        add_win.title("Add Car")
        labels = ["Name", "Model", "Year", "License Plate", "Price/Day", "Horsepower", "Seating", "Fuel Efficiency"]
        entries = {}
        for i, text in enumerate(labels):
            ttk.Label(add_win, text=f"{text}:").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(add_win)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[text] = entry

        def confirm_add():
            try:
                carName = entries["Name"].get()
                model = entries["Model"].get()
                year = int(entries["Year"].get())
                plate = entries["License Plate"].get()
                price = float(entries["Price/Day"].get())
                hp = entries["Horsepower"].get()
                seat = int(entries["Seating"].get())
                fuel = entries["Fuel Efficiency"].get()
                cur = self.controller.cursor
                conn = self.controller.conn

                cur.execute("INSERT INTO cars (carName, carModel, carModelYear, carLicensePlate) VALUES (%s, %s, %s, %s)",
                            (carName, model, year, plate))
                carID = cur.lastrowid
                cur.execute("INSERT INTO carInventory (carID, pricePerDay, isAvailable) VALUES (%s, %s, 1)", (carID, price))
                inventoryID = cur.lastrowid
                cur.execute("INSERT INTO carSpecs (inventoryID, horsepower, seatingCapacity, fuelEfficiency) VALUES (%s, %s, %s, %s)",
                            (inventoryID, hp, seat, fuel))
                conn.commit()
                messagebox.showinfo("Success", "Car added successfully.")
                add_win.destroy()
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(add_win, text="Add", command=confirm_add).grid(row=len(labels), column=0, columnspan=2, pady=10)
    
    def remove_car(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a car to remove.")
            return
        inventoryID = self.tree.item(selected[0])['values'][0]
        try:
            self.controller.cursor.execute("DELETE FROM carInventory WHERE inventoryID = %s", (inventoryID,))
            self.controller.conn.commit()
            messagebox.showinfo("Removed", "Car removed from inventory.")
            self.load_inventory()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def edit_cost(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a car to edit.")
            return
        inventoryID = self.tree.item(selected[0])['values'][0]
        current_cost = self.tree.item(selected[0])['values'][5]
        cost_win = tk.Toplevel(self)
        cost_win.title("Edit Cost")
        ttk.Label(cost_win, text="New Price Per Day:").grid(row=0, column=0, padx=5, pady=5)
        cost_entry = ttk.Entry(cost_win)
        cost_entry.insert(0, str(current_cost))
        cost_entry.grid(row=0, column=1, padx=5, pady=5)

        def confirm_edit():
            try:
                new_cost = float(cost_entry.get())
                self.controller.cursor.execute("UPDATE carInventory SET pricePerDay = %s WHERE inventoryID = %s",
                                                 (new_cost, inventoryID))
                self.controller.conn.commit()
                messagebox.showinfo("Updated", "Rental cost updated.")
                cost_win.destroy()
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(cost_win, text="Update", command=confirm_edit).grid(row=1, column=0, columnspan=2, pady=10)

# ------------------ User Panel Page ------------------
class UserPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.user_id = None
        
        title = ttk.Label(self, text="User Panel", font=("Arial", 20))
        title.pack(pady=10)
        
        # Available cars Treeview
        self.tree = ttk.Treeview(self, columns=("Inventory ID", "Car Name", "Model", "Year", "License", "Price/Day"),
                                 show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="View Car Specs", command=self.view_specs).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Rent Car", command=self.rent_car).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Return Car", command=self.return_car).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Transaction Log", command=self.view_transactions).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_available).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="Logout",
                   command=lambda: self.controller.show_frame("StartPage")).grid(row=0, column=5, padx=5)
        
        self.load_available()
    
    def set_user_details(self, user_id):
        self.user_id = user_id
        self.load_available()
    
    def load_available(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        query = """
            SELECT ci.inventoryID, c.carName, c.carModel, c.carModelYear, c.carLicensePlate, ci.pricePerDay
            FROM carInventory ci
            JOIN cars c ON ci.carID = c.carID
            WHERE ci.isAvailable = 1
        """
        try:
            self.controller.cursor.execute(query)
            for row in self.controller.cursor.fetchall():
                self.tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
    
    def view_specs(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a Car", "Please select a car first.")
            return
        inventoryID = self.tree.item(selected[0])['values'][0]
        try:
            self.controller.cursor.execute("SELECT horsepower, seatingCapacity, fuelEfficiency FROM carSpecs WHERE inventoryID = %s", (inventoryID,))
            result = self.controller.cursor.fetchone()
            if result:
                horsepower, seating, fuel = result
                messagebox.showinfo("Car Specs", f"Horsepower: {horsepower}\nSeating Capacity: {seating}\nFuel Efficiency: {fuel}")
            else:
                messagebox.showinfo("Car Specs", "No specs found for this car.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
    
    def rent_car(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a Car", "Please select a car to rent.")
            return
        inventoryID = self.tree.item(selected[0])['values'][0]
        
        rent_win = tk.Toplevel(self)
        rent_win.title("Rent Car")
        ttk.Label(rent_win, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(rent_win, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(rent_win, text="Insurance Type (basic, standard, premium):").grid(row=2, column=0, padx=5, pady=5)
        start_entry = ttk.Entry(rent_win)
        end_entry = ttk.Entry(rent_win)
        insurance_entry = ttk.Entry(rent_win)
        start_entry.grid(row=0, column=1, padx=5, pady=5)
        end_entry.grid(row=1, column=1, padx=5, pady=5)
        insurance_entry.grid(row=2, column=1, padx=5, pady=5)

        def confirm_rent():
            try:
                rentDate = datetime.strptime(start_entry.get(), "%Y-%m-%d").date()
                returnDate = datetime.strptime(end_entry.get(), "%Y-%m-%d").date()
                insuranceType = insurance_entry.get().lower()
                if insuranceType not in ['basic', 'standard', 'premium']:
                    messagebox.showerror("Invalid Insurance", "Choose: basic, standard, or premium")
                    return
                days = (returnDate - rentDate).days
                if days <= 0:
                    messagebox.showerror("Invalid Date", "Return date must be after rent date.")
                    return

                self.controller.cursor.execute("SELECT pricePerDay FROM carInventory WHERE inventoryID = %s", (inventoryID,))
                price = self.controller.cursor.fetchone()[0]
                insuranceRate = {"basic": 10, "standard": 20, "premium": 30}[insuranceType]
                rentalCost = days * price
                insuranceCost = days * insuranceRate

                query = """
                    INSERT INTO rentedCars (renterID, inventoryID, rentDate, returnDate, insuranceType, insuranceCost, rentalCost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.controller.cursor.execute(query,
                                               (self.user_id, inventoryID, rentDate, returnDate, insuranceType, insuranceCost, rentalCost))
                self.controller.cursor.execute("UPDATE carInventory SET isAvailable = 0 WHERE inventoryID = %s", (inventoryID,))
                self.controller.conn.commit()
                messagebox.showinfo("Success", "Car rented successfully!")
                rent_win.destroy()
                self.load_available()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(rent_win, text="Confirm", command=confirm_rent).grid(row=3, column=0, columnspan=2, pady=10)
    
    def return_car(self):
        return_win = tk.Toplevel(self)
        return_win.title("Return Car")
        tree = ttk.Treeview(return_win, columns=("Rental ID", "Car", "Model", "Year", "Total Cost"), show='headings')
        for col in tree['columns']:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        query = """
            SELECT r.rentalID, c.carName, c.carModel, c.carModelYear, (r.rentalCost + r.insuranceCost)
            FROM rentedCars r
            JOIN carInventory ci ON r.inventoryID = ci.inventoryID
            JOIN cars c ON ci.carID = c.carID
            WHERE r.renterID = %s AND ci.isAvailable = 0
        """
        try:
            self.controller.cursor.execute(query, (self.user_id,))
            for row in self.controller.cursor.fetchall():
                tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        
        def confirm_return():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Rental", "Please select a rental to return.")
                return
            rentalID = tree.item(selected[0])['values'][0]
            try:
                self.controller.cursor.execute("SELECT inventoryID FROM rentedCars WHERE rentalID = %s", (rentalID,))
                inventoryID = self.controller.cursor.fetchone()[0]
                self.controller.cursor.execute("UPDATE rentedCars SET returnDate = CURDATE() WHERE rentalID = %s", (rentalID,))
                self.controller.cursor.execute("UPDATE carInventory SET isAvailable = 1 WHERE inventoryID = %s", (inventoryID,))
                self.controller.cursor.execute("INSERT INTO transactions (rentalID) VALUES (%s)", (rentalID,))
                self.controller.conn.commit()
                messagebox.showinfo("Returned", "Car returned and transaction logged.")
                return_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(return_win, text="Confirm Return", command=confirm_return).pack(pady=10)
    
    def view_transactions(self):
        trans_win = tk.Toplevel(self)
        trans_win.title("Transaction Log")
        tree = ttk.Treeview(trans_win, columns=("Transaction ID", "Date", "Car", "Model", "Year", "Total Paid"), show='headings')
        for col in tree['columns']:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        query = """
            SELECT t.transactionID, t.transactionDate, c.carName, c.carModel, c.carModelYear,
                   (r.rentalCost + r.insuranceCost) AS totalPaid
            FROM transactions t
            JOIN rentedCars r ON t.rentalID = r.rentalID
            JOIN carInventory ci ON r.inventoryID = ci.inventoryID
            JOIN cars c ON ci.carID = c.carID
            WHERE r.renterID = %s
            ORDER BY t.transactionDate DESC
        """
        try:
            self.controller.cursor.execute(query, (self.user_id,))
            for row in self.controller.cursor.fetchall():
                tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

# ------------------ Run the Application ------------------
if __name__ == "__main__":
    app = CarRentalApp()
    app.mainloop()

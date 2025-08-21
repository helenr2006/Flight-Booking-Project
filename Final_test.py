import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import datetime

# مسیر فایل CSV
csv_file_path = "E:/Razie/Uni/Second_semester/AP/Final_Project/users.csv"

def load_csv(filename): # باز کردن فایل csv
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
    return data

# === تابع جدید برای رزرو پرواز ===
def reserve_flight(username, flight_id):
    """ذخیره رزرو در فایل CSV"""
    try:
        # بررسی آیا قبلاً رزرو شده
        reservations = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/reservation.csv')
        if any(row for row in reservations if row and row[0] == username and row[1] == flight_id):
            messagebox.showinfo("Info", "You have already reserved this flight")
            return False

        # بررسی ظرفیت پرواز
        flights = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv')
        flight = next((f for f in flights[1:] if f and f[0] == flight_id), None)
        if not flight:
            messagebox.showerror("Error", "Flight not found")
            return False
        if int(flight[5]) <= 0:
            messagebox.showerror("Error", "No seats available")
            return False

        # ذخیره رزرو
        with open('E:/Razie/Uni/Second_semester/AP/Final_Project/reservation.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, flight_id])
        
        # کاهش ظرفیت و ذخیره
        flight[5] = str(int(flight[5]) - 1)
        with open('E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(flights)
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to reserve flight: {e}")
        return False

# === تابع‌های پنل‌ها ===
def open_passenger_panel():
    username = username_entry.get()
    new_win = tk.Toplevel(window)
    new_win.title("Passenger Panel")
    csv_data = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv')
    csv_data_2 = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/reservation.csv')
    tk.Label(new_win, text="Welcome, Passenger!").pack()
    tk.Button(new_win , text= "Search Flights" , command=search_flights).pack(pady=10)
    # نمایش پروازها با قابلیت رزرو
    def show_flights_with_reserve():
        top = tk.Toplevel(new_win)
        top.title("Available Flights")
        
        columns = csv_data[0] + ['Action']
        tree = ttk.Treeview(top, columns=columns, show='headings')
        tree.pack(fill=tk.BOTH, expand=True)
        
        for col in csv_data[0]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.heading('Action', text='Action')
        tree.column('Action', width=100)
        
        for row in csv_data[1:]:
            if not row: continue
            flight_id = row[0]
            reserved = any(r for r in csv_data_2 if r and r[0] == username and r[1] == flight_id)
            action = "Booked" if reserved else "Reserve"
            tree.insert('', tk.END, values=row + [action], tags=('clickable',))
        
        tree.tag_configure('clickable', foreground='blue')
        
        def on_click(event):
            region = tree.identify("region", event.x, event.y)
            if region != "cell": return
            
            col = tree.identify_column(event.x)
            if col != f'#{len(csv_data[0])+1}': return
            
            item = tree.identify_row(event.y)
            values = tree.item(item, 'values')
            flight_id = values[0]
            
            if reserve_flight(username, flight_id):
                tree.item(item, values=values[:-1] + ["Booked"])
        
        tree.bind('<ButtonRelease-1>', on_click)
    
    button = tk.Button(new_win, text="Available Flights", command=show_flights_with_reserve)
    button.pack()
    
    button = tk.Button(new_win, text="My Reservations", command=lambda:reservations_list(csv_data_2, username))
    button.pack()

# بقیه توابع بدون تغییر باقی می‌مانند (open_admin_panel, flight_list, reservations_list, open_signup_form, login)
def open_admin_panel():
    new_win = tk.Toplevel(window)
    new_win.title("Admin Panel")
    file_path = 'E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv'
    csv_data = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv')
    tk.Label(new_win, text="Welcome, Flight Manager!").pack(pady = 10)
    button = tk.Button(new_win, text="flights list", command=lambda:(flight_list(csv_data)))
    button.pack()
    
    add_fields = ['Flight ID' , 'From' , 'To' , 'Date' , 'Time' ,'Capacity']
    add_entries = []

    for field in add_fields:
        tk.Label(new_win , text=field).pack()
        entry = tk.Entry(new_win)
        entry.pack()
        add_entries.append(entry)

    def add_flight():
        new_flight = [entry.get() for entry in add_entries]
        print("New flight to be added : " , new_flight)
        if all(new_flight):
            try:
                with open(file_path , mode='a' , newline='' , encoding='utf-8') as file :
                    writer = csv.writer(file)
                    writer.writerow(new_flight)

                    messagebox.showinfo("Success" , "Flight added successfully!")
                for entry in add_entries:
                    entry.delete(0 , tk.END)
            except Exception as e:
                messagebox.showerror("Error" , f"Failed add flight : {e}")
        else:
            messagebox.showerror("Error" , "All fields must be filled.")            

    tk.Button(new_win , text="Add flight" , command=add_flight).pack(pady=10)

    tk.Label(new_win, text="Delete Flight by ID").pack(pady=10) 
    delete_id_entry = tk.Entry(new_win)
    delete_id_entry.pack()

    def delete_flight():
            flight_id = delete_id_entry.get()
            if not flight_id:
                messagebox.showwarning("Warning", "Please enter Flight ID.")
                return
            try:
                csv_data = load_csv(file_path)
                updated_data = [csv_data[0]]
                deleted = False

                for row in csv_data[1:]:
                    if row[0] != flight_id:
                        updated_data.append(row)
                    else:
                        deleted = True
                if deleted:
                    with open(file_path , mode='w' , newline='' , encoding='utf=8') as file :
                        writer = csv.writer(file)
                        writer.writerows(updated_data)
                    messagebox.showinfo("Success" , f"Flight with ID '{flight_id}' deleted.")
                    delete_id_entry.delete(0 , tk.END)
                else:
                    messagebox.showerror("Error" , f"No flight with ID '{flight_id}' found.") 
            except Exception as e :
                messagebox.showerror("Error" , f"Failed to delete flight : {e}")
    tk.Button(new_win , text="Delete Flight" , command= delete_flight).pack(pady=5)
    

    

def flight_list(data):
    top = tk.Toplevel()  # create a new window on top of the main one
    top.title("Flights Data")

    columns = data[0]  # header row: ['flight_id', 'origin', 'destination', 'date', 'time', 'capacity']
    tree = ttk.Treeview(top, columns=columns, show='headings')
    tree.pack(fill=tk.BOTH, expand=True)

    # Configure columns and headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Insert rows (skip header)
    for row in data[1:]:
        tree.insert('', tk.END, values=row)

def reservations_list(data, username, parent=None):
    try:
        top = tk.Toplevel(parent) if parent else tk.Toplevel()
        top.title("Reservations List")  # More accurate title
        
        # Check if data is empty or None
        if not data or len(data) < 1:
            tk.Label(top, text="No data available").pack(pady=10)
            return
            
        columns = data[0]  # ['username', 'flight_id']
        
        # Handle case where entered_username is empty/None
        if not username:
            tk.Label(top, text="No username provided").pack(pady=10)
            return
            
        filtered_rows = [row for row in data[1:] if len(row) > 0 and row[0].lower() == username.lower()]

        if not filtered_rows:
            tk.Label(top, text=f"No reservations found for username: {username}").pack(pady=10)
            return
            
        tree = ttk.Treeview(top, columns=columns, show='headings')
        tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in filtered_rows:
            tree.insert('', tk.END, values=row)
            
    except Exception as e:
        # Provide error feedback if something goes wrong
        error_window = tk.Toplevel(top if 'top' in locals() else None)
        tk.Label(error_window, text=f"An error occurred: {str(e)}").pack(pady=10)


# === فرم ثبت‌نام ===
def open_signup_form():
    signup_win = tk.Toplevel(window)
    signup_win.title("Sign Up")

    tk.Label(signup_win, text="New Username:").pack()
    new_username = tk.Entry(signup_win)
    new_username.pack()

    tk.Label(signup_win, text="New Password:").pack()
    new_password = tk.Entry(signup_win, show="*")
    new_password.pack()

    tk.Label(signup_win, text="Select Role:").pack()
    role_var = tk.StringVar()

    tk.Radiobutton(signup_win, text="Passenger", variable=role_var, value="passenger").pack()
    tk.Radiobutton(signup_win, text="Flight Manager", variable=role_var, value="admin").pack()

    def register():
        username = new_username.get()
        password = new_password.get()
        role = role_var.get()

        if not username or not password:
            messagebox.showwarning("Error", "نام کاربری و رمز عبور نمی‌تواند خالی باشد")
            return
        if not role:
            messagebox.showwarning("Error", "لطفاً نقش خود را انتخاب کنید.")
            return

        # بررسی تکراری نبودن کاربر
        if os.path.exists(csv_file_path):
            with open(csv_file_path, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == username:
                        messagebox.showwarning("Error", "این نام کاربری قبلاً ثبت شده")
                        return

        # نوشتن اطلاعات در فایل CSV
        with open(csv_file_path, mode="a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password, role])
            messagebox.showinfo("Success", "ثبت‌نام با موفقیت انجام شد")
            signup_win.destroy()

    tk.Button(signup_win, text="Register", command=register).pack(pady=10)

# === تابع ورود ===
def login():
    entered_username = username_entry.get()
    entered_password = password_entry.get()
    found = False

    if not os.path.exists(csv_file_path):
        messagebox.showinfo("Not Found", "کاربر یافت نشد. لطفا ثبت نام کنید.")
        open_signup_form()
        return

    with open(csv_file_path, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == entered_username and row[1] == entered_password:
                found = True
                role = row[2]
                if role == "passenger":
                    open_passenger_panel()
                elif role == "admin":
                    open_admin_panel()
                break

    if not found:
        messagebox.showinfo("Not Found", "کاربر یافت نشد. لطفا ثبت نام کنید.")
        open_signup_form()


# === ساختار گرافیکی اصلی ===
window = tk.Tk()
window.title("Airlines")
window.geometry("1080x720")

label1 = tk.Label(window, text="Persian Airlines.com", font=("Arial", 16))
label1.pack(pady=10)

username = tk.Label(window, text="Username")
username.pack()
username_entry = tk.Entry(window)
username_entry.pack()

password = tk.Label(window, text="Password")
password.pack()
password_entry = tk.Entry(window, show="*")
password_entry.pack()

submit_button = tk.Button(window, text="Submit", command=login)
submit_button.pack(pady=10)

def search_flights():
    search_win = tk.Toplevel(window)
    search_win.title("Search Flights")

    tk.Label(search_win , text="From:").pack()
    from_entry = tk.Entry(search_win)
    from_entry.pack()

    tk.Label(search_win , text="To:").pack()
    to_entry = tk.Entry(search_win)
    to_entry.pack()

    tk.Label(search_win , text="Date (YYYY-MM-DD):").pack()
    date_entry = tk.Entry(search_win)
    date_entry.pack()

    def do_search():
        origin = from_entry.get().strip().lower()
        destination = to_entry.get().strip().lower()
        date = date_entry.get().strip()
        
        conditions = []
        if origin:
            conditions.append("مبدا")
        if destination:
            conditions.append("مقصد")
        if date :
            conditions.append("تاریخ") 

        if not conditions:
            messagebox.showwarning("Error" , "Please fill at least one field")
            return
        try:
            flights = load_csv("E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv") 
            headers = flights[0]
            matched = [headers]

            for row in flights[1:]:
                row_origin = row[1].strip().lower()
                row_destination =row[2].strip().lower()
                row_date = row[3].strip()

                match = True
                if origin and origin != row_origin:
                    match = False
                if destination and destination != row_destination:
                    match = False
                if date and date != row_date :
                    match = False

                if match:
                    matched.append(row)

            if len(matched) > 1:
                condition_text = ",".join(conditions)
                messagebox.showinfo("جسنجو انجام شد" , f" پرواز ها بر اساس {condition_text} یافت شدند.")
                flight_list(matched)

            else:
                messagebox.showinfo("هیچ پروازی با شرایط وارد شده پیدا نشد" , "نتیجه ایی یافت  نشد.")
        except Exception as e :
            messagebox.showerror("خطا" , f"خطا در جستجو:{str(e)}")

    tk.Button(search_win , text="Search" , command=do_search) .pack(pady=10)                                                  
            

window.mainloop()

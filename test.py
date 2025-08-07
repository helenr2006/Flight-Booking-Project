import tkinter as tk  # ساختن رابط کاربری گرافیکی
from tkinter import ttk
from tkinter import messagebox  # نمایش پیام های خطا و ورود کاربر
import csv  # برای خواندن و نوشتن در فایل csv
import os  # برای ارتباط با فایل users.csv
import datetime # برای استفاده از زمان 

# مسیر فایل CSV
csv_file_path = "E:/Razie/Uni/Second_semester/AP/Final_Project/users.csv"

def load_csv(filename): # باز کردن فایل csv
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
    return data

# === تابع‌های پنل‌ها ===
def open_passenger_panel():
    new_win = tk.Toplevel(window)
    new_win.title("Passenger Panel")
    csv_data = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv')
    csv_data_2 = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/reservation.csv')
    tk.Label(new_win, text="Welcome, Passenger!").pack()
    button = tk.Button(new_win, text="flights list", command=lambda:(flight_list(csv_data)))
    button.pack()
    button = tk.Button(new_win, text="Reservations", command=lambda:reservations_list(csv_data_2,username))
    button.pack()
    

def open_admin_panel(): 
    new_win = tk.Toplevel(window)
    new_win.title("Admin Panel")
    tk.Label(new_win, text="Welcome, Flight Manager!").pack()
    csv_data = load_csv('E:/Razie/Uni/Second_semester/AP/Final_Project/flights.csv')
    button = tk.Button(new_win, text="flights list", command=lambda:(flight_list(csv_data)))
    button.pack()
    

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
    top = tk.Toplevel(parent) if parent else tk.Toplevel()
    top.title("Flights Data")

    columns = data[0]  # ['username', 'flight_id']

    filtered_rows = [row for row in data[1:] if len(row) > 0 and row[0].lower() == username.lower()]

    tree = ttk.Treeview(top, columns=columns, show='headings')
    tree.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for row in filtered_rows:
        tree.insert('', tk.END, values=row)

    if not filtered_rows:
        tk.Label(top, text=f"No reservations found for username: {username}").pack(pady=10)



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

label1 = tk.Label(window, text="Persion Airlines.com", font=("Arial", 16))
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

window.mainloop()
# testing
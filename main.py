#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Features:
- Login / Signup (roles: passenger, admin)
- Passenger panel: list flights, reserve flight, view own reservations
- Admin panel: list/add/delete flights
- CSV datastore with automatic file creation (headers included)
- Cross‑platform paths (pathlib) — files created next to this script
- Live date/time header (updates each second)
- ttk widgets + simple style

CSV files (auto-created if not exist):
- users.csv: username,password,role  (password stored as plain for simplicity)
- flights.csv: id,origin,destination,date,time,capacity
- reservations.csv: username,flight_id,timestamp
"""
from __future__ import annotations # نگه داشتن تایپ ها به صورت string
import tkinter as tk # ساختن رابط کاربری گرافیکی
from tkinter import ttk, messagebox # نمایش پیام های خطا و ورود کاربر
from pathlib import Path #برای قابل اجرا کردن برنامه در هرجا
import csv  # برای خواندن و نوشتن در فایل csv
from datetime import datetime # برای استفاده از زمان

APP_TITLE = "Airlines"

# ---------------------- Data Layer ----------------------
# این کلاس مسئول مدیریت مسیر فایل‌های داده‌ای (CSV) است
# مسیر فایل‌ها تنظیم می‌گردد.
# اطمینان حاصل می‌شود که فایل‌ها موجودند (یا ساخته می‌شوند)
class DataStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.users = base_dir / "users.csv"
        self.flights = base_dir / "flights.csv"
        self.reservations = base_dir / "reservations.csv"
        self._ensure_files()

    def _ensure_files(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if not self.users.exists():
            self._write_rows(self.users, [["username", "password", "role"]])
        if not self.flights.exists():
            self._write_rows(self.flights, [["id", "origin", "destination", "date", "time", "capacity"]])
        if not self.reservations.exists():
            self._write_rows(self.reservations, [["username", "flight_id", "timestamp"]])

    # --- helpers ---
    # این تابع پس از خواندن فایل CSV یک لیست از ردیف‌ها (هر ردیف خودش یک لیست از رشته‌ها است) می سازد
    def _read_rows(self, path: Path) -> list[list[str]]:
        with path.open(newline='', encoding='utf-8') as f:
            return list(csv.reader(f))
    #بازنویسی کامل یک فایل CSV (مثلا وقتی بخواهی همه‌ی داده‌ها را ذخیره کنی بعد از تغییرات)
    def _write_rows(self, path: Path, rows: list[list[str]]):
        with path.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerows(rows)
    #زمانی که بخواهی فقط یک کاربر/پرواز/رزرو جدید اضافه کنی، بدون دست زدن به بقیه داده‌ها
    def _append_row(self, path: Path, row: list[str]):
        with path.open('a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(row)

    # --- users ---
    # این تابع کاربران راجست و جو میکند
    def find_user(self, username: str) -> tuple[str, str, str] | None:
        rows = self._read_rows(self.users)
        for r in rows[1:]:
            if len(r) >= 3 and r[0] == username:
                return tuple(r[:3])  # username, password, role
        return None
    #این تابع کاربران را اضافه میکند
    def add_user(self, username: str, password: str, role: str) -> bool:
        if self.find_user(username):
            return False
        self._append_row(self.users, [username, password, role])
        return True

    # --- flights ---
    #پرواز ها به صورت رشته از فایل برمیگرداند
    def list_flights(self) -> list[list[str]]:
        return self._read_rows(self.flights)
    #پرواز اضافه میکند
    def add_flight(self, fid: str, origin: str, dest: str, date: str, time_: str, capacity: str) -> None:
        self._append_row(self.flights, [fid, origin, dest, date, time_, capacity])
    #پرواز های موجود را پاک میکند
    def delete_flight(self, fid: str) -> bool:
        rows = self._read_rows(self.flights)
        header, body = rows[0], rows[1:]
        new_body = [r for r in body if r and r[0] != fid]
        if len(new_body) == len(body):
            return False
        self._write_rows(self.flights, [header] + new_body)
        return True

    # --- reservations ---
    #رزرو هارا به صورت رشته برمیگرداند
    def list_reservations(self) -> list[list[str]]:
        return self._read_rows(self.reservations)

    def list_user_reservations(self, username: str) -> list[list[str]]:
        rows = self._read_rows(self.reservations)
        return [r for r in rows if r and (r[0] == username or r[0] == 'username')]
    #تعداد رزرو های یک پرواز را میشمارد
    def count_reservations_for_flight(self, fid: str) -> int:
        rows = self._read_rows(self.reservations)
        return sum(1 for r in rows[1:] if r and r[1] == fid)
    #پیدا کردن پرواز ها بر اساس ID
    def get_flight_by_id(self, fid: str) -> list[str] | None:
        rows = self._read_rows(self.flights)
        for r in rows[1:]:
            if r and r[0] == fid:
                return r
        return None
    # پروازی را رزرو میکند
    def add_reservation(self, username: str, fid: str) -> tuple[bool, str]:
        flight = self.get_flight_by_id(fid)
        if not flight:
            return False, "Flight not found."
        # ظرفیت را بررسی میکند
        try:
            cap = int(flight[5])
        except Exception:
            return False, "Invalid flight capacity."
        taken = self.count_reservations_for_flight(fid)
        if taken >= cap:
            return False, "This flight is full."
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._append_row(self.reservations, [username, fid, ts])
        return True, "Reservation completed."


# ---------------------- UI Layer ----------------------
#از کتابخانه Tkinter برای ساخت رابط کاربری (GUI) استفاده می‌کند.
class AirlinesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x640")
        self.minsize(900, 560)

        # data store next to script file
        base = Path(__file__).resolve().parent
        self.store = DataStore(base)

        self.style = ttk.Style(self)
        self._setup_style()

        self._build_header()
        self.container = ttk.Frame(self, padding=16)
        self.container.pack(fill='both', expand=True)

        self.frames = {}
        for F in (LoginFrame, PassengerFrame, AdminFrame):
            frame = F(parent=self.container, app=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.show("LoginFrame")
        self._tick_clock()
    #وظیفه‌ی تنظیم ظاهر و استایل ویجت‌های ttk (تم‌های Tkinter) را دارد.
    def _setup_style(self):
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            pass
        self.style.configure('TButton', padding=8)
        self.style.configure('TEntry', padding=4)
        self.style.configure('Card.TFrame', relief='flat', borderwidth=0)
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'))
        self.style.configure('Hint.TLabel', foreground='#6b7280')
    #وظیفه‌ی ساختن سربرگ (Header) بالای پنجره برنامه رو داره.
    def _build_header(self):
        top = ttk.Frame(self, padding=(16, 12))
        top.pack(fill='x')
        ttk.Label(top, text="✈ Airlines System", style='Header.TLabel').pack(side='left')
        self.clock_lbl = ttk.Label(top, text="--:--:--", style='Hint.TLabel')
        self.clock_lbl.pack(side='right')
    #این تابع کارش نمایش و به‌روز کردن ساعت زنده در بالای برنامه است.
    def _tick_clock(self):
        now = datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
        self.clock_lbl.config(text=now)
        self.after(1000, self._tick_clock)
    #این متد مسئول نمایش یک صفحه (Frame) از بین فریم‌های مختلف برنامه است.
    def show(self, name: str):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()


# ---------------------- Frames ----------------------
# فرم ساخته شده برای login
class LoginFrame(ttk.Frame):
    def __init__(self, parent, app: AirlinesApp):
        super().__init__(parent, padding=24)
        self.app = app

        card = ttk.Frame(self, style='Card.TFrame', padding=20)
        card.pack(expand=True)

        ttk.Label(card, text="ورود به سامانه", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 12))
        ttk.Label(card, text="Username:").grid(row=1, column=0, sticky='e', padx=(0,6), pady=6)
        ttk.Label(card, text="Password:").grid(row=2, column=0, sticky='e', padx=(0,6), pady=6)

        self.username = ttk.Entry(card, width=28)
        self.password = ttk.Entry(card, width=28, show='*')
        self.username.grid(row=1, column=1, pady=6)
        self.password.grid(row=2, column=1, pady=6)

        btns = ttk.Frame(card)
        btns.grid(row=3, column=0, columnspan=2, pady=12)
        ttk.Button(btns, text="Login", command=self.login).pack(side='left')
        ttk.Button(btns, text="Sign up", command=self.signup_dialog).pack(side='left', padx=8)

        self.info = ttk.Label(card, text="نکته: فایل‌های CSV کنار اسکریپت ذخیره می‌شوند.", style='Hint.TLabel')
        self.info.grid(row=4, column=0, columnspan=2, pady=(6,0))

    def login(self):
        u, p = self.username.get().strip(), self.password.get().strip()
        rec = self.app.store.find_user(u)
        if not rec or rec[1] != p:
            messagebox.showerror("Login failed", "نام کاربری یا گذرواژه نادرست است.")
            return
        role = rec[2]
        if role == 'admin':
            self.app.frames['AdminFrame'].current_user = u
            self.app.show('AdminFrame')
        else:
            self.app.frames['PassengerFrame'].current_user = u
            self.app.show('PassengerFrame')

    def signup_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Sign up")
        dlg.transient(self)
        dlg.grab_set()
        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill='both', expand=True)
        ttk.Label(frm, text="ثبت‌نام", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0,12))
        ttk.Label(frm, text="Username:").grid(row=1, column=0, sticky='e', padx=(0,6), pady=6)
        ttk.Label(frm, text="Password:").grid(row=2, column=0, sticky='e', padx=(0,6), pady=6)
        ttk.Label(frm, text="Role:").grid(row=3, column=0, sticky='e', padx=(0,6), pady=6)

        u = ttk.Entry(frm, width=28)
        p = ttk.Entry(frm, width=28, show='*')
        role = ttk.Combobox(frm, values=['passenger', 'admin'], state='readonly', width=25)
        role.current(0)
        u.grid(row=1, column=1, pady=6)
        p.grid(row=2, column=1, pady=6)
        role.grid(row=3, column=1, pady=6)

        def do_signup():
            if not u.get().strip() or not p.get().strip():
                messagebox.showwarning("خطا", "تمام فیلدها را پر کنید.")
                return
            ok = self.app.store.add_user(u.get().strip(), p.get().strip(), role.get())
            if not ok:
                messagebox.showwarning("خطا", "این نام کاربری وجود دارد.")
                return
            messagebox.showinfo("موفق", "ثبت‌نام انجام شد. اکنون وارد شوید.")
            dlg.destroy()

        ttk.Button(frm, text="ایجاد حساب", command=do_signup).grid(row=4, column=0, columnspan=2, pady=12)


class PassengerFrame(ttk.Frame):
    def __init__(self, parent, app: AirlinesApp):
        super().__init__(parent, padding=16)
        self.app = app
        self.current_user: str | None = None

        header = ttk.Frame(self)
        header.pack(fill='x')
        ttk.Label(header, text="پنل مسافر", style='Header.TLabel').pack(side='left')
        ttk.Button(header, text="خروج", command=lambda: app.show('LoginFrame')).pack(side='right')

        body = ttk.Frame(self)
        body.pack(fill='both', expand=True, pady=(10,0))

        # left: flights list
        flights_card = ttk.Labelframe(body, text="لیست پروازها", padding=12)
        flights_card.pack(side='left', fill='both', expand=True, padx=(0,8))

        self.flights_tv = ttk.Treeview(flights_card, columns=("id","origin","destination","date","time","capacity"), show='headings', height=12)
        for c in ("id","origin","destination","date","time","capacity"):
            self.flights_tv.heading(c, text=c)
            self.flights_tv.column(c, width=100)
        self.flights_tv.pack(fill='both', expand=True)

        reserve_bar = ttk.Frame(flights_card)
        reserve_bar.pack(fill='x', pady=(8,0))
        ttk.Label(reserve_bar, text="Flight ID:").pack(side='left')
        self.reserve_id = ttk.Entry(reserve_bar, width=12)
        self.reserve_id.pack(side='left', padx=6)
        ttk.Button(reserve_bar, text="رزرو", command=self.reserve).pack(side='left')

        # right: my reservations
        my_card = ttk.Labelframe(body, text="رزروهای من", padding=12)
        my_card.pack(side='left', fill='both', expand=True, padx=(8,0))
        self.my_tv = ttk.Treeview(my_card, columns=("username","flight_id","timestamp"), show='headings', height=12)
        for c in ("username","flight_id","timestamp"):
            self.my_tv.heading(c, text=c)
            self.my_tv.column(c, width=120)
        self.my_tv.pack(fill='both', expand=True)

    def on_show(self):
        self._refresh_flights()
        self._refresh_my_reservations()

    def _refresh_flights(self):
        for i in self.flights_tv.get_children():
            self.flights_tv.delete(i)
        rows = self.app.store.list_flights()
        for r in rows[1:]:
            self.flights_tv.insert('', 'end', values=r)

    def _refresh_my_reservations(self):
        for i in self.my_tv.get_children():
            self.my_tv.delete(i)
        if not self.current_user:
            return
        rows = self.app.store.list_user_reservations(self.current_user)
        for r in rows[1:]:
            self.my_tv.insert('', 'end', values=r)

    def reserve(self):
        fid = self.reserve_id.get().strip()
        if not fid:
            messagebox.showwarning("خطا", "کد پرواز را وارد کنید.")
            return
        ok, msg = self.app.store.add_reservation(self.current_user, fid)
        if ok:
            messagebox.showinfo("موفق", msg)
            self._refresh_my_reservations()
        else:
            messagebox.showerror("ناموفق", msg)


class AdminFrame(ttk.Frame):
    def __init__(self, parent, app: AirlinesApp):
        super().__init__(parent, padding=16)
        self.app = app
        self.current_user: str | None = None

        header = ttk.Frame(self)
        header.pack(fill='x')
        ttk.Label(header, text="پنل مدیر پرواز", style='Header.TLabel').pack(side='left')
        ttk.Button(header, text="خروج", command=lambda: app.show('LoginFrame')).pack(side='right')

        body = ttk.Frame(self)
        body.pack(fill='both', expand=True, pady=(10,0))

        # left: flights
        left = ttk.Frame(body)
        left.pack(side='left', fill='both', expand=True, padx=(0,8))

        flights_card = ttk.Labelframe(left, text="لیست پروازها", padding=12)
        flights_card.pack(fill='both', expand=True)

        self.tv = ttk.Treeview(flights_card, columns=("id","origin","destination","date","time","capacity"), show='headings', height=14)
        for c in ("id","origin","destination","date","time","capacity"):
            self.tv.heading(c, text=c)
            self.tv.column(c, width=100)
        self.tv.pack(fill='both', expand=True)

        ttk.Button(flights_card, text="بازخوانی", command=self.refresh).pack(pady=8)

        # right: add/delete
        right = ttk.Labelframe(body, text="افزودن / حذف پرواز", padding=12)
        right.pack(side='left', fill='y', padx=(8,0))

        self.e_id = ttk.Entry(right); self._l(right, "ID:").grid(row=0, column=0, sticky='e'); self.e_id.grid(row=0, column=1, pady=4, padx=6)
        self.e_o = ttk.Entry(right); self._l(right, "From:").grid(row=1, column=0, sticky='e'); self.e_o.grid(row=1, column=1, pady=4, padx=6)
        self.e_d = ttk.Entry(right); self._l(right, "To:").grid(row=2, column=0, sticky='e'); self.e_d.grid(row=2, column=1, pady=4, padx=6)
        self.e_date = ttk.Entry(right); self._l(right, "Date (YYYY-MM-DD):").grid(row=3, column=0, sticky='e'); self.e_date.grid(row=3, column=1, pady=4, padx=6)
        self.e_time = ttk.Entry(right); self._l(right, "Time (HH:MM):").grid(row=4, column=0, sticky='e'); self.e_time.grid(row=4, column=1, pady=4, padx=6)
        self.e_cap = ttk.Entry(right); self._l(right, "Capacity:").grid(row=5, column=0, sticky='e'); self.e_cap.grid(row=5, column=1, pady=4, padx=6)

        ttk.Button(right, text="افزودن پرواز", command=self.add).grid(row=6, column=0, columnspan=2, pady=(8,4))

        ttk.Separator(right, orient='horizontal').grid(row=7, column=0, columnspan=2, sticky='ew', pady=8)
        self.del_id = ttk.Entry(right)
        self._l(right, "Delete by ID:").grid(row=8, column=0, sticky='e')
        self.del_id.grid(row=8, column=1, padx=6, pady=4)
        ttk.Button(right, text="حذف", command=self.delete).grid(row=9, column=0, columnspan=2, pady=(4,0))

    def _l(self, parent, text):
        return ttk.Label(parent, text=text)

    def on_show(self):
        self.refresh()

    def refresh(self):
        for i in self.tv.get_children():
            self.tv.delete(i)
        rows = self.app.store.list_flights()
        for r in rows[1:]:
            self.tv.insert('', 'end', values=r)

    def add(self):
        fid = self.e_id.get().strip()
        origin = self.e_o.get().strip()
        dest = self.e_d.get().strip()
        date = self.e_date.get().strip()
        time_ = self.e_time.get().strip()
        cap = self.e_cap.get().strip()
        if not all([fid, origin, dest, date, time_, cap]):
            messagebox.showwarning("خطا", "همه فیلدها را پر کنید.")
            return
        # basic validations
        try:
            datetime.strptime(date, '%Y-%m-%d')
            datetime.strptime(time_, '%H:%M')
            _ = int(cap)
        except Exception:
            messagebox.showerror("خطا", "تاریخ/ساعت یا ظرفیت نامعتبر است.")
            return
        self.app.store.add_flight(fid, origin, dest, date, time_, cap)
        messagebox.showinfo("موفق", "پرواز اضافه شد.")
        self.refresh()

    def delete(self):
        fid = self.del_id.get().strip()
        if not fid:
            messagebox.showwarning("خطا", "شناسه پرواز را وارد کنید.")
            return
        ok = self.app.store.delete_flight(fid)
        if ok:
            messagebox.showinfo("موفق", "پرواز حذف شد.")
            self.refresh()
        else:
            messagebox.showerror("خطا", "پروازی با این شناسه یافت نشد.")


# ---------------------- Run ----------------------
if __name__ == '__main__':
    app = AirlinesApp()
    app.mainloop()

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import shutil
import getpass

# ---------- ฟังก์ชันการจัดการบัญชี ----------

def create_account(username, password):
    try:
        if username.strip() == "" or username == "ชื่อบัญชี":
            messagebox.showwarning("เตือน", "กรุณาใส่ชื่อบัญชีให้ถูกต้อง")
            return

        if not password.strip() or password == "รหัสผ่าน":
            password = ""

        subprocess.run(f'net user "{username}" "{password}" /add', shell=True, check=True)
        subprocess.run(f'net localgroup administrators "{username}" /add', shell=True, check=True)
        messagebox.showinfo("สำเร็จ", f"สร้างบัญชี {username} แล้วให้สิทธิ์แอดมิน")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("ผิดพลาด", str(e))

def is_logged_in_user(username):
    return username.strip().lower() == getpass.getuser().strip().lower()

def user_exists(username):
    result = subprocess.run(f'net user "{username}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def force_unlock_folder(path):
    try:
        subprocess.run(f'takeown /F "{path}" /R /D Y', shell=True, check=True)
        subprocess.run(f'icacls "{path}" /grant administrators:F /T', shell=True, check=True)
    except Exception as e:
        print("ปลดล็อกสิทธิ์ล้มเหลว:", e)

def ignore_errors(func, path, exc_info):
    import stat
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def delete_account(username):
    try:
        if not username.strip():
            messagebox.showwarning("เตือน", "ใส่ชื่อผู้ใช้ก่อนจะลบ")
            return

        if not user_exists(username):
            messagebox.showerror("ไม่พบบัญชี", f"ไม่มีบัญชีชื่อ '{username}' ในระบบ")
            return

        if is_logged_in_user(username):
            messagebox.showerror("ลบไม่ได้", "คุณพยายามลบบัญชีที่กำลังใช้อยู่!")
            return

        if not messagebox.askyesno("ยืนยันการลบ", f"แน่ใจว่าจะลบบัญชี '{username}' จริงใช่มั้ย?"):
            return

        subprocess.run(f'net user "{username}" /delete', shell=True, check=True)

        user_folder = os.path.join("C:\\Users", username)
        if os.path.exists(user_folder):
            try:
                force_unlock_folder(user_folder)
                shutil.rmtree(user_folder, onerror=ignore_errors)
                messagebox.showinfo("สำเร็จ", f"ลบบัญชีและโฟลเดอร์ {username} เรียบร้อยแล้ว")
            except Exception as e:
                messagebox.showerror("ลบโฟลเดอร์ไม่ได้", f"ล้มเหลว:\n{e}")
        else:
            messagebox.showinfo("ลบบัญชีแล้ว", f"ลบ user {username} แล้ว แต่ไม่เจอโฟลเดอร์ให้ลบ")
    except Exception as e:
        messagebox.showerror("ลบพัง", str(e))

def change_password(username, new_password):
    try:
        if not user_exists(username):
            messagebox.showerror("ไม่พบบัญชี", f"ไม่มีบัญชีชื่อ '{username}' ในระบบ")
            return

        subprocess.run(f'net user "{username}" "{new_password}"', shell=True, check=True)
        messagebox.showinfo("สำเร็จ", f"เปลี่ยนรหัสผ่านของ {username} แล้ว")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("ผิดพลาด", str(e))

def rename_user(old_name, new_name):
    try:
        if not user_exists(old_name):
            messagebox.showerror("ไม่พบบัญชี", f"ไม่มีบัญชีชื่อ '{old_name}'")
            return

        powershell_cmd = f'Rename-LocalUser -Name "{old_name}" -NewName "{new_name}"'
        subprocess.run(["powershell", "-Command", powershell_cmd], shell=True, check=True)
        messagebox.showinfo("สำเร็จ", f"เปลี่ยนชื่อ {old_name} เป็น {new_name} แล้ว")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("ผิดพลาด", f"เปลี่ยนชื่อไม่สำเร็จ:\n{str(e)}")

def install_thai_language():
    try:
        subprocess.run("lpksetup /i th-TH /r /s", shell=True, check=True)
        messagebox.showinfo("สำเร็จ", "ติดตั้งภาษาไทยแล้ว")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("ผิดพลาด", f"ติดตั้งไม่สำเร็จ:\n{e}")

# ---------- GUI ----------

app = tk.Tk()
app.title("User Manager")
app.geometry("300x250")

def clear_window():
    for widget in app.winfo_children():
        widget.destroy()

def show_main_menu():
    clear_window()
    app.configure(bg="#f0f0f0")

    title = tk.Label(app, text="เมนูหลัก", font=("Segoe UI", 16, "bold"), bg="#f0f0f0")
    title.pack(pady=(20, 10))

    grid_frame = tk.Frame(app, bg="#f0f0f0")
    grid_frame.pack()

    style_btn = {
        "width": 18,
        "height": 2,
        "font": ("Segoe UI", 10),
        "relief": "raised",
        "bd": 1,
        "bg": "#ffffff",
        "activebackground": "#e0e0e0",
    }

    tk.Button(grid_frame, text="สร้างบัญชี", command=show_create_user, **style_btn).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(grid_frame, text="ลบบัญชี", command=show_delete_user, **style_btn).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(grid_frame, text="เปลี่ยนชื่อ", command=show_rename_user, **style_btn).grid(row=1, column=0, padx=10, pady=5)
    tk.Button(grid_frame, text="เปลี่ยนรหัสผ่าน", command=show_change_password, **style_btn).grid(row=1, column=1, padx=10, pady=5)

    tk.Button(app, text="ติดตั้งภาษา", command=show_language_installer, **style_btn).pack(pady=(15, 10))

def show_create_user():
    clear_window()
    app.configure(bg="#f0f0f0")  # ให้พื้นหลังเหมือนหน้าเมนูหลัก

    # หัวข้อ
    tk.Label(app, text="สร้างบัญชีใหม่", font=("Segoe UI", 14, "bold"), bg="#f0f0f0").pack(pady=(15, 10))

    # กรอบสำหรับ input
    frame = tk.Frame(app, bg="#f0f0f0")
    frame.pack(pady=10)

    entry_style = {"width": 25, "font": ("Segoe UI", 10)}

    username = tk.Entry(frame, fg='grey', **entry_style)
    username.insert(0, "ชื่อบัญชี")
    username.pack(pady=5)

    def clear_username(e): 
        if username.get() == "ชื่อบัญชี":
            username.delete(0, tk.END); username.config(fg='black')
    def restore_username(e): 
        if username.get() == "":
            username.insert(0, "ชื่อบัญชี"); username.config(fg='grey')
    username.bind("<FocusIn>", clear_username)
    username.bind("<FocusOut>", restore_username)

    password = tk.Entry(frame, fg='grey', show='', **entry_style)
    password.insert(0, "รหัสผ่าน")
    password.pack(pady=5)

    def clear_password(e): 
        if password.get() == "รหัสผ่าน":
            password.delete(0, tk.END); password.config(fg='black', show='*')
    def restore_password(e): 
        if password.get() == "":
            password.insert(0, "รหัสผ่าน"); password.config(fg='grey', show='')
    password.bind("<FocusIn>", clear_password)
    password.bind("<FocusOut>", restore_password)

    btn_style = {
        "width": 12, "height": 1,
        "font": ("Segoe UI", 10),
        "bg": "#ffffff",
        "activebackground": "#e0e0e0",
        "relief": "raised", "bd": 1
    }

    tk.Button(app, text="สร้าง", command=lambda: create_account(username.get(), password.get()), **btn_style).pack(pady=(10, 5))
    tk.Button(app, text="กลับ", command=show_main_menu, **btn_style).pack()

def show_delete_user():
    clear_window()
    app.configure(bg="#f0f0f0")  # พื้นหลังเทาอ่อน

    tk.Label(app, text="ลบบัญชี", font=("Segoe UI", 14, "bold"), bg="#f0f0f0").pack(pady=(20, 10))

    frame = tk.Frame(app, bg="#f0f0f0")
    frame.pack(pady=10)

    entry_style = {"width": 25, "font": ("Segoe UI", 10)}

    username = tk.Entry(frame, fg='grey', **entry_style)
    username.insert(0, "บัญชีที่ต้องการลบ")
    username.pack(pady=5)

    def clear_username(e): 
        if username.get() == "บัญชีที่ต้องการลบ":
            username.delete(0, tk.END); username.config(fg='black')
    def restore_username(e): 
        if username.get() == "":
            username.insert(0, "บัญชีที่ต้องการลบ"); username.config(fg='grey')
    username.bind("<FocusIn>", clear_username)
    username.bind("<FocusOut>", restore_username)

    btn_style = {
        "width": 12, "height": 1,
        "font": ("Segoe UI", 10),
        "bg": "#ffffff",
        "activebackground": "#e0e0e0",
        "relief": "raised", "bd": 1
    }

    tk.Button(app, text="ลบ", command=lambda: delete_account(username.get()), **btn_style).pack(pady=(10, 5))
    tk.Button(app, text="กลับ", command=show_main_menu, **btn_style).pack()
        # คำเตือน
    warning = tk.Label(app, text="※ ต้อง Logout ออกจากบัญชีก่อนลบ", 
                       font=("Segoe UI", 10, "italic"), 
                       fg="red", bg="#f0f0f0")
    warning.pack(pady=(30, 10))



def show_change_password():
    clear_window()
    app.configure(bg="#f0f0f0")

    tk.Label(app, text="เปลี่ยนรหัสผ่าน", font=("Segoe UI", 14, "bold"), bg="#f0f0f0").pack(pady=(20, 10))

    frame = tk.Frame(app, bg="#f0f0f0")
    frame.pack(pady=10)

    entry_style = {"width": 25, "font": ("Segoe UI", 10)}

    username = tk.Entry(frame, fg='grey', **entry_style)
    username.insert(0, "ชื่อบัญชี")
    username.pack(pady=5)

    password = tk.Entry(frame, show='', fg='grey', **entry_style)
    password.insert(0, "รหัสผ่านใหม่")
    password.pack(pady=5)

    def clear_un(e):
        if username.get() == "ชื่อบัญชี":
            username.delete(0, tk.END); username.config(fg='black')
    def restore_un(e):
        if username.get() == "":
            username.insert(0, "ชื่อบัญชี"); username.config(fg='grey')

    def clear_pw(e):
        if password.get() == "รหัสผ่านใหม่":
            password.delete(0, tk.END); password.config(fg='black', show='*')
    def restore_pw(e):
        if password.get() == "":
            password.insert(0, "รหัสผ่านใหม่"); password.config(fg='grey', show='')

    username.bind("<FocusIn>", clear_un)
    username.bind("<FocusOut>", restore_un)
    password.bind("<FocusIn>", clear_pw)
    password.bind("<FocusOut>", restore_pw)

    btn_style = {
        "width": 12, "height": 1,
        "font": ("Segoe UI", 10),
        "bg": "#ffffff",
        "activebackground": "#e0e0e0",
        "relief": "raised", "bd": 1
    }

    tk.Button(app, text="เปลี่ยน", command=lambda: change_password(username.get(), password.get()), **btn_style).pack(pady=(10, 5))
    tk.Button(app, text="กลับ", command=show_main_menu, **btn_style).pack()


def show_rename_user():
    clear_window()
    app.configure(bg="#f0f0f0")

    tk.Label(app, text="เปลี่ยนชื่อบัญชี", font=("Segoe UI", 14, "bold"), bg="#f0f0f0").pack(pady=(20, 10))

    frame = tk.Frame(app, bg="#f0f0f0")
    frame.pack(pady=10)

    entry_style = {"width": 25, "font": ("Segoe UI", 10)}

    old = tk.Entry(frame, fg='grey', **entry_style)
    old.insert(0, "ชื่อบัญชีเดิม")
    old.pack(pady=5)

    new = tk.Entry(frame, fg='grey', **entry_style)
    new.insert(0, "ชื่อบัญชีใหม่")
    new.pack(pady=5)

    def clear_old(e): 
        if old.get() == "ชื่อบัญชีเดิม":
            old.delete(0, tk.END); old.config(fg='black')
    def restore_old(e): 
        if old.get() == "":
            old.insert(0, "ชื่อบัญชีเดิม"); old.config(fg='grey')
    def clear_new(e): 
        if new.get() == "ชื่อบัญชีใหม่":
            new.delete(0, tk.END); new.config(fg='black')
    def restore_new(e): 
        if new.get() == "":
            new.insert(0, "ชื่อบัญชีใหม่"); new.config(fg='grey')

    old.bind("<FocusIn>", clear_old)
    old.bind("<FocusOut>", restore_old)
    new.bind("<FocusIn>", clear_new)
    new.bind("<FocusOut>", restore_new)

    btn_style = {
        "width": 12, "height": 1,
        "font": ("Segoe UI", 10),
        "bg": "#ffffff",
        "activebackground": "#e0e0e0",
        "relief": "raised", "bd": 1
    }

    tk.Button(app, text="เปลี่ยนชื่อ", command=lambda: rename_user(old.get(), new.get()), **btn_style).pack(pady=(10, 5))
    tk.Button(app, text="กลับ", command=show_main_menu, **btn_style).pack()


def show_language_installer():
    clear_window()
    app.geometry("400x500")  # <- เพิ่มตรงนี้
    app.configure(bg="#f0f0f0")

    tk.Label(app, text="เลือกภาษาที่ต้องการติดตั้ง", font=("Segoe UI", 14, "bold"), bg="#f0f0f0").pack(pady=(20, 10))

    container = tk.Frame(app, bg="#f0f0f0")
    container.pack(pady=10)

    lang_options = {
        "ภาษาไทย": "th-TH",
        "ภาษา English (US)": "en-US",
        "ภาษา Chinese (Simplified, China)": "zh-CN"
    }

    lang_vars = {}
    for label, code in lang_options.items():
        var = tk.IntVar()
        tk.Checkbutton(container, text=label, variable=var, font=("Segoe UI", 10), bg="#f0f0f0").pack(anchor="w", padx=20)
        lang_vars[code] = var

    tk.Label(app, text="ตั้งค่าภาษาหลักของ Windows เป็น:", font=("Segoe UI", 10), bg="#f0f0f0").pack(pady=(10, 0))

    selected_lang = tk.StringVar(value="th-TH")

    for label, code in lang_options.items():
        tk.Radiobutton(app, text=label, variable=selected_lang, value=code,
                       font=("Segoe UI", 10), bg="#f0f0f0").pack(anchor="w", padx=40)

    def apply_language_settings():
        to_install = [code for code, var in lang_vars.items() if var.get() == 1]
        if not to_install:
            messagebox.showwarning("เตือน", "กรุณาเลือกอย่างน้อย 1 ภาษาเพื่อติดตั้ง")
            return

        for code in to_install:
            capability = f"Language.Basic~~~{code}~0.0.1.0"
            ps_cmd = f"Add-WindowsCapability -Online -Name '{capability}'"
            try:
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("ผิดพลาด", f"ติดตั้ง {code} ล้มเหลว:\n{e}")
                return

        new_lang = selected_lang.get()
        full_list = [new_lang] + [code for code in to_install if code != new_lang]

        try:
            lang_list_str = ",".join([f"'{code}'" for code in full_list])
            ps_ui = f"""
            $langs = @({lang_list_str});
            Set-WinUserLanguageList -LanguageList $langs -Force;
            Set-WinUILanguageOverride -Language '{new_lang}';
            """
            subprocess.run(["powershell", "-Command", ps_ui], check=True)
            messagebox.showinfo("สำเร็จ", f"ติดตั้งภาษา และตั้งค่าภาษา UI เป็น {new_lang} แล้ว\n(อาจต้องรีสตาร์ท)")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("ผิดพลาด", f"ตั้งค่าภาษา UI ไม่สำเร็จ:\n{e}")

    # ปุ่มควบคุม
    btn_style = {
        "width": 22, "height": 2,
        "font": ("Segoe UI", 10),
        "bg": "#ffffff",
        "activebackground": "#e0e0e0",
        "relief": "raised", "bd": 1
    }

    tk.Button(app, text="ติดตั้งและตั้งค่าภาษา", command=apply_language_settings, **btn_style).pack(pady=(20, 5))
    tk.Button(app, text="กลับ", command=show_main_menu, **btn_style).pack(pady=(0, 20))
    
def center_window(win, width, height):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")




app.title("User Manager")
center_window(app, 400, 500)  # กำหนดขนาดและจัดกลางจอ

# เริ่มต้น
show_main_menu()
app.mainloop()

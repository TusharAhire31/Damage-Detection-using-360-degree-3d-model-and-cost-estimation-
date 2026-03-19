# gui/login_page.py
import customtkinter as ctk
from tkinter import messagebox

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.win = None

    def show(self, on_success):
        self.win = ctk.CTkFrame(self.root)
        self.win.pack(fill="both", expand=True)
        ctk.CTkLabel(self.win, text="Welcome", font=("Arial", 24)).pack(pady=12)
        self.email = ctk.StringVar()
        self.pw = ctk.StringVar()
        ctk.CTkEntry(self.win, placeholder_text="Email", textvariable=self.email, width=300).pack(pady=8)
        ctk.CTkEntry(self.win, placeholder_text="Password", textvariable=self.pw, width=300, show="*").pack(pady=8)

        def attempt():
            if self.email.get().strip() and self.pw.get().strip():
                self.win.pack_forget()
                on_success()
            else:
                messagebox.showerror("Login failed", "Enter email and password (demo)")

        ctk.CTkButton(self.win, text="Login", command=attempt).pack(pady=12)

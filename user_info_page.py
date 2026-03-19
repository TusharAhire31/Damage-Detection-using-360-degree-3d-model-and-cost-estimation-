# gui/user_info_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import re

class UserInfoPage(tk.Frame):
    """
    User info + validation page.
    Validates inputs before allowing 'Continue'.
    Call set_continue_callback(func) to set what happens on success.
    """

    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#1e1e1e")
        self.controller = controller
        self.continue_callback = None
        self.user_data = {}

        # --- layout frames -------------------------------------------------
        header = tk.Frame(self, bg="#1e1e1e")
        header.pack(fill="x", pady=(10, 6))
        tk.Label(header, text="User Information", bg="#1e1e1e", fg="cyan",
                 font=("Arial", 18, "bold")).pack()

        form = tk.Frame(self, bg="#1e1e1e")
        form.pack(fill="both", expand=True, padx=18, pady=8)

        # --- variables -----------------------------------------------------
        self.var_name = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_mobile = tk.StringVar()
        self.var_pincode = tk.StringVar()
        self.var_vehicle_cat = tk.StringVar()
        self.var_vehicle_model = tk.StringVar()

        # --- helper: create label+entry with grid positioning --------------
        def make_row(row, label_text, widget):
            lbl = tk.Label(form, text=label_text, anchor="w", bg="#1e1e1e", fg="white", font=("Arial", 11))
            lbl.grid(row=row, column=0, sticky="w", pady=6, padx=(0,8))
            widget.grid(row=row, column=1, sticky="we", pady=6)
            form.grid_columnconfigure(1, weight=1)
            return widget

        # Full name
        entry_name = tk.Entry(form, textvariable=self.var_name, font=("Arial", 11))
        make_row(0, "Full name (letters only):", entry_name)

        # Email
        entry_email = tk.Entry(form, textvariable=self.var_email, font=("Arial", 11))
        make_row(1, "Email (example@domain.com):", entry_email)

        # Mobile number
        entry_mobile = tk.Entry(form, textvariable=self.var_mobile, font=("Arial", 11))
        make_row(2, "Mobile (10 digits):", entry_mobile)

        # Pincode
        entry_pin = tk.Entry(form, textvariable=self.var_pincode, font=("Arial", 11))
        make_row(3, "Pincode (6 digits):", entry_pin)

        # Vehicle category (combobox)
        cat_values = ["-- Select --", "Car", "SUV", "Truck"]
        cb_cat = ttk.Combobox(form, textvariable=self.var_vehicle_cat, values=cat_values, state="readonly")
        cb_cat.current(0)
        make_row(4, "Vehicle category:", cb_cat)

        # Vehicle model (dependent)
        # sample model lists (you can extend)
        self.models_by_cat = {
            "Car": ["-- Select Model --", "Toyota Altis", "Honda City", "Hyundai i20", "Maruti Swift"],
            "SUV": ["-- Select Model --", "Hyundai Creta", "Kia Seltos", "Mahindra XUV300", "Toyota Fortuner"],
            "Truck": ["-- Select Model --", "Tata Ace", "Ashok Leyland Dost", "Mahindra Jeeto"]
        }
        cb_model = ttk.Combobox(form, textvariable=self.var_vehicle_model, values=["-- Select --"], state="readonly")
        cb_model.current(0)
        make_row(5, "Vehicle model:", cb_model)

        # Bind category change to update models
        def on_cat_change(event=None):
            cat = self.var_vehicle_cat.get()
            if cat in self.models_by_cat:
                models = self.models_by_cat[cat]
            else:
                models = ["-- Select --"]
            cb_model.config(values=models)
            cb_model.current(0)
            self.var_vehicle_model.set(models[0])

        cb_cat.bind("<<ComboboxSelected>>", on_cat_change)

        # --- buttons ------------------------------------------------------
        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(fill="x", pady=(6,14), padx=18)

        btn_submit = tk.Button(btn_frame, text="Continue", command=self._on_continue,
                               bg="#0078D7", fg="white", font=("Arial", 11, "bold"), width=14)
        btn_submit.pack(side="right", padx=6)

        btn_reset = tk.Button(btn_frame, text="Reset", command=self._reset_form,
                              bg="#444444", fg="white", font=("Arial", 11), width=10)
        btn_reset.pack(side="right")

        # --- realtime simple validation (on focus out) --------------------
        entry_name.bind("<FocusOut>", lambda e: self._validate_field("name"))
        entry_email.bind("<FocusOut>", lambda e: self._validate_field("email"))
        entry_mobile.bind("<FocusOut>", lambda e: self._validate_field("mobile"))
        entry_pin.bind("<FocusOut>", lambda e: self._validate_field("pincode"))

        # store quick references for styling
        self._field_widgets = {
            "name": entry_name,
            "email": entry_email,
            "mobile": entry_mobile,
            "pincode": entry_pin,
            "category": cb_cat,
            "model": cb_model
        }

    # -------------------------
    # Public: app controller will call this
    def set_continue_callback(self, func):
        """Set the function to call when Continue is pressed and validation passes."""
        self.continue_callback = func

    # -------------------------
    # Validation helpers
    def _validate_name(self):
        val = self.var_name.get().strip()
        # letters and spaces only; at least two characters
        if len(val) < 2:
            return False, "Name too short"
        if not re.fullmatch(r"[A-Za-z ]+", val):
            return False, "Name must contain letters and spaces only"
        return True, ""

    def _validate_email(self):
        val = self.var_email.get().strip()
        # simple email pattern; good enough for form validation
        if not val:
            return False, "Email required"
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", val):
            return False, "Invalid email format"
        return True, ""

    def _validate_mobile(self):
        val = self.var_mobile.get().strip()
        if not val:
            return False, "Mobile required"
        if not val.isdigit():
            return False, "Mobile must be digits only"
        if len(val) != 10:
            return False, "Mobile must be 10 digits"
        return True, ""

    def _validate_pincode(self):
        val = self.var_pincode.get().strip()
        if not val:
            return False, "Pincode required"
        if not val.isdigit():
            return False, "Pincode must be digits only"
        if len(val) not in (5,6):  # allow 5 or 6 digits (adjust if you want strict 6)
            return False, "Pincode length looks wrong"
        return True, ""

    def _validate_vehicle(self):
        cat = self.var_vehicle_cat.get()
        model = self.var_vehicle_model.get()
        if cat not in ("Car", "SUV", "Truck"):
            return False, "Select vehicle category"
        # ensure model valid for selected category
        models = self.models_by_cat.get(cat, [])
        if model not in models or model.startswith("--"):
            return False, "Select vehicle model"
        return True, ""

    def _validate_field(self, field):
        """Validate single field and color the widget border (visual cue)."""
        mapper = {
            "name": self._validate_name,
            "email": self._validate_email,
            "mobile": self._validate_mobile,
            "pincode": self._validate_pincode
        }
        widget = self._field_widgets.get(field)
        if field in mapper:
            ok, _msg = mapper[field]()
            # color border: red for invalid, default for valid
            if widget:
                widget.config(highlightthickness=2, highlightbackground=("#ff4d4d" if not ok else "#2e2e2e"))
            return ok
        return True

    def _collect_and_validate_all(self):
        # run all validations, collect error messages
        validators = [
            ("Full name", self._validate_name),
            ("Email", self._validate_email),
            ("Mobile", self._validate_mobile),
            ("Pincode", self._validate_pincode),
            ("Vehicle selection", self._validate_vehicle)
        ]
        errors = []
        for title, fn in validators:
            ok, msg = fn()
            if not ok:
                errors.append(f"{title}: {msg}")

        if errors:
            return False, errors

        # all ok -> store data
        self.user_data = {
            "name": self.var_name.get().strip(),
            "email": self.var_email.get().strip(),
            "mobile": self.var_mobile.get().strip(),
            "pincode": self.var_pincode.get().strip(),
            "vehicle_category": self.var_vehicle_cat.get(),
            "vehicle_model": self.var_vehicle_model.get()
        }
        return True, []

    # -------------------------
    def _on_continue(self):
        ok, errors = self._collect_and_validate_all()
        if not ok:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        # success: call external continue callback if provided
        if callable(self.continue_callback):
            try:
                self.continue_callback()   # e.g. app moves to next page
            except Exception as e:
                # don't crash the UI; show helpful message
                messagebox.showerror("Error", f"Continue callback failed: {e}")
        else:
            # no callback set — just acknowledge
            messagebox.showinfo("Success", "Information saved successfully!")
            self.controller.go_to_image_upload()

    def _reset_form(self):
        self.var_name.set("")
        self.var_email.set("")
        self.var_mobile.set("")
        self.var_pincode.set("")
        self.var_vehicle_cat.set("-- Select --")
        self.var_vehicle_model.set("-- Select --")
        # reset highlight styles
        for w in self._field_widgets.values():
            try:
                w.config(highlightthickness=0)
            except Exception:
                pass

    # optional: other modules can call this
    def get_user_data(self):
        return self.user_data.copy()

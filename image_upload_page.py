import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from models.damage_detector import DentDetector
from models.cost_estimator import estimate_repair_cost
from gui.viewer_3d import show_3d
from utils.garage_locator import find_nearby_garages, open_google_maps


class ImageUploadPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#202124")
        self.detector = DentDetector()
        self.image_path = None
        self.depth_map_path = None
        self.controller = controller

        # Sidebar
        sidebar = tk.Frame(self, bg="#181818", width=200)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)
        main = tk.Frame(self, bg="#202124")
        main.pack(side="right", expand=True, fill="both", padx=20, pady=10)

        def make_button(text, cmd):
            return tk.Button(
                sidebar, text=text, command=cmd,
                bg="#0078D7", fg="white", font=("Arial", 10, "bold")
            )

        tk.Label(sidebar, text="Controls", bg="#181818", fg="white", font=("Arial", 14, "bold")).pack(pady=10)
        make_button("Upload Image", self.upload_image).pack(fill="x", pady=4)
        make_button("Detect & Process", self.detect_damage).pack(fill="x", pady=4)
        make_button("View 3D", self.view_3d).pack(fill="x", pady=4)
        make_button("Estimate Cost", self.show_cost).pack(fill="x", pady=4)
        make_button("Find Nearby Garages", self.show_garages_popup).pack(fill="x", pady=4)
        make_button("Clear", self.clear_display).pack(fill="x", pady=4)

        # Pincode input
        tk.Label(sidebar, text="Enter Pincode:", bg="#181818", fg="white").pack(pady=(10, 0))
        self.pincode_entry = tk.Entry(sidebar)
        self.pincode_entry.pack(fill="x", pady=5)
        self.pincode_entry.insert(0, "411001")

        # Display area
        self.labels = {}
        for name in ["Original", "Detected Damage"]:
            tk.Label(main, text=name, fg="#00d4ff", bg="#202124", font=("Arial", 12, "bold")).pack(pady=(10, 0))
            lbl = tk.Label(main, bg="#202124")
            lbl.pack()
            self.labels[name] = lbl

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.png;*.jpeg")])
        if not self.image_path:
            return
        img = Image.open(self.image_path).resize((500, 350))
        tk_img = ImageTk.PhotoImage(img)
        self.labels["Original"].configure(image=tk_img)
        self.labels["Original"].image = tk_img
        messagebox.showinfo("Image Uploaded", "Image loaded successfully.")

    def detect_damage(self):
        if not self.image_path:
            messagebox.showwarning("Upload Required", "Please upload an image first.")
            return

        dents, overlay, depth = self.detector.detect_dent(self.image_path)
        out_path = "temp_depth.png"
        cv2.imwrite(out_path, depth)
        self.depth_map_path = out_path

        tk_img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)))
        self.labels["Detected Damage"].configure(image=tk_img)
        self.labels["Detected Damage"].image = tk_img

        messagebox.showinfo("Detection Complete", "Dent detection and depth estimation completed successfully.")

    def view_3d(self):
        if not self.depth_map_path:
            messagebox.showwarning("No Depth Map", "Please process the image first.")
            return
        show_3d(self.depth_map_path)

    # -----------------------------------
    def show_cost(self):
        if not self.depth_map_path:
            messagebox.showwarning("Error", "Please detect and process the image first.")
            return

        try:
            cost_data = estimate_repair_cost(self.depth_map_path)

            if isinstance(cost_data, tuple):
                total_cost, area_cm2, avg_depth = cost_data
                severity = (
                    "Low" if avg_depth < 0.3 else
                    "Moderate" if avg_depth < 0.6 else
                    "Severe"
                )
                message = (
                    f"🧾 Estimated Repair Report\n\n"
                    f"Damage Severity: {severity}\n"
                    f"Dent Area: {area_cm2:.2f} cm²\n"
                    f"Average Depth: {avg_depth:.3f}\n"
                    f"-----------------------------\n"
                    f"Approx. Repair Cost: ₹{total_cost:.2f}"
                )
            else:
                message = f"Approx. Repair Cost: ₹{float(cost_data):.2f}"

            messagebox.showinfo("Estimated Repair Cost", message)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to estimate cost:\n{str(e)}")

    def show_garages_popup(self):
        pincode = self.pincode_entry.get().strip()
        if not pincode:
            messagebox.showerror("Input Required", "Please enter a valid pincode.")
            return

        garages = find_nearby_garages(pincode)
        popup = tk.Toplevel(self)
        popup.title("Nearby Garages")
        popup.geometry("450x400")
        popup.config(bg="#202124")

        tk.Label(popup, text=f"Garages near {pincode}", bg="#202124", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

        for g in garages:
            tk.Label(popup, text=f"{g['name']} — {g['distance']} km — {g['contact']}",
                     bg="#202124", fg="#00ffcc", font=("Arial", 10)).pack()

        tk.Button(popup, text="Open in Google Maps",
                  command=lambda: open_google_maps(pincode),
                  bg="#0078D7", fg="white").pack(pady=10)

    # -----------------------------------
    def clear_display(self):
        for lbl in self.labels.values():
            lbl.configure(image="")
        self.image_path = None
        self.depth_map_path = None
        messagebox.showinfo("Cleared", "Workspace cleared successfully.")

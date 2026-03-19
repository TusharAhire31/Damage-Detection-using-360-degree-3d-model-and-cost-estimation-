# gui/app_main.py
import tkinter as tk
from gui.user_info_page import UserInfoPage
from gui.image_upload_page import ImageUploadPage

class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Damage 2D→3D Demo")
        self.geometry("1200x800")
        self.configure(bg="#202124")

        # Container for all pages
        container = tk.Frame(self, bg="#202124")
        container.pack(fill="both", expand=True)

        self.pages = {}
        for PageClass, name in [(UserInfoPage, "user_info"), (ImageUploadPage, "image_upload")]:
            page = PageClass(container, controller=self)
            self.pages[name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("user_info")

    def show_page(self, name):
        """Show a specific page."""
        page = self.pages[name]
        page.tkraise()

    def go_to_image_upload(self):
        """Called by UserInfoPage after successful validation."""
        self.show_page("image_upload")


def main():
    app = AppController()
    app.mainloop()


if __name__ == "__main__":
    main()

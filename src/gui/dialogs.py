import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from src.core.config import API_CALCULATION_METHODS, API_SCHOOLS, FONT_SIZES, DEFAULT_FONT_SIZE

class LocationDialog(simpledialog.Dialog):
    """Dialog to ask the user for their location."""
    def body(self, master):
        tk.Label(master, text="Enter your city:").grid(row=0)
        self.city_entry = tk.Entry(master)
        self.city_entry.grid(row=0, column=1)
        return self.city_entry

    def apply(self):
        self.result = self.city_entry.get()

class SettingsDialog(simpledialog.Dialog):
    """Dialog to configure API calculation methods, school, and font size."""
    
    def __init__(self, parent, title, current_method, current_school, current_font_size=None):
        self.current_method = current_method
        self.current_school = current_school
        self.current_font_size = current_font_size or DEFAULT_FONT_SIZE
        self.result = None  # Initialize result to prevent AttributeError if cancelled
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Calculation Method:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Reverse mapping for display
        self.method_options = {v: k for k, v in API_CALCULATION_METHODS.items()}
        self.method_combo = ttk.Combobox(master, values=list(self.method_options.keys()), width=40, state="readonly")
        
        # Set current value
        current_method_name = API_CALCULATION_METHODS.get(self.current_method, "Islamic Society of North America (ISNA)")
        self.method_combo.set(current_method_name)
        self.method_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(master, text="Madhab (School):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.school_options = {v: k for k, v in API_SCHOOLS.items()}
        self.school_combo = ttk.Combobox(master, values=list(self.school_options.keys()), width=40, state="readonly")
        
        current_school_name = API_SCHOOLS.get(self.current_school, "Hanafi")
        self.school_combo.set(current_school_name)
        self.school_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(master, text="Font Size:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.font_size_options = list(FONT_SIZES.keys())
        self.font_size_combo = ttk.Combobox(master, values=self.font_size_options, width=40, state="readonly")
        self.font_size_combo.set(self.current_font_size)
        self.font_size_combo.grid(row=2, column=1, padx=5, pady=5)
        
        return self.method_combo
    
    def apply(self):
        method_name = self.method_combo.get()
        school_name = self.school_combo.get()
        font_size = self.font_size_combo.get()
        
        self.result = {
            "method": self.method_options[method_name],
            "school": self.school_options[school_name],
            "font_size": font_size
        }

def show_error(message):
    """Show an error message dialog."""
    messagebox.showerror("Error", message)

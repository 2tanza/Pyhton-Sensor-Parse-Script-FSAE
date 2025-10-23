import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class CsvColumnSelector(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CSV Column Selector")
        self.geometry("400x500")

        self.df = None
        self.header_vars = []
        self.headers = []
        self.input_file_path = ""

        # --- Main Layout ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Load Button
        load_button = ttk.Button(main_frame, text="1. Load CSV File", command=self.load_csv)
        load_button.pack(fill=tk.X, pady=5)

        self.file_label = ttk.Label(main_frame, text="No file loaded.", wraplength=380)
        self.file_label.pack(pady=5)

        # 2. Header Selection Area
        selection_label = ttk.Label(main_frame, text="2. Select Columns to Keep")
        selection_label.pack(pady=(10, 0))

        # --- Checkbox Frame with Scrollbar ---
        checkbox_container = ttk.Frame(main_frame)
        checkbox_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        canvas = tk.Canvas(checkbox_container)
        scrollbar = ttk.Scrollbar(checkbox_container, orient="vertical", command=canvas.yview)
        
        # This frame holds the actual checkboxes
        self.checkbox_frame = ttk.Frame(canvas)

        self.checkbox_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Select All/None Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        select_all_btn = ttk.Button(button_frame, text="Select All", command=self.select_all)
        select_all_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        
        deselect_all_btn = ttk.Button(button_frame, text="Deselect All", command=self.deselect_all)
        deselect_all_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # 3. Export Button
        export_button = ttk.Button(main_frame, text="3. Export New CSV", command=self.export_csv)
        export_button.pack(fill=tk.X, pady=10)

    def load_csv(self):
        # Open file dialog
        path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not path:
            return  # User cancelled

        try:
            # Read CSV and get headers
            self.df = pd.read_csv(path)
            self.headers = list(self.df.columns)
            self.input_file_path = path
            self.file_label.config(text=f"Loaded: {path.split('/')[-1]}")
            
            self.create_checkboxes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            self.df = None
            self.file_label.config(text="Error loading file. Try again.")

    def create_checkboxes(self):
        # Clear old checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.header_vars = []

        # Create new checkboxes
        for header in self.headers:
            var = tk.BooleanVar(value=True) # Default to selected
            self.header_vars.append(var)
            cb = ttk.Checkbutton(self.checkbox_frame, text=header, variable=var)
            cb.pack(anchor="w", padx=10)

    def select_all(self):
        for var in self.header_vars:
            var.set(True)

    def deselect_all(self):
        for var in self.header_vars:
            var.set(False)

    def export_csv(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a CSV file first.")
            return

        # Get selected headers
        selected_headers = []
        for header, var in zip(self.headers, self.header_vars):
            if var.get():
                selected_headers.append(header)

        if not selected_headers:
            messagebox.showwarning("Warning", "Please select at least one column.")
            return

        # Ask where to save the new file
        save_path = filedialog.asksaveasfilename(
            title="Save new CSV as...",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not save_path:
            return  # User cancelled

        try:
            # Create new DataFrame with only selected columns
            new_df = self.df[selected_headers]
            
            # Save to new CSV
            new_df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", f"File saved successfully at:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    app = CsvColumnSelector()
    app.mainloop()
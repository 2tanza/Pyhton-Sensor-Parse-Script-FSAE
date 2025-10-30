import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import platform

# dpi fix, solves blurry display on high resolution screens for windows
if platform.system() == 'Windows':
    try:
        import ctypes
        # Set process to be "System DPI Aware" (value=1)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        print(f"Warning: Could not set DPI awareness. GUI might be blurry. Error: {e}")

class CsvColumnSelector(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CSV Column Selector")
        self.geometry("800x1000")
        self.minsize(600, 1000)

        self.df = None
        # --- MODIFIED: self.header_vars removed. This is the single source of truth.
        # This list will store tuples: (header_string, var_object, widget_object)
        self.checkbox_data = []
        self.headers = []
        self.input_file_path = ""
        
        # --- NEW: Number of columns for the grid ---
        self.num_columns = 3 

        # --- Main Layout ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Load Button
        load_button = ttk.Button(main_frame, text="1. Load CSV File", command=self.load_csv)
        load_button.pack(fill=tk.X, pady=5)

        self.file_label = ttk.Label(main_frame, text="No file loaded.", wraplength=780)
        self.file_label.pack(pady=5, fill=tk.X)

        # --- NEW: 2. Search Bar ---
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        search_label = ttk.Label(search_frame, text="2. Search Columns:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._update_checkbox_display)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        clear_search_btn = ttk.Button(search_frame, text="Clear", command=lambda: self.search_var.set(""))
        clear_search_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 3. Header Selection Area
        selection_label = ttk.Label(main_frame, text="3. Select Columns to Keep")
        selection_label.pack(pady=(10, 0))

        # --- Checkbox Frame with Scrollbar ---
        checkbox_container = ttk.Frame(main_frame)
        checkbox_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        canvas = tk.Canvas(checkbox_container)
        scrollbar = ttk.Scrollbar(checkbox_container, orient="vertical", command=canvas.yview)
        
        self.checkbox_frame = ttk.Frame(canvas, padding="5")

        self.checkbox_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # --- MODIFIED: Bind mouse wheel to canvas (cross-platform) ---
        # We pass the canvas object 'c' to the handling function
        canvas.bind_all("<MouseWheel>", lambda e, c=canvas: self._on_mousewheel(e, c))
        # Bind Linux scroll buttons (if not Windows)
        if platform.system() != 'Windows':
            canvas.bind_all("<Button-4>", lambda e, c=canvas: self._on_mousewheel(e, c))
            canvas.bind_all("<Button-5>", lambda e, c=canvas: self._on_mousewheel(e, c))

        canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Select All/None Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        select_all_btn = ttk.Button(button_frame, text="Select All (Visible)", command=self.select_all_visible)
        select_all_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        
        deselect_all_btn = ttk.Button(button_frame, text="Deselect All (Visible)", command=self.deselect_all_visible)
        deselect_all_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # 4. Export Button
        export_button = ttk.Button(main_frame, text="4. Export New CSV", command=self.export_csv)
        export_button.pack(fill=tk.X, pady=10)

    def load_csv(self):
        path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not path:
            return

        try:
            self.df = pd.read_csv(path)
            self.headers = list(self.df.columns)
            self.input_file_path = path
            self.file_label.config(text=f"Loaded: {path.split('/')[-1]}")
            
            self.search_var.set("")
            self.create_checkboxes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            self.df = None
            self.file_label.config(text="Error loading file. Try again.")

    def create_checkboxes(self):
        # Clear old checkboxes from the frame
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
            
        # --- MODIFIED: Cleaned up ---
        self.checkbox_data = []

        # Create new checkbox data (variable and widget)
        for header in self.headers:
            var = tk.BooleanVar(value=True) # Default to selected
            cb = ttk.Checkbutton(self.checkbox_frame, text=header, variable=var)
            
            # Store the header, var, and widget for filtering
            self.checkbox_data.append((header, var, cb))

        self._update_checkbox_display()

    # --- NEW: Function to filter and display checkboxes in a grid ---
    def _update_checkbox_display(self, *args):
        """
        Filters checkboxes based on search_var and displays them
        in a grid with self.num_columns.
        """
        search_term = self.search_var.get().lower()
        
        visible_index = 0
        for header, var, widget in self.checkbox_data:
            if search_term in header.lower():
                row = visible_index // self.num_columns
                col = visible_index % self.num_columns
                widget.grid(row=row, column=col, sticky="w", padx=10, pady=2)
                visible_index += 1
            else:
                widget.grid_forget()

    # --- NEW: Cross-platform mouse wheel handler ---
    def _on_mousewheel(self, event, canvas):
        """Cross-platform mouse wheel scrolling."""
        if platform.system() == 'Windows':
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # Linux and other *nix
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    # --- MODIFIED: Select/Deselect all *visible* checkboxes ---
    def select_all_visible(self):
        search_term = self.search_var.get().lower()
        for header, var, widget in self.checkbox_data:
            # Only affect visible items
            if search_term in header.lower():
                var.set(True)

    def deselect_all_visible(self):
        search_term = self.search_var.get().lower()
        for header, var, widget in self.checkbox_data:
            # Only affect visible items
            if search_term in header.lower():
                var.set(False)

    def export_csv(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a CSV file first.")
            return

        selected_headers = []
        # Iterate over the *full* data list, not just visible ones
        for header, var, widget in self.checkbox_data:
            if var.get():
                selected_headers.append(header)

        if not selected_headers:
            messagebox.showwarning("Warning", "Please select at least one column.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save new CSV as...",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not save_path:
            return

        try:
            new_df = self.df[selected_headers]
            new_df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", f"File saved successfully at:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    app = CsvColumnSelector()
    app.mainloop()
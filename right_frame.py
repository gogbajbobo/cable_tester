import tkinter as tk
from tkinter import ttk

from app import CableTesterApplication


def setup_right_frame(self: CableTesterApplication, frame: ttk.LabelFrame):
    # Create notebook for different logs
    notebook = ttk.Notebook(frame)
    notebook.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    # Application logs tab
    logs_frame = ttk.Frame(notebook)
    notebook.add(logs_frame, text="Application Logs")

    self.logs_text = tk.Text(logs_frame, wrap="word")
    self.logs_text.pack(fill="both", expand=True)
    logs_scrollbar = ttk.Scrollbar(logs_frame, command=self.logs_text.yview)
    logs_scrollbar.pack(side="right", fill="y")
    self.logs_text.configure(yscrollcommand=logs_scrollbar.set)

    # Configure grid weights for right frame
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

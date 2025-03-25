from tkinter import ttk

from app import CableTesterApplication


def setup_left_frame(self: CableTesterApplication, frame: ttk.LabelFrame):
    # Tables section
    ttk.Label(frame, text="Tables:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Button(frame, text="Update Tables List", command=self.update_tables_list).grid(
        row=1, column=0, padx=5, pady=5, sticky="ew"
    )
    self.tables_combobox = ttk.Combobox(frame, textvariable=self.selected_table)
    self.tables_combobox.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
    # Привязываем обработчик события выбора
    self.tables_combobox.bind("<<ComboboxSelected>>", self.on_table_selected)

    # COM Ports section
    ttk.Label(frame, text="COM Ports:").grid(
        row=3, column=0, padx=5, pady=5, sticky="w"
    )
    ttk.Button(
        frame, text="Update COM Ports List", command=self.update_ports_list
    ).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
    self.ports_combobox = ttk.Combobox(frame, textvariable=self.selected_port)
    self.ports_combobox.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

    # Contact count
    ttk.Label(frame, text="Number of Contacts:").grid(
        row=6, column=0, padx=5, pady=5, sticky="w"
    )
    ttk.Entry(frame, textvariable=self.contact_count).grid(
        row=7, column=0, padx=5, pady=5, sticky="ew"
    )

    # Control buttons
    ttk.Button(frame, text="Start Process", command=self.start_process).grid(
        row=8, column=0, padx=5, pady=5, sticky="ew"
    )
    ttk.Button(frame, text="Stop Process", command=self.stop_process).grid(
        row=9, column=0, padx=5, pady=5, sticky="ew"
    )

    # Configure grid weights for left frame
    frame.grid_columnconfigure(0, weight=1)

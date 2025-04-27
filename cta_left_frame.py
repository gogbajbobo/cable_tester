import os
import tkinter as tk
from tkinter import ttk, filedialog

from app import CableTesterApplication
import cta_tables
import cta_ports
import cta_process

STOP_BUTTON = "stop_button"


def setup_left_frame(self: CableTesterApplication, frame: ttk.LabelFrame):

    _update_tables_list = lambda: cta_tables.update_tables_list(self)
    _update_ports_list = lambda: cta_ports.update_ports_list(self)
    _on_table_selected = lambda event: cta_tables.on_table_selected(
        self, event
    )
    _start_process = lambda: cta_process.start_process(self)
    _stop_process = lambda: cta_process.stop_process(self)

    def browse_directory(self: CableTesterApplication):
        """Открывает диалог выбора директории"""

        # Получаем текущую директорию
        current_dir = self.data_directory.get()

        # Открываем диалог выбора директории
        directory = filedialog.askdirectory(
            initialdir=current_dir, title="Select Directory for Tables"
        )

        # Если директория выбрана, обновляем переменную и список таблиц
        if directory:
            self.data_directory.set(directory)
            self.log(f"Changed data directory to: {directory}")
            _update_tables_list()

    _browse_directory = lambda: browse_directory(self)

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    # Tables section

    tables_row_start = 0
    ttk.Label(frame, text="Tables:").grid(
        row=tables_row_start + 0, column=0, padx=5, pady=5, sticky="w"
    )

    # Entry для отображения пути к директории
    self.dir_entry = ttk.Entry(
        frame,
        textvariable=self.data_directory,
        state="readonly",
    )
    self.dir_entry.grid(
        row=tables_row_start + 1, column=0, padx=5, pady=5, sticky="w"
    )

    # Кнопка выбора директории

    ttk.Button(
        frame,
        text="...",
        command=_browse_directory,
        width=3,
    ).grid(row=tables_row_start + 1, column=1, padx=5, pady=5, sticky="ewsn")

    ttk.Button(
        frame, text="Update Tables List", command=_update_tables_list
    ).grid(
        row=tables_row_start + 2,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )
    self.tables_combobox = ttk.Combobox(
        frame, textvariable=self.selected_table
    )
    self.tables_combobox.grid(
        row=tables_row_start + 3,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )
    # Привязываем обработчик события выбора
    self.tables_combobox.bind("<<ComboboxSelected>>", _on_table_selected)

    ttk.Separator(frame, orient="horizontal").grid(
        row=tables_row_start + 4,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )

    # COM Ports section

    comport_row_start = tables_row_start + 5

    ttk.Label(frame, text="COM Ports:").grid(
        row=comport_row_start + 0, column=0, padx=5, pady=5, sticky="w"
    )
    ttk.Button(
        frame, text="Update COM Ports List", command=_update_ports_list
    ).grid(
        row=comport_row_start + 1,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )
    self.ports_combobox = ttk.Combobox(frame, textvariable=self.selected_port)
    self.ports_combobox.grid(
        row=comport_row_start + 2,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )

    ttk.Separator(frame, orient="horizontal").grid(
        row=comport_row_start + 3,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )

    # Contact count

    contacts_row_start = comport_row_start + 4

    ttk.Label(frame, text="Number of Contacts:").grid(
        row=contacts_row_start + 0,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="w",
    )
    ttk.Entry(frame, textvariable=self.contact_count).grid(
        row=contacts_row_start + 1,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )

    ttk.Separator(frame, orient="horizontal").grid(
        row=contacts_row_start + 2,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )

    # Control buttons

    controls_row_start = contacts_row_start + 3

    ttk.Button(frame, text="Start Process", command=_start_process).grid(
        row=controls_row_start + 0,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )
    ttk.Button(
        frame, text="Stop Process", command=_stop_process, name=STOP_BUTTON
    ).grid(
        row=controls_row_start + 1,
        column=0,
        columnspan=2,
        padx=5,
        pady=5,
        sticky="ew",
    )

    # Update initial ports and tables lists
    self.root.after(0, _update_tables_list)
    self.root.after(0, _update_ports_list)


def set_controls_state(self: CableTesterApplication, state: str):
    for child in self.left_frame.winfo_children():
        if child.winfo_name() != STOP_BUTTON:
            child["state"] = state


def disable_controls(self: CableTesterApplication):
    set_controls_state(self, tk.DISABLED)


def enable_controls(self: CableTesterApplication):
    set_controls_state(self, tk.NORMAL)

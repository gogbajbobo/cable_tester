import os
import pandas as pd

from app import CableTesterApplication
import cta_left_frame
import cta_middle_frame
import cta_process_frame


def on_table_selected(self: CableTesterApplication, event=None):
    """Обрабатывает выбор таблицы из выпадающего списка"""
    selected_table = self.selected_table.get()

    self.log(f"selected_table: {selected_table}")

    if not selected_table:
        cta_left_frame.check_start_state(self)
        self.log("No table selected")
        # Очищаем текущие данные в Treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        cta_middle_frame.update_data_view(self)
        return

    cta_left_frame.check_start_state(self)
    self.log(f"Table selected: {selected_table}")

    try:
        load_selected_table(self)

        # Получаем информацию о таблице
        rows, cols = self.table_data.shape
        self.log(f"Table loaded: {rows} rows, {cols} columns")

        # Очищаем текущие данные в Treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

        columns = tuple(self.table_data.columns)[:-2]

        self.data_tree["columns"] = columns

        # Set column headings
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=64)

        for i in range(rows):
            row = self.table_data.iloc[i][:-2]
            row_data = [data for data in row.fillna("").values]
            self.data_tree.insert("", "end", values=row_data)

        # find_value_in_table(self, "1")

    except Exception as e:
        self.log_error(f"Error loading table {selected_table}: {str(e)}")


def update_tables_list(self: CableTesterApplication):
    """Update the list of available tables"""
    # This is a placeholder - replace with actual table discovery logic
    # For example, scan a directory for CSV or Excel files

    self.log("Updating tables list")

    # Example implementation - looking for CSV and Excel files in current directory
    self.tables_list = []

    if os.path.isdir(self.data_directory.get()):
        for file in os.listdir(self.data_directory.get()):
            if file.startswith("colors") and file.endswith(".csv"):
                self.colors_data = pd.read_csv(
                    os.path.join(self.data_directory.get(), file),
                    sep=";",
                    dtype=str,
                )
                # self.log(f"Load colors data:\n{self.colors_data}")
            elif (
                file.endswith(".csv")
                or file.endswith(".xlsx")
                or file.endswith(".xls")
            ):
                self.tables_list.append(file)
    else:
        self.log_error(f"Have no data dir {self.data_directory.get()}")

    self.tables_combobox["values"] = self.tables_list

    if self.tables_list:
        self.tables_combobox.current(0)
        self.log(f"Found {len(self.tables_list)} tables")
        self.root.after(0, lambda: on_table_selected(self))
    else:
        self.table_data = pd.DataFrame()
        self.selected_table.set("")
        on_table_selected(self)
        self.log("No tables found")


def load_selected_table(self: CableTesterApplication):
    # Load the selected table
    st = os.path.join(self.data_directory.get(), self.selected_table.get())
    try:
        if st.endswith(".csv"):
            self.table_data = pd.read_csv(st, sep=";", dtype=str)
        elif st.endswith(".xlsx") or st.endswith(".xls"):
            self.table_data = pd.read_excel(st, dtype=str)
        else:
            self.log_warning(f"Unsupported file format: {st}")
            return
        self.log_info(f"Successfully loaded table: {st}")
        cta_middle_frame.update_data_view(self)
    except Exception as e:
        self.log_error(f"Error loading table: {str(e)}")
        return


def construct_line(v1: str, v2: str, max_len=16):
    line = " ".join([v1, v2])
    if len(line) > max_len:
        idx = max_len - len(v2) - 1
        v1 = v1[:idx]
        line = " ".join([v1, v2])
    return line


def find_value_in_table(
    self: CableTesterApplication, value: str
) -> tuple[str, str] | None:
    try:
        result = self.table_data.loc[
            self.table_data["Откуда"].str.endswith(f":{value}")
        ]
        if result.empty:
            self.log_warning(f"Value {value} not found in table.")
            cta_process_frame.update_process_frame(self)
            return

        result = result.fillna("")

        idx = result.index[0]

        rows = self.data_tree.get_children()
        if len(rows) > idx:
            child_id = rows[idx]
            self.data_tree.selection_set(child_id)

        mark_value = result["Маркировка"].values[0].strip()
        from_value = result["Откуда"].values[0].strip()
        to_value = result["Куда"].values[0].strip()
        color_value = result["Цвет"].values[0].strip()

        if not self.colors_data.empty:
            color_data = self.colors_data.loc[
                self.colors_data["Lat"].str.contains(color_value)
            ]
            if not color_data.empty:
                color_value = color_data["Color"].values[0].strip()

        self.log_info(f"Маркировка: {mark_value}")
        self.log_info(f"Куда: {to_value}")

        self.log_info(f"Цвет: {color_value}")
        self.log_info(f"Откуда: {from_value}")

        cta_process_frame.update_process_frame(
            self, from_value, to_value, mark_value, color_value
        )

        line_1 = construct_line(mark_value, to_value)
        line_2 = construct_line(color_value, "")

        return line_1, line_2

    except Exception as e:
        self.log_error(f"Error test table: {str(e)}")
        return

import os
import pandas as pd

from app import CableTesterApplication, DATA_PATH
import cta_middle_frame


def on_table_selected(self: CableTesterApplication, event=None):
    """Обрабатывает выбор таблицы из выпадающего списка"""
    selected_table = self.selected_table.get()

    if not selected_table:
        self.log("No table selected")
        return

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
            self.data_tree.column(col, width=150)

        for i in range(rows):
            row = self.table_data.iloc[i][:-2]
            row_data = [data for data in row.fillna("").values]
            self.data_tree.insert("", "end", values=row_data)

        find_value_in_table(self, "1")

    except Exception as e:
        self.log_error(f"Error loading table {selected_table}: {str(e)}")


def update_tables_list(self: CableTesterApplication):
    """Update the list of available tables"""
    # This is a placeholder - replace with actual table discovery logic
    # For example, scan a directory for CSV or Excel files

    self.log("Updating tables list")

    # Example implementation - looking for CSV and Excel files in current directory
    self.tables_list = []

    if os.path.isdir(DATA_PATH):
        for file in os.listdir(DATA_PATH):
            if file.startswith("colors") and file.endswith(".csv"):
                self.colors_data = pd.read_csv(
                    os.path.join(DATA_PATH, file), sep=";"
                )
                self.log(f"Load colors data:\n{self.colors_data}")
            elif (
                file.endswith(".csv")
                or file.endswith(".xlsx")
                or file.endswith(".xls")
            ):
                self.tables_list.append(file)
    else:
        self.log_error(f"Have no data dir {DATA_PATH}")

    self.tables_combobox["values"] = self.tables_list

    if self.tables_list:
        self.tables_combobox.current(0)
        self.log(f"Found {len(self.tables_list)} tables")
        self.root.after(0, lambda: on_table_selected(self))
    else:
        self.log("No tables found")


def load_selected_table(self: CableTesterApplication):
    # Load the selected table
    st = os.path.join(DATA_PATH, self.selected_table.get())
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


def find_value_in_table(self: CableTesterApplication, value: str):
    try:
        result = self.table_data.loc[
            self.table_data["Откуда"].str.endswith(f":{value}")
        ]
        if result.empty:
            self.log_warning(f"Value {value} not found in table.")
            return

        idx = result.index[0]

        rows = self.data_tree.get_children()
        if len(rows) > idx:
            child_id = rows[idx]
            self.data_tree.selection_set(child_id)

        from_value = result["Откуда"].values[0]
        to_value = result["Куда"].values[0]

        self.log_info(f"Откуда: {from_value}")
        self.log_info(f"Куда: {to_value}")
        return from_value, to_value

    except Exception as e:
        self.log_error(f"Error test table: {str(e)}")
        return

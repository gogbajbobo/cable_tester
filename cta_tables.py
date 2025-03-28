import os
import pandas as pd

from app import CableTesterApplication, DATA_PATH


def on_table_selected(self: CableTesterApplication, event=None):
    """Обрабатывает выбор таблицы из выпадающего списка"""
    selected_table = self.selected_table.get()

    if not selected_table:
        self.log("No table selected")
        return

    self.log(f"Table selected: {selected_table}")

    try:
        load_selected_table(self)
        test_table_data(self)

        # Получаем информацию о таблице
        rows, cols = self.table_data.shape
        self.log(f"Table loaded: {rows} rows, {cols} columns")

        # Очищаем текущие данные в Treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

        # Опционально: Показываем превью таблицы (первые несколько строк)
        # preview_rows = min(5, rows)  # показываем максимум 5 строк для превью
        preview_rows = rows
        for i in range(preview_rows):
            row = self.table_data.iloc[i]
            preview = str(dict(zip(self.table_data.columns[:3], row.values[:3])))
            if len(self.table_data.columns) > 3:
                preview += " ... "  # добавляем многоточие, если есть больше столбцов
            self.data_tree.insert("", "end", values=(f"Preview Row {i}", preview))

        # Если таблица содержит информацию о контактах, обновляем соответствующее поле
        if (
            "contacts" in self.table_data.columns
            or "Contacts" in self.table_data.columns
        ):
            contact_col = (
                "contacts" if "contacts" in self.table_data.columns else "Contacts"
            )
            # Берем максимальное значение из столбца контактов, если это число
            try:
                max_contacts = self.table_data[contact_col].max()
                if pd.notna(max_contacts) and isinstance(max_contacts, (int, float)):
                    self.contact_count.set(int(max_contacts))
                    self.log(
                        f"Updated contact count to {max_contacts} based on table data"
                    )
            except Exception as e:
                self.log(f"Could not update contact count from table: {str(e)}")

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
            if file.endswith(".csv") or file.endswith(".xlsx") or file.endswith(".xls"):
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
            self.table_data = pd.read_csv(st, sep=";")
        elif st.endswith(".xlsx") or st.endswith(".xls"):
            self.table_data = pd.read_excel(st)
        else:
            self.log_warning(f"Unsupported file format: {st}")
            return
        self.log_info(f"Successfully loaded table: {st}")
    except Exception as e:
        self.log_error(f"Error loading table: {str(e)}")
        return


def test_table_data(self: CableTesterApplication):
    try:
        # print("test_table_data:", self.table_data)
        test_value = "XS1:1"
        result = self.table_data.loc[self.table_data["Откуда"] == test_value]
        print(f"result: {result}")
        print(f"Куда: {result['Куда'].values}")
    except Exception as e:
        self.log_error(f"Error test table: {str(e)}")
        return

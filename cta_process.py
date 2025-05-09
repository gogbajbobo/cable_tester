import threading
import time

from app import CableTesterApplication, COM_STATE
import cta_left_frame
import cta_process_frame
import cta_ports


def start_process(self: CableTesterApplication):
    """Start the main process loop"""
    if self.running:
        self.log_warning("Процесс уже запущен")
        return

    if not self.selected_port.get():
        self.log_error("Ошибка: не выбран COM-порт")
        return

    if not self.selected_table.get():
        self.log_error("Ошибка: не выбрана таблица")
        return

    try:
        self.log(
            f"Запускаю процесс с COM-портом {self.selected_port.get()} и таблицей {self.selected_table.get()}"
        )

        cta_ports.open_serial_connection(self)

        # Start the process thread
        self.com_state = COM_STATE.PREINIT
        cta_left_frame.disable_controls(self)
        self.running = True
        self.thread = threading.Thread(target=lambda: process_loop(self))
        self.thread.daemon = True
        self.thread.start()

    except Exception as e:
        self.log(f"Ошибка запуска процесса: {str(e)}")


def stop_process(self: CableTesterApplication):
    """Stop the main process loop"""
    if not self.running:
        self.log_warning("Процесс не запущен")
        return

    self.log("Отанавливаю процесс")
    self.running = False
    self.com_state = COM_STATE.NONE
    cta_left_frame.enable_controls(self)
    cta_process_frame.update_process_frame(self)

    # # Wait for the thread to finish
    # print(f"self.thread {self.thread}")
    # if self.thread:
    #     self.thread.join(timeout=0.5)

    cta_ports.close_serial_connection(self)


def process_loop(self: CableTesterApplication):
    """Main processing loop - runs in a separate thread"""
    self.log("Начинаю цикл процесса")

    while self.running:
        try:
            if not self.serial_connection:
                raise ValueError("Не установлено соединение с COM-портом")

            cta_ports.read_data(self)

            # Small delay to prevent CPU hogging
            time.sleep(0.01)

        except Exception as e:
            self.log(f"Ошибка в цикле процесса: {str(e)}")
            stop_process(self)

    self.log("Завершён цикл процесса")

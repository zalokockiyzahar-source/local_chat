import socket
import threading

from customtkinter import *


SERVER_IP = "192.168.0.185"
PORT = 5000


class ChatApp(CTkToplevel):

    def __init__(self, username, registration_window):

        super().__init__(registration_window)

        self.registration_window = registration_window

        self.title("Локальний чат")
        self.geometry("600x500")

        self.username = username

        # -------------------------
        # Підключення до сервера
        # -------------------------

        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:

            self.client.connect(
                (SERVER_IP, PORT)
            )

            print("Підключено до сервера!")

        except Exception as e:

            print("Не вдалося підключитися до сервера!")
            print(e)

            self.destroy()

            # Повертаємо форму
            self.registration_window.deiconify()

            return

        # -------------------------
        # Заголовок
        # -------------------------

        self.title_label = CTkLabel(
            self,
            text=f"Вітаємо, {self.username}!",
            font=("Arial", 22, "bold")
        )

        self.title_label.pack(pady=15)

        # -------------------------
        # Поле повідомлень
        # -------------------------

        self.messages = CTkTextbox(
            self,
            width=500,
            height=300
        )

        self.messages.pack(pady=10)

        # -------------------------
        # Поле введення
        # -------------------------

        self.message_entry = CTkEntry(
            self,
            width=400,
            placeholder_text="Введіть повідомлення..."
        )

        self.message_entry.pack(pady=10)

        # -------------------------
        # Кнопка
        # -------------------------

        self.send = CTkButton(
            self,
            text="Надіслати",
            command=self.send_message
        )

        self.send.pack(pady=10)

        # -------------------------
        # Потік отримання повідомлень
        # -------------------------

        self.receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True
        )

        self.receive_thread.start()

        # -------------------------
        # Закриття вікна
        # -------------------------

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_connection
        )

    def send_message(self):

        message = self.message_entry.get()

        if message:

            full_message = f"{self.username}: {message}"

            try:

                self.client.send(
                    full_message.encode("utf-8")
                )

                self.message_entry.delete(
                    0,
                    "end"
                )

            except Exception as e:

                print("Помилка відправлення:", e)

    def receive_messages(self):

        while True:

            try:

                message = self.client.recv(1024)

                if not message:
                    break

                message = message.decode()

                # Передаємо оновлення GUI
                # у головний потік Tkinter
                self.after(
                    0,
                    self.show_message,
                    message
                )

            except Exception as e:

                print("З'єднання закрито:", e)
                break

    def show_message(self, message):

        self.messages.insert(
            "end",
            message + "\n"
        )

        self.messages.see("end")

    def close_connection(self):

        try:

            self.client.shutdown(
                socket.SHUT_RDWR
            )

        except:
            pass

        try:

            self.client.close()

        except:
            pass

        # Закриваємо чат
        self.destroy()

        # Повертаємо форму реєстрації
        self.registration_window.deiconify()
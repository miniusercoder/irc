import os
import socket
from binascii import Error as CryptoKeyError
from datetime import datetime
from threading import Thread, main_thread

from cryptography.fernet import Fernet, InvalidToken
from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import set_title


class Client:
    _ip: str
    _username: str

    def __init__(self, ip: str, username: str, cypher_key: bytes):
        self._ip = ip
        self._username = username
        try:
            self._cipher = Fernet(cypher_key)
        except CryptoKeyError:
            print("Невалидный ключ шифрования")
            connect()
            return
        self._conn = socket.socket()
        try:
            self._conn.connect((ip, 9885))
        except Exception as e:
            print(e)
            print("Не удалось подключиться к серверу!")
            raise SystemExit()
        self._conn.send(self._cipher.encrypt(username.encode()))
        try:
            count = int(self._cipher.decrypt(self._conn.recv(5120)).decode("utf-8"))
        except InvalidToken:
            print("Этот ключ шифрования не подходит данному серверу")
            connect()
            return
        print(f"Подключено успешно к {ip}\nВ чате {count} пользователей\n\n", end="")
        set_title(f"{ip} - {self._username}")
        Thread(target=self.__receive_messages).start()

    def send_message(self, message):
        self._conn.send(self._cipher.encrypt(f"{self._username}|{message}".encode()))

    def __receive_messages(self):
        while True and main_thread().is_alive():
            try:
                data = self._cipher.decrypt(self._conn.recv(5120))
            except Exception as e:
                print(e)
                print("Потерял соединение с сервером!")
                connect()
                break
            if not data:
                print("Потерял соединение с сервером!")
                connect()
                break
            data = data.decode("utf-8").split("|")
            username = data[0]
            message = "|".join(data[1:])
            print(f"\r{username}: {message}")


def connect():
    ip = prompt("Введите ip сервера: ")
    login = prompt("Введите ваш логин: ")
    key = prompt("Ключ шифрования сервера: ").encode()
    client = Client(ip, login, key)
    while True:
        with patch_stdout():
            msg = prompt(f"{login}: ")
        if msg == "/exit":
            os._exit(0)
        if msg == "":
            print("\r", end="")
            continue
        client.send_message(msg)


date = datetime.now().strftime("%Y-%m-%d %H.%M")

connect()

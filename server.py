import socket
import time
from threading import Thread

from cryptography.fernet import Fernet

socket = socket.socket()
socket.bind(('', 9885))
socket.listen(50)
clients = []
try:
    key = open("key.txt", "r", encoding="utf-8")
except FileNotFoundError:
    key = Fernet.generate_key()
    open("key.txt", "w", encoding="utf-8").write(key.decode("utf-8"))
else:
    key = key.read().encode()
cipher = Fernet(key)
print(f"Ключ шифрования сервера: {key.decode('utf-8')}")


def accept_clients():
    while True:
        client = socket.accept()
        login = cipher.decrypt(client[0].recv(5120)).decode("utf-8")
        if login == "server":
            client[0].close()
            continue
        Thread(target=send_to_other, args=("server", f"Новый пользователь в чате: {login}", "")).start()
        client[0].send(cipher.encrypt(str(len(clients)).encode()))
        print(f"Новый пользователь в чате: {client[1]} ({login})")
        client = [client[0], login]
        clients.append(client)
        Thread(target=client_handler, args=(client,)).start()
        time.sleep(0.5)


def send_to_other(login, message, sender):
    for client in clients:
        if client[1] == sender:
            continue
        client[0].send(cipher.encrypt(f"{login}|{message}".encode()))


def client_handler(client):
    conn = client[0]
    while True:
        try:
            data = conn.recv(5120)
        except Exception:
            clients.remove(client)
            Thread(target=send_to_other, args=("server", f"Пользователь {client[1]} вышел из чата", ""),
                   daemon=True).start()
            print(f"Потерял соединение с {client[1]}")
            break
        if not data:
            clients.remove(client)
            break
        data = cipher.decrypt(data).decode("utf-8").split("|")
        login = data[0]
        msg = "|".join(data[1:])
        # print(login, msg)
        Thread(target=send_to_other, args=(login, msg, client[1])).start()


Thread(target=accept_clients).start()

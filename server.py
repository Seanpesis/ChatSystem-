import socket
import threading
import sqlite3
from datetime import datetime
import pytz

DB_FILE = "chat.db"

def setup_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)
    connection.commit()
    connection.close()

class ChatServer:
    def __init__(self, host="0.0.0.0", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        print(f"Server running on {host}:{port}")
        self.clients = {}  

    def send_message_to_client(self, sender, receiver, message):
        if receiver in self.clients:
            client_socket = self.clients[receiver]
            try:
                client_socket.sendall(f"Received from {sender} to you: {message}".encode('utf-8'))
                self.save_message(sender, receiver, message)
            except Exception as e:
                print(f"Error sending message to {receiver}: {e}")
        else:
            print(f"User {receiver} not connected.")

    def broadcast(self, sender, message, exclude=None):
        for client_name, client_socket in self.clients.items():
            if client_name != exclude:
                try:
                    client_socket.sendall(f"Received from {sender} to everyone: {message}".encode('utf-8'))
                except Exception as e:
                    print(f"Error sending message to {client_name}: {e}")

    def save_message(self, sender, receiver, message):
        local_tz = pytz.timezone('Asia/Jerusalem')  
        local_time = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')

        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO chat_history (sender, receiver, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (sender, receiver, message, local_time))
        connection.commit()
        connection.close()

    def handle_client(self, client_socket):
        try:
            client_socket.sendall("Enter your name: ".encode('utf-8'))
            name = client_socket.recv(1024).decode('utf-8').strip()
            if name in self.clients:
                client_socket.sendall("Name already taken. Disconnecting.".encode('utf-8'))
                client_socket.close()
                return

            self.clients[name] = client_socket
            print(f"{name} connected.")

            self.broadcast("Server", f"{name} has joined the chat.", exclude=name)

            while True:
                data = client_socket.recv(1024).decode('utf-8').strip()
                if ":" in data:
                    receiver, message = data.split(":", 1)
                    receiver, message = receiver.strip(), message.strip()
                    self.send_message_to_client(name, receiver, message)
                else:
                    self.broadcast(name, data, exclude=name)
                    self.save_message(name, "All", data)
        except Exception as e:
            print(f"Connection with client lost: {e}")
        finally:
            if name in self.clients:
                del self.clients[name]
                self.broadcast("Server", f"{name} has left the chat.", exclude=name)
            client_socket.close()

    def start(self):
        while True:
            client_socket, client_address = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    setup_database()
    server = ChatServer()
    server.start()

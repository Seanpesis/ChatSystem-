import socket
import threading

class ChatClient:
    def __init__(self, host="127.0.0.1", port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    print(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self):
        try:
            name = input("Enter your name: ").strip()
            self.client.sendall(name.encode('utf-8'))
            print(f"Welcome {name}! Start sending messages.\n")
            print("Instructions:")
            print("- To send a general message, just type the message and press Enter.")
            print("- To send a private message, use the format 'Recipient:Message'.\n")

            while True:
                data = input()
                self.client.sendall(data.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    client = ChatClient()
    client.send_message()

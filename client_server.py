import socket
import threading

clients = []


def handle_client(client_socket, client_address):
    clients.append(client_socket)

    welcome_message = f"Un nuovo utente è entrato nella chat: {client_address}\n"
    broadcast(welcome_message.encode())

    try:
        while True:

            message = client_socket.recv(1024).decode()

            if message == "/exit":
                break

            broadcast(message.encode(), client_socket)
    except Exception as e:
        print(f"Errore: {e}")
    finally:

        clients.remove(client_socket)
        client_socket.close()
        leave_message = f"Un utente ha lasciato la chat: {client_address}\n"
    broadcast(leave_message.encode())


def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)


def start_server():
    server_ip = '0.0.0.0'
    server_port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print("Server in ascolto sulla porta 12345...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connessione stabilita con {client_address}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    start_server()



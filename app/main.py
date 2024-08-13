
import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Sever running on port 4221....")

    try:
        client_socket, client_address = server_socket.accept()
        print(f"Connection accepted from {client_address}.")

        client_data = client_socket.recv(1024)
        print(f"client data: {client_data.decode()}")

        response = "HTTP/1.1 200 OK\r\n\r\n"
        client_socket.sendall(response.encode())
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()
        print("Server shut down")


if __name__ == "__main__":
    main()

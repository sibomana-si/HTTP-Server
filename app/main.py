
import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Sever running on port 4221....")

    try:
        client_socket, client_address = server_socket.accept()
        print(f"Connection accepted from {client_address}.")

        client_data = client_socket.recv(1024)
        client_request = client_data.decode().split('\r\n')
        request_line = client_request[0]
        request_target = request_line.split()[1]

        if request_target == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client_socket.sendall(response.encode())
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()
        print("Server shut down")


if __name__ == "__main__":
    main()

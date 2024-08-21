import asyncio
import sys
from getopt import getopt
from pathlib import Path


async def client_handler(reader, writer):
    client_address = writer.get_extra_info('peername')
    print(f"Connection accepted from {client_address}.")
    try:
        request = await reader.read(1024)
        response = await generate_response(request)
        writer.write(response.encode())
        await writer.drain()
        writer.close()
    except Exception as ex:
        print(f"ERROR in client_handler: {client_address}|{ex}")


async def generate_response(request):
    client_request = request.decode().split('\r\n')
    try:
        request_target = client_request[0].split()[1]
        base_url = request_target.split("/")[1]
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        request_headers = {}
        for line in client_request[1:]:
            if line:
                header = line.split(":")[0]
                if header in {"Host", "User-Agent", "Accept", "Accept-Encoding"}:
                    request_headers[header] = line
        user_agent_header = request_headers.get("User-Agent", "")
        accept_encoding_header = request_headers.get("Accept-Encoding", "")

        if base_url == "":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif base_url == "echo":
            response = await get_echo_response(client_request, accept_encoding_header)
        elif base_url == "files":
            response = await get_files_response(client_request)
        elif base_url == "user-agent":
            response = await get_user_agent_response(user_agent_header)

        return response
    except Exception as ex:
        print(f"ERROR in generate_response: {client_request}|{ex}")
        raise ex


async def get_echo_response(client_request, accept_encoding_header):
    request_target = client_request[0].split()[1]
    content_type = "text/plain"
    response_status_line = "HTTP/1.1 200 OK\r\n"
    response_body = request_target.split("/")[2]
    content_length = len(response_body)
    response_headers = f"Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n"

    if len(accept_encoding_header) > 0:
        request_compression = accept_encoding_header.split(":")[1].strip()
        if request_compression in compression_schemes:
            response_headers = (f"Content-Type: {content_type}\r\nContent-Encoding: {request_compression}\r\n"
                                f"Content-Length: {content_length}\r\n\r\n")
            
    response = f"{response_status_line}{response_headers}{response_body}"
    return response


async def get_files_response(client_request):
    request_data = client_request[-1]
    http_method, request_target, http_version = client_request[0].split()
    target_file = Path(file_dir + request_target.split("/")[2])
    response = "HTTP/1.1 404 Not Found\r\n\r\n"

    if http_method == "GET":
        if target_file.is_file():
            content_type = "application/octet-stream"
            response_status_line = "HTTP/1.1 200 OK\r\n"
            content_length = target_file.stat().st_size
            response_body = target_file.read_text()
            response_headers = f"Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n"
            response = f"{response_status_line}{response_headers}{response_body}"
    elif http_method == "POST":
        target_file.write_text(request_data)
        response = "HTTP/1.1 201 Created\r\n\r\n"

    return response


async def get_user_agent_response(user_agent_header):
    content_type = "text/plain"
    response_status_line = "HTTP/1.1 200 OK\r\n"
    response_body = user_agent_header.split(":")[1].strip()
    content_length = len(response_body)
    response_headers = f"Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n"
    response = f"{response_status_line}{response_headers}{response_body}"
    return response


async def main():
    host_ip = '127.0.0.1'
    host_port = 4221

    server = await asyncio.start_server(client_connected_cb=client_handler, host=host_ip, port=host_port,
                                        reuse_port=True)
    print(server)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        opts = getopt(sys.argv[1:], '', ['directory='])
        file_dir = ""
        if len(opts[0]) != 0:
            file_dir = opts[0][0][1]
        compression_schemes = {"gzip", }
        asyncio.run(main())
    except (Exception, KeyboardInterrupt) as e:
        print(f"ERROR: {e}")
    finally:
        print("Server shut down")

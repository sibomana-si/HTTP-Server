import asyncio
import sys
import gzip
import logging
import socketserver
from asyncio import StreamReader, StreamWriter
from getopt import getopt
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)


async def client_handler(reader: StreamReader, writer: StreamWriter):
    client_address: str = writer.get_extra_info('peername')
    logger.info(f"Connection accepted from {client_address}.")
    try:
        while True:
            request: bytes = await reader.read(1024)
            if not request:
                break
            client_request: list[str] = request.decode().split('\r\n')
            request_headers = {}
            for line in client_request[1:]:
                if line:
                    header = line.split(":")[0]
                    if header in {"Host", "User-Agent", "Accept", "Accept-Encoding", "Connection"}:
                        request_headers[header] = line
            connection_status: str = request_headers.get("Connection", "")
            response: bytes = await generate_response(client_request, request_headers)
            writer.write(response)
            await writer.drain()
            if connection_status == "close":
                break
    except Exception as ex:
        logger.exception(f"ERROR in client_handler: {client_address}|{ex}")
    finally:
        writer.close()
        await writer.wait_closed()

async def generate_response(client_request: list[str], request_headers: dict[str, str]) -> bytes:
    try:
        request_target: str = client_request[0].split()[1]
        base_url: str = request_target.split("/")[1]
        user_agent_header: str = request_headers.get("User-Agent", "")
        accept_encoding_header: str = request_headers.get("Accept-Encoding", "")
        response = bytes("HTTP/1.1 404 Not Found\r\n\r\n", "utf-8")

        if base_url == "":
            response = "HTTP/1.1 200 OK\r\n\r\n".encode()
        elif base_url == "echo":
            response: bytes = await get_echo_response(client_request, accept_encoding_header)
        elif base_url == "files":
            response: bytes = await get_files_response(client_request)
        elif base_url == "user-agent":
            response: bytes = await get_user_agent_response(user_agent_header)

        return response
    except Exception as ex:
        raise ex


async def get_echo_response(client_request: list[str], accept_encoding_header: str) -> bytes:
    request_target: str = client_request[0].split()[1]
    content_type = "text/plain"
    response_status_line: bytes = "HTTP/1.1 200 OK\r\n".encode()
    response_body_plain: str = request_target.split("/")[2]
    content_length: int = len(response_body_plain)
    response_headers: bytes = f"Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n".encode()
    response_body: bytes = response_body_plain.encode()

    if len(accept_encoding_header) > 0:
        client_compression_schemes: list[str] = accept_encoding_header.split(":")[1].split(",")
        for client_compression_scheme in client_compression_schemes:
            response_compression_scheme = client_compression_scheme.strip()
            if response_compression_scheme in server_compression_schemes:
                response_body: bytes = gzip.compress(response_body, mtime=0)
                content_length: int = len(response_body)
                response_headers: bytes = (f"Content-Type: {content_type}\r\n"
                                    f"Content-Encoding: {response_compression_scheme}\r\n"
                                    f"Content-Length: {content_length}\r\n\r\n").encode()

    response: bytes = response_status_line + response_headers + response_body
    return response


async def get_files_response(client_request: list[str]) -> bytes:
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

    return response.encode()


async def get_user_agent_response(user_agent_header: str) -> bytes:
    content_type = "text/plain"
    response_status_line = "HTTP/1.1 200 OK\r\n"
    response_body = user_agent_header.split(":")[1].strip()
    content_length = len(response_body)
    response_headers = f"Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n"
    response = f"{response_status_line}{response_headers}{response_body}"
    return response.encode()


async def main():
    host_ip = '127.0.0.1'
    host_port = 4221
    server: socketserver = await asyncio.start_server(client_connected_cb=client_handler, host=host_ip,
                                        port=host_port, reuse_port=True)
    logger.info(server)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        opts = getopt(sys.argv[1:], '', ['directory='])
        file_dir = ""
        if len(opts[0]) != 0:
            file_dir = opts[0][0][1]
        server_compression_schemes = {"gzip", }
        asyncio.run(main())
    except (Exception, KeyboardInterrupt) as e:
        logger.exception("TERMINAL ERROR:")
    finally:
        logger.info("Server shut down")

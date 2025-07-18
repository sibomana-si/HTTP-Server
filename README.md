[![progress-banner](https://backend.codecrafters.io/progress/http-server/a14d9049-3093-49b4-919c-8fd43b6d90e3)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

# Description

A lightweight HTTP server implementation that handles basic HTTP requests and responses.

This server was built as part of the [CodeCrafters HTTP Server Challenge](https://codecrafters.io/challenges/http-server).

## Features

- Support for HTTP/1.1 protocol
- Content compression with gzip
- Connection persistence
- Asynchronous request handling with asyncio
- Multiple endpoint support:
  - `/` - Returns 200 OK
  - `/echo/<message>` - Echoes back the message
  - `/user-agent` - Returns the User-Agent header from the request

## Usage

Run the server with:

```bash
python main.py [--directory=<directory_path>]
```

Where:
- `--directory`: Optional parameter to specify the directory for file operations


## API Endpoints

### Root Endpoint
- **URL**: `/`
- **Method**: GET
- **Response**: Returns a 200 OK status

### Echo Endpoint
- **URL**: `/echo/<message>`
- **Method**: GET
- **Response**: Returns the message with a 200 OK status
- **Features**: Supports gzip compression if the client accepts it

### User-Agent Endpoint
- **URL**: `/user-agent`
- **Method**: GET
- **Response**: Returns the User-Agent header from the request

### Files Endpoint
- **URL**: `/files/<filename>`
- **Methods**: 
  - **GET**: Retrieves the content of the specified file
  - **POST**: Creates or updates the specified file with the request body
- **Response**: 
  - 200 OK with file content (GET)
  - 201 Created (POST)
  - 404 Not Found if the file doesn't exist (GET)

## Technical Details

- Supports HTTP headers parsing and generation
- Handles persistent connections with proper Connection header handling
- Built with Python's asyncio for handling concurrent connections
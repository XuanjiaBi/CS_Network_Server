#!/usr/bin/env python3

# GET /index.html HTTP/1.1
# Host: localhost:4457
# Connection: keep-alive
# sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"
# sec-ch-ua-mobile: ?0
# sec-ch-ua-platform: "Windows"
# DNT: 1
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
# Sec-Fetch-Site: none
# Sec-Fetch-Mode: navigate
# Sec-Fetch-User: ?1
# Sec-Fetch-Dest: document
# Accept-Encoding: gzip, deflate, br
# Accept-Language: en-US,en;q=0.9
# Cookie: csrftoken=Ke7jl5xTGXg1UFxk2PlYQapAUOlWC1hEJsS6xAMXqwZ6nLA4fFpb55Ggj0VxtqI0;
import os.path
import socket
import sys
import queue
import select
import os

from file_reader import FileReader


class Jewel:
    # Note, this starter example of using the socket is very simple and
    # insufficient for implementing the project. You will have to modify this
    # code.
    def __init__(self, port, file_path, file_reader):
        self.file_path = file_path
        self.file_reader = file_reader
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", port))
        print("bind successfully")
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #server.setblocking(0)
        server.listen(5)
        # Sockets from which we expect to read
        inputs = [server]

        # Sockets to which we expect to write

        outputs = []

        # Outgoing message queues (socket: Queue)
        message_queues = {}

        while inputs:
            # Wait for at least one of the sockets to be ready for processing
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                if s is server:
                    # A "readable" socket is ready to accept a connection
                    (client, address) = s.accept()
                    # print("[CONN] Connection from " + str(address) + " on port " + str(port))
                    # this is connection not server
                    #client.setblocking(0)
                    inputs.append(client)
                    # Give the connection a queue for data we want to send
                    message_queues[client] = queue.Queue()
                else:
                    data = s.recv(2 ** 18)
                    if data:
                        # A readable client socket has data
                        # print (sys.stderr, 'received "%s" from %s' % (data, s.getpeername()))
                        message_queues[s].put(data)
                        # Add output channel for response
                        if s not in outputs:
                            outputs.append(s)
                        else:
                            # Interpret empty result as closed connection
                            # print ( sys.stderr, 'closing', address,'after reading no data')
                            # Stop listening for input on the connection
                            if s in outputs:
                                outputs.remove(s)
                            inputs.remove(s)
                            s.close()
                            # Remove message queue
                            del message_queues[s]
            for s in writable:
                #s.setblocking(0)
                try:
                    data = message_queues[s].get_nowait()
                except queue.Empty:
                    print("")
                    outputs.remove(s)
                else:
                    print(data)
                    sys.stdout.write("[CONN] Connection from " + str(address) + " on port " + str(port)+"\n")
                    data = data.decode('utf-8')
                    requestType = data.split("\n")[0].split()[0]
                    path = data.split("\n")[0].split()[1]
                    file_context = file_reader.get(file_path + path, "")
                    header = file_reader.head(file_path + path, "")
                    ## GET::
                    # ------------------------------------------------------------------------
                if requestType == "GET":
                    if file_context is None:
                        sys.stdout.write("[ERRO] [" + str(address) + ":" + str(port) + "] " + str(
                            requestType) + " request returned error 404\n")
                        client.send(b"HTTP/1.1 404 Not Found\r\n")
                        client.sendall("0".encode())
                        client.sendall(("Content-Length: {0}\r\n\r\n").encode())
#                       client.sendall("Server: xb4syf\r\n\r\n".encode())
                        file_context = "<html><body><h1>{}</h1></body></html>".format("Invalid Path")
                        client.sendall(file_context.encode())
                    elif isinstance(file_context, str):
                        client.send(b"HTTP/1.1 200 OK\r\n")
                        client.sendall("0".encode())
                        client.sendall(("Content-Length: {:}\r\n\r\n".format(header)).encode())
                    else:
                        # print("Content-Length: {:}\r\n\r\n".format(header))
                        sys.stdout.write("[REQU] [" + str(address) + ":" + str(port) + "] " + str(
                            requestType) + " request for " + str(path) + "\n")
                        # To handle the errors:
                        try:
                            client.send(b"HTTP/1.1 200 OK\r\n")
                            client.sendall("Server: xb4syf".encode())
                            client.sendall(("Content-Length: {:}\r\n\r\n".format(header)).encode())
                            client.sendall(file_context)
                        except BlockingIOError or BrokenPipeError:
                            return
                        print("succeed")
                if requestType == "HEAD":
                    if header is None:
                        # print("[ERRO] [" + str(address) + ":" + str(port) + "] " + str(requestType) + " request returned error 404\n")
                        client.send(b"HTTP/1.1 404 Not Found\r\n")
                        client.sendall("0".encode())
                        client.sendall("Content-Length: {0}\r\n\r\n".encode())
                    elif isinstance(header, str):
                        # if it is a dir send out the string that indicate the dic
                        client.send(b"HTTP/1.1 200 OK\r\n")
                        client.sendall(header.encode())
                        client.sendall(("Content-Length: {:}\r\n\r\n".format(header)).encode())
                        del message_queues[s]
                    else:
                        sys.stdout.write("[REQU] [" + str(address) + ":" + str(port) + "] " + str(
                            requestType) + " request for " + str(path) + "\n")
                        client.send(b"HTTP/1.1 200 OK\r\n")
                        client.sendall(("Content-Length: {:}\r\n\r\n".format(header)).encode())
                if not (requestType == "GET" or requestType == "HEAD"):
                    sys.stdout.write("[ERRO] [" + str(address) + ":" + str(port) + "] " + str(
                        requestType) + " request returned error 501\n")
                    client.send(b"HTTP/1.1 501 Not Implemented\r\n")
                    client.sendall("0".encode())
                    client.sendall(("Content-Length: {:}\r\n\r\n".format(header)).encode())
            # # Handle "exceptional conditions"
            for s in exceptional:
                print("Handling exception for: " + str(s.getpeername()) + " \n")
                inputs.remove(s)
                for s in outputs:
                    outputs.remove(s)
                s.close()
                # remove message queue
                del message_queues[s]
if __name__ == "__main__":
    # port = int(sys.argv[1])
    # file_path = sys.argv[2]
    port = int(os.environ.get('PORT', 5000))
    file_path = './EC_root'
    FR = FileReader()

    J = Jewel(port, file_path, FR)
    ## port = int(os.environ.get('PORT',5000))
    ## filde_path = 'file_Path'

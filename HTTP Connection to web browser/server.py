                            #######################*BONUS CODE*############################

import socket
from os.path import exists
from urllib.parse import unquote_plus
#request_parser function takes the incoming data and extracts the method, filename, HTTP version, and body
def request_parser(data):
    print("data received in bytes:")  
    print(data)
    print("--------------------------------------------------------------------------------------------------")
    data = str(data, 'UTF-8')
    method = data.split(' /')[0]
    filename = data.split(' ')[1][1:]
    http_ver = data.split('\r\n')[0][-3:]
    body = ""
    if method == "POST":
        body = data.split("\r\n\r\n")[1]
    return method, filename, http_ver, body

#connection_parser function takes the incoming data and checks if the connection is going to be closed or kept alive.
def connection_parser(data):
    data = str(data, 'UTF-8')
    try:
        connection = data.split("Connection: ")[1][0]
        if connection == 'k':
            return 'k'
        else:
            return 'c'
    except IndexError:
        return 'c'

# keep_alive_parser function takes the incoming data and extracts the timeout value for a keep-alive connection.
def keep_alive_parser(data):
    data = str(data, 'UTF-8')
    try:
        timeout = data.split("Keep-Alive: ")[1].split(", ")[0].split("=")[1]
        print("Time out: ", timeout)
        return int(timeout)
    except IndexError:
        return 10


def get_handler(filename, sock, http_ver):
    try:
        with open(filename, "r") as f:
            body = bytes(f.read(), 'utf-8')
    except FileNotFoundError:
        data_to_be_send = "HTTP/" + http_ver + " 404 Not Found\r\n\r\n"
        data_to_be_send = bytes(data_to_be_send, 'utf-8')
        sock.send(data_to_be_send)
        return

    data_to_be_send = "HTTP/" + http_ver + " 200 OK\r\n\r\n"
    data_to_be_send = bytes(data_to_be_send, 'utf-8')
    data_to_be_send = data_to_be_send + body
    print("Data to be sent in bytes:")
    print(data_to_be_send[:1024])
    print("------------------------------------------")
    sock.send(data_to_be_send)
    print("Data has been sent")



def post_handler(filename, body, sock, http_ver):
    body = unquote_plus(body)


    print("body to be written in file:")
    print(body)
    print("------------------------------------------")
    f = open(filename, "w+")
    f.write(body)
    print("body has been wrote")
    f.close()
    ok_message = "HTTP/" + http_ver + " 200 OK\r\nContent-Type: text/html\r\n\r\n"
    ok_message = bytes(ok_message, 'utf-8')
    sock.send(ok_message)
    print("OK message has been sent")



def Main():
    host = "127.0.0.1"
    port = 65432
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("--------------------------------------------------------------------------------------------------")
    print("socket binded to port", port)

    s.listen()
    print("socket is listening")
    print("--------------------------------------------------------------------------------------------------")

    while True:
        c, addr = s.accept()
        print('Connected to :', addr[0], ':', addr[1])

        while True:
            data = b''
            try:
                recv_data = []
                recv_data.append(c.recv(1024))
                c.settimeout(0.5)
                i = 0
                while recv_data[i]:
                    data += recv_data[i]
                    i += 1
                    recv_data.append(c.recv(1024))
                c.settimeout(None)
            except TimeoutError:
                c.settimeout(None)

            if not data:
                break

            method, filename, http_ver, body = request_parser(data)
            print("method: " + method)
            print("filename: " + filename)
            print("http_ver: " + http_ver)
            print("--------------------------------------------------------------------------------------------------")

            if method == "POST":
                print("in POST")
                post_handler(filename, body, c, http_ver)
                print(
                    "--------------------------------------------------------------------------------------------------")

            elif method == "GET":
                print("in GET")
                is_exist = exists(filename)
                if is_exist:
                    print("file exists")
                    print("------------------------------------------")
                    get_handler(filename, c, http_ver)
                    print(
                        "--------------------------------------------------------------------------------------------------")
                else:
                    print("file not exists")
                    error_message = "HTTP/" + http_ver + " 404 Not Found\r\n\r\n"
                    error_message = bytes(error_message, 'utf-8')
                    c.send(error_message)
                    print("Error message has been sent")
                    print(
                        "--------------------------------------------------------------------------------------------------")

            if http_ver == "1.1":
                connection = connection_parser(data)
                if connection == 'k':
                    timeout = keep_alive_parser(data)
                    print("Waiting... 1.1, keep-alive")
                    c.settimeout(timeout)
                else:
                    print("Not waiting... 1.1, close")
                    break
            else :
                print("Not waiting... 1.0")
                break

        if data.decode().strip() == "exit":
            
            c.close()
            
            print("connection closed")
            print("--------------------------------------------------------------------------------------------------")
            print("--------------------------------------------------------------------------------------------------")
            break

    s.close()


if __name__ == '__main__':
    Main()

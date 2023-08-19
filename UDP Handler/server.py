# server
import socketserver
import binascii
import os
import signal
import threading

chunk_size = 1000
recseq = 0
recack = -1
initiate = 0
connection = 0





class MyUDPHandler(socketserver.BaseRequestHandler):
    initiate = 0
    sequence = 0
    recseq = 0
    chunk = 0

    def handle(self):
        global j, initiate, connection, sequence, err, mydomain, browser, formats, encodings, languages, contype, chunk, contenttype, recseq, timer
        socket = self.request[1]
        socket.settimeout(2)

        # data = self.request[0].strip()
        def finishconn(sequence, recseq):
            print("Timed out while waiting for input")
            send_data = "end"
            initiate = 0
            connection = 0
            checksum = binascii.crc32(send_data.encode())
            message = str(sequence).zfill(10) + str(recseq).zfill(10) + str(checksum).zfill(
                10) + "001" + send_data
            sequence = sequence + len(send_data)
            socket.sendto(message.encode(), self.client_address)

        if initiate == 0:
            data = self.request[0].strip()
        else:
            def read_input():
                data = self.request[0].strip()
                return data

            timer = threading.Timer(4.0, lambda: finishconn(sequence, recseq))
            timer.start()
            try:
                data = read_input()
                timer.cancel()
            except:
                timer.cancel()
                pass
        data = data.decode()
        print(data)
        recseq = int(data[:10])
        data = data[10:]
        recack = int(data[:10])
        data = data[10:]
        reccheck = int(data[:10])
        data = data[10:]
        syn = int(data[0])
        ack = int(data[1])
        fin = int(data[2])
        data = data[3:]
        checking = binascii.crc32(data.encode())

        if fin:
            send_data = "end"
            initiate = 0
            connection = 0
            checksum = binascii.crc32(send_data.encode())
            message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                10) + "001" + send_data
            sequence = sequence + len(send_data)
            socket.sendto(message.encode(), self.client_address)
        if syn == 1 and ack == 0 and fin == 0:
            initiate = 1
            connection = 0
            j = -1
            err = 0
            sequence = 0
            initiate = 1
            send_data = "ok"
            checksum = binascii.crc32(send_data.encode())
            message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                10) + "110" + send_data
            sequence = sequence + len(send_data)
            socket.sendto(message.encode(), self.client_address)

        elif syn == 0 and ack == 1 and initiate == 1 and connection == 0 and fin == 0:
            connection = 1

        elif connection == 1 and data[:3].upper() == "GET" and fin == 0:
            datalines = data.split('\n')
            temp = datalines[0].split(" ")
            type, path, version = temp[0], temp[1], temp[2]
            datalines = datalines[1:]
            for line in datalines:
                header, attributes = line.split(" ", 1)
                if header == "Host:":
                    mydomain = attributes
                elif header == "User-Agent:":
                    browser = attributes
                elif header == "Accept:":
                    formats = attributes.split(',')
                elif header == "Accept-Encoding:":
                    encodings = attributes.split(',')
                elif header == "Accept-Language:":
                    languages = attributes.split(',')
                elif header == "Connection:":
                    contype = attributes

            current_dir = os.getcwd()
            if os.path.exists(current_dir + path):
                with open(current_dir + path, 'r') as file:
                    file = file.read()
                chunk = [0 for i in range(int(len(file) / chunk_size) + 1)]
                j = 0
                for i in range(0, len(file), chunk_size):
                    chunk[j] = file[i:i + chunk_size]
                    j = j + 1
                j = -1

                send_data = "HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length:" + str(len(file)) + "\n"
                checksum = binascii.crc32(send_data.encode())
                message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                    10) + "000" + send_data
                sequence = sequence + len(send_data)
                socket.sendto(message.encode(), self.client_address)

            else:
                send_data = "HTTP/1.1 404 Not_Found\nContent-Type: text/html; charset=utf-8\nContent-Length: 132\nConnection: close"
                checksum = binascii.crc32(send_data.encode())
                message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                    10) + "001" + send_data
                sequence = sequence + len(send_data)
                socket.sendto(message.encode(), self.client_address)
                chunk = ""

        elif connection and data[:4].upper() == "POST" and fin == 0:
            splitter = ""
            datalines = data.split('\n')
            if (len(datalines) > 1):
                temp = datalines[0].split(" ")
                type, path, version = temp[0], temp[1], temp[2]
                datalines = datalines[1:3]
                for line in datalines:
                    header, attributes = line.split(" ", 1)
                    if header == "Host:":
                        mydomain = attributes
                    elif header == "User-Agent:":
                        browser = attributes
                    elif header == "Accept:":
                        formats = attributes.split(',')
                    elif header == "Accept-Encoding:":
                        encodings = attributes.split(',')
                    elif header == "Accept-Language:":
                        languages = attributes.split(',')
                    elif header == "Connection:":
                        contype = attributes
                    elif header == "Content-Type:":
                        contenttype = attributes.split(" boundary=")
                        splitter = contenttype[1]

                datalines = data.split('--' + splitter)
                datalines = datalines[1:-1]
                names = [0 for i in range(int(len(datalines)))]
                values = [0 for i in range(int(len(datalines)))]
                k = 0
                for line in datalines:
                    temp = line.split('\n\n')
                    values[k] = temp[-1].split('\n')[0]
                    temp = temp[0].split("\"")
                    names[k] = temp[1]
                    k = k + 1
                print(names)
                print(values)
            send_data = "end"
            initiate = 0
            connection = 0
            checksum = binascii.crc32(send_data.encode())
            message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                10) + "001" + send_data
            sequence = sequence + len(send_data)
            socket.sendto(message.encode(), self.client_address)


        elif connection and 'chunk' in globals():
            if (j + 1) < len(chunk) and fin == 0:
                if recack == sequence and checking == reccheck:
                    j = j + 1
                    err = 0
                else:
                    sequence = sequence - len(chunk[j])
                    err = err + 1
                send_data = chunk[j]
                checksum = binascii.crc32(send_data.encode())
                message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                    10) + "000" + send_data
                sequence = sequence + len(send_data)
                socket.sendto(message.encode(), self.client_address)
            else:
                send_data = "end"
                initiate = 0
                connection = 0
                checksum = binascii.crc32(send_data.encode())
                message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                    10) + "001" + send_data
                sequence = sequence + len(send_data)
                socket.sendto(message.encode(), self.client_address)
            if err > 100:
                send_data = "end"
                initiate = 0
                connection = 0
                checksum = binascii.crc32(send_data.encode())
                message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                    10) + "001" + send_data
                sequence = sequence + len(send_data)
                socket.sendto(message.encode(), self.client_address)
        else:
            send_data = "error, Invalid request!"
            initiate = 0
            connection = 0
            checksum = binascii.crc32(send_data.encode())
            message = str(sequence).zfill(10) + str(recseq + len(data)).zfill(10) + str(checksum).zfill(
                10) + "001" + send_data
            sequence = sequence + len(send_data)
            socket.sendto(message.encode(), self.client_address)
        # timer = threading.Timer(4.0, lambda: finishconn(sequence, recseq))
        # timer.start()


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()

# client
import socket
import binascii
import select
import threading


def finishconn(sequence):
    print("Timed out while waiting for input")
    data = "end"
    checksum = binascii.crc32(data.encode())
    message = str(sequence).zfill(10) + str(last_ack).zfill(10) + str(checksum).zfill(10) + "001" + data
    sock.sendto(bytes(message, "utf-8"), (HOST, PORT))

first=1
rdata = ""
recseq = -1
j = 0
win = 5
last_ack = 0
chunk_size = 1000
window_start = 0
sequence = 0
HOST, PORT = "localhost", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)

checksum = binascii.crc32("dataa".encode())
checksum = binascii.crc32("dataa".encode())

data = "begin"
checksum = binascii.crc32(data.encode())
message = str(sequence).zfill(10) + str(recseq + 1).zfill(10) + str(checksum).zfill(10) + "100" + data
sequence = sequence + len(data)
sock.sendto(bytes(message, "utf-8"), (HOST, PORT))
readable, writable, exceptional = select.select([sock], [], [], 5)


# if sock in readable:
#     received = str(sock.recv(chunk_size * 3), "utf-8")
# else:
#     print("No data received within 5 seconds")



def read_input():
    received = str(sock.recv(chunk_size * 3), "utf-8")
    return received


timer = threading.Timer(1.0,print(""))
timer.start()
try:
    received = read_input()
    timer.cancel()
except:
    timer.cancel()
    pass
if 'received' in locals():
    # received = str(sock.recv(chunk_size * 3), "utf-8")
    recseq = int(received[:10])
    received = received[10:]
    recack = int(received[:10])
    received = received[10:]
    reccheck = int(received[:10])
    received = received[10:]
    synflag = int(received[0])
    ackflag = int(received[1])
    finflag = int(received[2])
    received = received[3:]

    if synflag == 1 and ackflag == 1:
        data = "start"
        checksum = binascii.crc32(data.encode())
        message = str(sequence).zfill(10) + str(recseq + len(received)).zfill(10) + str(checksum).zfill(10) + "010" + data
        last_ack = recseq + len(received)
        sequence = sequence + len(data)
        sock.sendto(bytes(message, "utf-8"), (HOST, PORT))
        data = input("Enter your Get request: ")
        err = 0
        while True:
            line = input()
            if line:
                data += "\n" + line
                err = 0
            else:
                data += "\n"
                err = err + 1
                if err > 1:
                    err = 0
                    break
        print("done")

        # data = "GET /index.html HTTP/1.1\nHost: example.com\nUser-Agent: Mozilla/5.0\nAccept-Language: en-us\nAccept-Encoding: gzip, deflate\nConnection: keep-alive\n"
        checksum = binascii.crc32(data.encode())
        message = str(sequence).zfill(10) + str(recseq + len(received)).zfill(10) + str(checksum).zfill(
            10) + "000" + data
        last_ack = recseq + len(received)
        sequence = sequence + len(data)
        sock.sendto(bytes(message, "utf-8"), (HOST, PORT))
    while True:

        def read_input():
            received = str(sock.recv(chunk_size * 3), "utf-8")
            return received


        timer = threading.Timer(30.0, lambda: finishconn(sequence))
        timer.start()
        try:
            received = read_input()
            timer.cancel()
        except:
            timer.cancel()
            pass
        recseq = int(received[:10])
        received = received[10:]
        recack = int(received[:10])
        received = received[10:]
        reccheck = int(received[:10])
        received = received[10:]
        synflag = int(received[0])
        ackflag = int(received[1])
        finflag = int(received[2])
        received = received[3:]
        checksum = binascii.crc32(received.encode())
        if first:
            first=0
            print(received.split('\n')[0].split(' ')[-2:])
        if last_ack == recseq and checksum == reccheck:
            data = "ack"
            checksum = binascii.crc32(data.encode())
            message = str(sequence).zfill(10) + str(recseq + len(received)).zfill(10) + str(checksum).zfill(
                10) + "010" + data
            last_ack = recseq + len(received)
            sequence = sequence + len(data)
            sock.sendto(bytes(message, "utf-8"), (HOST, PORT))
            if received != "end":
                rdata = rdata + received

        else:
            data = "ack"
            checksum = binascii.crc32(data.encode())
            message = str(sequence).zfill(10) + str(last_ack).zfill(10) + str(checksum).zfill(10) + "010" + data
            sock.sendto(bytes(message, "utf-8"), (HOST, PORT))
        if finflag:
            print(rdata)
            print("connection dropped")
            break
else:
    print("connection time out!")
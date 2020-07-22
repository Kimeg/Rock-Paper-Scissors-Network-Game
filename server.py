from collections import defaultdict
import socket
import threading
import sys

BYTE_SIZE = 1024
PORT = int(sys.argv[1])
SERVER = socket.gethostbyname(socket.gethostname());
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT = "quit"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
server.bind(ADDR)
clients = []

CONN_LIMIT = 2
ids = defaultdict(int)

def handle_client(conn, addr):
    print(f"\n[NEW CONNECTION] USER_{ids[addr]} connected.\n")

    connected = True
    while connected:
        msg_length = conn.recv(BYTE_SIZE).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT:
                connected = False

            content = "\n[USER_{0}] : {1}\n".format(str(ids[addr]), msg)
            print(content)
            
            for c in clients:
                if c == conn:
                    continue
                c.send(msg.encode(FORMAT))

    print(f"\n[DISCONNECTED] USER_{ids[addr]}\n")
    conn.close()
    return

def main():
    print("\n[SERVER START]\n")

    server.listen()
    print(f"\n[LISTENING] Server IP-Address : {SERVER}\n")

    count = 0
    while True:
        count += 1
        conn, addr = server.accept()
        
        if len(clients)==CONN_LIMIT:
            conn.close()
            continue
            
        ids[addr] = count
        for c in clients:
            c.send(f"\n[USER_{ids[addr]} HAS JOINED]\n".encode(FORMAT))

        clients.append(conn)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
    return

if __name__=="__main__":
    main()


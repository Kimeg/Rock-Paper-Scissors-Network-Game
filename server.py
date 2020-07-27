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

CONN_LIMIT = 2

class Server:
    def __init__(self, server):
        self.server = server
        self.clients = []
        self.ids = defaultdict(int)

    def handle_client(self, conn, addr):
        # conn and addr objects are related to a specific client.
        print(f"\n[NEW CONNECTION] USER_{self.ids[addr]} connected.\n")

        connected = True
        while connected:
            # Receives an incoming message from the client.
            msg_length = conn.recv(BYTE_SIZE).decode(FORMAT)

            # We have to check message length to differentiate between messages 
            # sent by the client and an empty message. 
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT:
                    connected = False

                content = "\n[USER_{0}] : {1}\n".format(str(self.ids[addr]), msg)
                print(content)
                
                # Sends the client's message to all other clients
                for c in self.clients:
                    if c == conn:
                        continue
                    c.send(msg.encode(FORMAT))

        print(f"\n[DISCONNECTED] USER_{self.ids[addr]}\n")
        conn.close()
        return

def main():
    print("\n[SERVER START]\n")
    # Generate a Server object to store connection info and clients
    server = Server(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    # Server's socket object binds to the specified port number of localhost IP address
    server.server.bind(ADDR)
    # Server's socket starts to listen to incoming connections from client(s).
    server.server.listen()
    print(f"\n[LISTENING] Server IP-Address : {SERVER}\n")

    count = 0
    # Interactions between the server and potential clients happen inside the following while loop.
    while True:
        count += 1
        # The following line waits for a client's request for connection.
        conn, addr = server.server.accept()

        # If the number of connected clients reaches it's limit, no further requests are accepted.
        if len(server.clients)==CONN_LIMIT:
            conn.close()
            continue
        
        # Server object keeps track of its clients by assigning them unique ID's
        # Once a new client is connected to the server, a message is sent to each client 
        # to inform that a new client has joined the server.
        server.ids[addr] = count
        for c in server.clients:
            c.send(f"\n[USER_{server.ids[addr]} HAS JOINED]\n".encode(FORMAT))

        # The connection object between the server and the client is added to Server object's clients list
        # In short, this is just to keep track of all connected clients for latter network processing.
        server.clients.append(conn)

        # From here, a new thread is assigned to deal with the connection between the server and THIS SPECIFIC client.
        # Basically, every new client will be assigned a new thread to be handled.
        thread = threading.Thread(target=server.handle_client, args=(conn, addr))
        thread.start()
    return

if __name__=="__main__":
    main()


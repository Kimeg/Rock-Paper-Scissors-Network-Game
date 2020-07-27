from DB import *
import socket
import threading
import sys

BYTE_SIZE = 1024
PORT = int(sys.argv[1])

FORMAT = "utf-8"
DISCONNECT= "quit"
SERVER = socket.gethostbyname(socket.gethostname());
ADDR = (SERVER, PORT)

def mapper(v):
    if v in PAPERS:
        return 'P'
    elif v in SCISSORS:
        return 'S'
    elif v in ROCKS:
        return 'R' 
    return None

class Client:
    def __init__(self, client):
        self.client = client
        self.connection = True
        self.received = False
        self.sent = False

        self.received_msg = None
        self.sent_msg = None

    def listen(self):
        # message from the server
        from_server = self.client.recv(BYTE_SIZE).decode(FORMAT)

        # Checks if message received from the server is the one from another client (opponent).
        if not from_server=='' and not 'USER' in from_server:
            if self.received:
                return

            # Received a message from the opponent.
            self.received = True

            if self.sent:        
                # if you already have sent your message to the opponent,
                # reveals messages from both sides.
                mine = mapper(self.sent_msg)
                opp = mapper(from_server)

                print(f"\nYOU : {MAPPED[mine]} VS OPPONENT : {MAPPED[opp]}\n")
                print(f"\n{CASES[mine+opp]}\n")
                    
                self.received = False
                self.sent = False
            else:
                # if you have not yet sent your message to the opponent,
                # you are only notified of successful message retrival.
                # (this makes sense since you have to send yours before revealing opponent's.)
                print("\nOPPONENT HAS SENT ROCK/PAPER/SCISSORS.\n\nYOUR TURN.\n")
                self.received_msg = from_server
        return

    def send(self):
        while True:
            # If you have already sent a message, then you cannot send another one until 
            # you received a message from the opponent.
            if self.sent:
                continue

            # Type one of the three choices to be sent to the opponent.
            msg = input('\nType one of the following:\nRock/Paper/Scissors\n')
            message = msg.encode(FORMAT)
            msg_length = len(message)

            send_length = str(msg_length).encode(FORMAT)
            send_length += b' '*(BYTE_SIZE-len(send_length))

            try:
                if self.received:
                    # If you have received a message from the opponent,
                    # reveals messages from both sides.
                    mine = mapper(message.decode(FORMAT))
                    opp = mapper(self.received_msg)
                    try:
                        print(f"\nYOU : {MAPPED[mine]} VS OPPONENT : {MAPPED[opp]}\n")
                        print(f"\n{CASES[mine+opp]}\n")
                        self.client.send(send_length)
                        self.client.send(message)
                        self.sent = False
                        self.received = False
                    except:
                        print(f"\nInvalid input. Type one of the following:\nRock/Paper/Scissors\n")


                else:
                    # If you have not yet received a message from the opponent,
                    # you are informed that you have sent a message.
                    self.sent_msg = message.decode(FORMAT)
                    mine = mapper(self.sent_msg)
                    try:
                        print(f"\nYOU SENT {MAPPED[mine]}\n\nWAITING FOR OPPONENT's TURN.\n")
                        self.sent = True
                        self.client.send(send_length)
                        self.client.send(message)
                    except:
                        print(f"\nInvalid input. Type one of the following:\nRock/Paper/Scissors\n")
                    
            except socket.error as e:
                self.connection = False
                print(e)
                break
        return

def main():
    client = Client(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    client.client.connect(ADDR)

    # Starts a new thread that ONLY deals with sending messages to the server.
    thread = threading.Thread(target=client.send)
    thread.start()

    # As long as the connection is valid, the client listens to incoming messages from the server.
    # Since a single thread cannot handle both listening and sending tasks, we have assigned one thread
    # for handling message sending and another thread for listening to incoming messages.
    while client.connection:
        client.listen()
    client.client.close()

if __name__=="__main__":
    main()

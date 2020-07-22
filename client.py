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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
client.connect(ADDR)

connection = True
received = False
sent = False

received_msg = None
sent_msg = None

def mapper(v):
    if v in PAPERS:
        return 'P'
    elif v in SCISSORS:
        return 'S'
    elif v in ROCKS:
        return 'R' 
    return None

def listen(client):
    global sent, received, received_msg, sent_msg
    from_server = client.recv(BYTE_SIZE).decode(FORMAT)
    if not from_server=='' and not 'USER' in from_server:
        if received:
            return

        received = True

        if sent:        
            mine = mapper(sent_msg)
            opp = mapper(from_server)
            print(f"\nYOU : {MAPPED[mine]} VS OPPONENT : {MAPPED[opp]}\n")
            print(f"\n{CASES[mine+opp]}\n")
                
            received = False
            sent = False
        else:
            print("\nOPPONENT HAS SENT ROCK/PAPER/SCISSORS.\n\nYOUR TURN.\n")
            received_msg = from_server
    return

def send():
    global sent, received, received_msg, sent_msg
    while True:
        if sent:
            continue

        msg = input('\nType one of the following:\nRock/Paper/Scissors\n')
        message = msg.encode(FORMAT)
        msg_length = len(message)

        send_length = str(msg_length).encode(FORMAT)
        send_length += b' '*(BYTE_SIZE-len(send_length))

        try:
            if received:
                mine = mapper(message.decode(FORMAT))
                opp = mapper(received_msg)
                try:
                    print(f"\nYOU : {MAPPED[mine]} VS OPPONENT : {MAPPED[opp]}\n")
                    print(f"\n{CASES[mine+opp]}\n")
                    client.send(send_length)
                    client.send(message)
                    sent = False
                    received = False
                except:
                    print(f"\nInvalid input. Type one of the following:\nRock/Paper/Scissors\n")


            else:
                sent_msg = message.decode(FORMAT)
                mine = mapper(sent_msg)
                try:
                    print(f"\nYOU SENT {MAPPED[mine]}\n\nWAITING FOR OPPONENT's TURN.\n")
                    sent = True
                    client.send(send_length)
                    client.send(message)
                except:
                    print(f"\nInvalid input. Type one of the following:\nRock/Paper/Scissors\n")
                
        except socket.error as e:
            connection = False
            print(e)
            break
    return

def main():
    thread = threading.Thread(target=send)
    thread.start()
    while connection:
        listen(client)
    client.close()

if __name__=="__main__":
    main()
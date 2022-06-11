import socket
from threading import Thread
import signal 
import sys
import os


def registration():
    regtosend = f'REGISTER TOSEND {sys.argv[1]}\n\n'
    regtorecv = f'REGISTER TORECV {sys.argv[1]}\n\n'
    while True:
        try: 
            client_socket_recv.send(regtorecv.encode('utf8'))
            respo = client_socket_recv.recv(BUFFERSIZE).decode('utf8')
            print(respo)
            if respo == f'ERROR 101 No user registered\n\n':
                exit()
        except:
            continue
        else:
            break

    while True:
        try: 
            client_socket_send.send(regtosend.encode('utf8'))
            respo = client_socket_send.recv(BUFFERSIZE).decode('utf8')
            print(respo)
            if respo == f'ERROR 101 No user registered\n\n':
                exit()
        except:
            continue
        else:
            return
    

def send_msg():
    while True:
        try:
            inp = str(input())
            arr = inp.split()
            tempusr=arr[0]
            usr = tempusr.strip('@')
            data = " ".join(arr[1:])

            msg = f'SEND {usr} \nContent-length: {len(data)}\n\n{data}'
            
            client_socket_send.send(msg.encode('utf8'))
            receive_msg = client_socket_send.recv(BUFFERSIZE).decode('utf8')
            
            if receive_msg == f'ERROR 103 Header incomplete\n\n':
                print(receive_msg)
                exit()
            if receive_msg == f'ERROR 102 Unable to send\n\n':
                print(receive_msg)
                continue  
            if receive_msg == f'SENT {usr}\n\n':
                print(receive_msg)
                continue
        except:
            continue
            


def receive_msg():
    while True:
        try:
            msg = client_socket_recv.recv(BUFFERSIZE).decode("utf8")
            stream = msg.strip().split('\n')

            usr = stream[0].strip().split()[1]
            data = stream[3]
 
            if check_header(stream):
                client_socket_recv.send(f'ERROR 103 Header Incomplete\n\n'.encode('utf8'))
                continue
        except OSError as error:
            return error
        else:
            client_socket_recv.send(f'RECEIVED {usr}\n\n'.encode('utf8'))
            print(usr+" : "+data)


def check_header(l):
    a = l[1].strip().split(':')
    if len(a)!=2:
        return False
    cont_len = int(a[1].strip())
    if len(l[3])!=cont_len:
        return False
    return True




if __name__ == '__main__':

    HOST = sys.argv[2]
    PORT = 8888
    BUFFERSIZE = 1024

    
    #signal.signal(signal.SIGINT, signal.handler)
    client_socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket_send.connect((HOST, PORT))
    client_socket_recv.connect((HOST, PORT))
    
    registration()
    
    
    send_thread = Thread(target=send_msg)
    send_thread.start()
    
    
    receive_thread = Thread(target=receive_msg)
    receive_thread.start()
    
    
    #send_msg()



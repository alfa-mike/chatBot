import socket
from threading import Thread 


IP = '127.0.0.1'
PORT = 8888
BUFFERSIZE = 1024
ROOM_NAME = "DragonStone"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP,PORT))

clients_send = {}
clients_recv = {}

print("Waiting for connection...")
server.listen()


def incomming_connections():
    while True: 
        client, addr = server.accept()
        print(f'client {addr} is connected to server!')
        Thread(target=SERVER, args=(client,)).start() 


        
def SERVER(client): 
    client_name = 'alfa'    
    while True:
        msg = client.recv(BUFFERSIZE)

        if msg=='exit()'.encode('utf8'):
            exit_server(client_name)
            break

        data = msg.decode('utf8').strip().split() 
        
        if data[0]=="REGISTER":    
            if not data[2].isalnum():
                client.send(f'ERROR 100 Malformed username: {data[2]}\n\n'.encode())
                return
        
            client_name=data[2]            
            
            if msg == f'REGISTER TORECV {client_name}\n\n'.encode('utf8'):
                clients_recv[client_name]=client
                client.send(f'REGISTERED TORECV {client_name}\n\n'.encode())
                
                return

            if msg == f'REGISTER TOSEND {client_name}\n\n'.encode('utf8'): 
                client.send(f'REGISTERED TOSEND {client_name}\n\n'.encode('utf8'))
                clients_send[client_name]=client
                continue
                
    
        data1 = msg.decode('utf8').strip().split('\n')
        
        if not check_header(data1):
            client.send(f'ERROR 103 Header incomplete\n\n'.encode('utf8'))
            exit_server(client_name)
            return 

        recipient = data1[0].split()[1]           # key for clients_recv
        
        len_usrmsg = data1[1].split()[1].strip()     #string h
        
        #formatting msg to be forwarded
        tosend = f'FORWARD {client_name}\n Content-length: {len_usrmsg}\n\n {data1[3]}'.encode('utf8')
        
        
        if recipient=="ALL":
            val = broadcast_msg2(tosend,client_name)
            if val==1:
                client.send(f'SENT {recipient}\n\n'.encode('utf8'))
            elif val==0:
                client.send(f'ERROR 102 Unable to send\n\n'.encode('utf8'))
            else:
                client.send(f'ERROR 103 Header incomplete\n\n'.encode('utf8'))
                exit_server(client_name)
            
            continue

        else:
            val = unicast_msg(tosend,recipient,client_name)
            if val==1:
                client.send(f'SENT {recipient}\n\n'.encode('utf8'))
            elif val==0:
                client.send(f'ERROR 102 Unable to send\n\n'.encode('utf8'))
            else:
                client.send(f'ERROR 103 Header incomplete\n\n'.encode('utf8'))
                exit_server(client_name)

    

def check_header(l):
    if len(l)!=4:
        False
    a = l[1].strip().split(':')
    if len(a)!=2:
        return False
    cont_len = int(a[1].strip())
    if len(l[3])!=cont_len:
        return False
    return True


def exit_server(name):
    print(f'{name} has disconnected.')    

    clients_recv[name].close()
    clients_send[name].close()
    
    del clients_recv[name]
    del clients_send[name]


def broadcast_msg1(tosend):
    if len(clients_recv)==0:
        return
    msg = f'FORWARD {ROOM_NAME}\nContent-length: {len(tosend)}\n\n{tosend}'
    for k in clients_recv.values():
        k.send(msg.encode('utf8'))
    return


def broadcast_msg2(msg,sender_usrname):       # 0 - unable to send || 1-send succesfully || 2 - header incomplete
    if len(clients_recv)==0:
        return 0

    for k,v in clients_recv.items():
        if k!=sender_usrname:
            try:
                v.send(msg)
            except:
                return 0
            else:
                response = v.recv(BUFFERSIZE).decode('utf8')
                if response==f'ERROR 103 Header Incomplete\n\n':
                    return 2
    return 1
        

def unicast_msg(msg,recvr_usrname,sender_usrname):
    if len(clients_recv)==0:
        return 0
    
    for k,v in clients_recv.items():
        if k==recvr_usrname:
            try:
                v.send(msg)
            except:
                return 0
            else:
                response=v.recv(BUFFERSIZE).decode('utf8')
                if response == f'RECEIVED {sender_usrname}\n\n':
                    return 1
                if response ==f'ERROR 103 Header Incomplete\n\n':
                    return 2
    return 0


ACCEPT_THREAD = Thread(target=incomming_connections)
ACCEPT_THREAD.start()
ACCEPT_THREAD.join()
server.close()
    



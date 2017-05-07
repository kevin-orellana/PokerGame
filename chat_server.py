#==============================================================================
# Index
# 
# class Server:
#         __init__:
#                 new_clients list
#                 logged_name2sock dictionary
#                 logged_sock2name dictionary
#                 all_sockets list
#                 group as a Group class object from chat_group.py
#                 server object created using select module
#                 indices dictionary
#         methods:
#                 new_client(self, sock)
#                 login(self, sock)
#                 logout(self, sock)
#                 handle_msg(self, from_sock)
#                 run(self)
#         
#==============================================================================

import time
import socket
import select
import sys
import string
import indexer
import pickle as pkl
from chat_utils import *
import chat_group as grp

M_UNDEF     = '0'
M_LOGIN     = '1'
M_CONNECT   = '2'
M_EXCHANGE  = '3'
M_LOGOUT    = '4'
M_DISCONNECT= '5'
M_SEARCH    = '6'
M_LIST      = '7'
M_POEM      = '8'
M_TIME      = '9'

#CHAT_IP = ''
CHAT_IP = socket.gethostname()
CHAT_PORT = 1112
SERVER = (CHAT_IP, CHAT_PORT)

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        #start server
#==============================================================================
#       SERVER SIDE TCP SOCKET NOTES 
#        Above is a TCP-socket, socket.AF_inet for family and socket.SOCK_STREAM for type
#        The socket.Socket objects have the following main methods:
#        1. bind("localhost", PORT_NUMBER): specific for server socket
#        2. listen(1): 
#                -specific for server socket
#        3. accept(): used to accept an incoming connection, will block 
#                      until a new client connects. When client connects, it will
#                        create a new socket and return it together with the client's address
#                -specific for server socket 
#        4. connect(): specific for client socket
#        5. send(): 
#                   -both types (server/client)
#        6. recv(1024): example: socketA.recv(1024) will read data from socketA in batches of 1024 bytes
#                   -both types (server/client)
#        7. sendall(data): will send all data back to socketB.sendall(data) while repeatedly calling
#                            the recv()  -  Ignore this for now.
        
#       ALL socket methods block, meaning they do not let program do anything else when it 
#        is reading from a socket or writing to the program
#
#        
#       SERVER INFORMATION from chat_utils.py
#        
#       CHAT_IP = socket.gethostname()
#        CHAT_PORT = 1112
#        SERVER = (CHAT_IP, CHAT_PORT)
#    
#        
#        
#        
#        
#        
#        
#==============================================================================
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices = {} #CHECK... is this meant to be an Index object?
        #sonnet indexing
        self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        self.sonnet = pkl.load(self.sonnet_f)
        self.sonnet_f.close()
        
    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0) #SETS socket TO NONBLOCKING
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        msg = myrecv(sock)
        if len(msg) > 0:
            
            code = msg[0]
            
            if code == M_LOGIN: 
                name = msg[1:]
                if self.group.is_member(name) != True:
                    #move socket from new clients list to logged clients
                    self.new_clients.remove(sock)
                    #add into the name to sock mapping
                    self.logged_name2sock[name] = sock
                    self.logged_sock2name[sock] = name
                    #load chat history of that user
                    if name not in self.indices.keys():
                        try:
                            self.indices[name]=pkl.load(open(name+'.idx','rb'))
                        except IOError: #chat index does not exist, then create one
                            self.indices[name] = indexer.Index(name)
                    print(name + ' logged in')
                    self.group.join(name)
                    mysend(sock, M_LOGIN + 'ok')
                else: #a client under this name has already logged in
                    mysend(sock, M_LOGIN + 'duplicate')
                    print(name + ' duplicate login attempt')
            else:
                print ('wrong code received')
        else: #client died unexpectedly
            self.logout(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock): #from_socket is the socket of the client sending the message
        #msg is the string sent by the client state machine: IMPORTANT
        msg = myrecv(from_sock)  #myrecv(from_sock) returns "0__", "1__",...
        if len(msg) > 0:
            code = msg[0] 
#==============================================================================
#             handle connect request: this is implemented for you
#==============================================================================
            if code == M_CONNECT: #if code == "2"
                to_name = msg[1:] #to_name is the name of the peer that from_socket's client is sending to
                from_name = self.logged_sock2name[from_sock] #returns value of {}, which = name of client sending msg
                if to_name == from_name: #to_name = from_name if con 
                    msg = M_CONNECT + 'hey you'
                # connect to the peer
                elif self.group.is_member(to_name): 
                    to_sock = self.logged_name2sock[to_name] #the socket of the client we are sending/connecting TO
                    self.group.connect(from_name, to_name) 
                    the_guys = self.group.list_me(from_name) #returns list of all members in from_name's group
                    msg = M_CONNECT + 'ok'
                    for g in the_guys[1:]: #calls mysend(to_sock, M_CONNECT + from_name) to all members in from_name's group
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, M_CONNECT + from_name)
                else:
                    msg = M_CONNECT + 'no_user'
                mysend(from_sock, msg) #sends msg with M_CONNECT + ok/hey you/no user to from_socket 
#==============================================================================
#             handle multicast message exchange; IMPLEMENT THIS    
#==============================================================================
            elif code == M_EXCHANGE: #CHECK... I think the Indexing is wrong
                from_name = self.logged_sock2name[from_sock] #is the name of client sending the messages
                # Finding the list of people to send to
                the_guys = self.group.list_me(from_name)[1:] #all the clients in from_name's group
                exchange_message = msg[1:]
                self.indices[from_name].add_msg_and_index(exchange_message) 
                
#line above adds&indices the msg to from_name's key (an Index obj) in self.indices {}
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]                
                    mysend(to_sock, M_EXCHANGE + exchange_message)
#==============================================================================
#             listing available peers; IMPLEMENT THIS
#==============================================================================
            elif code == M_LIST: #WORKS BUT MAKE SURE
                from_name = self.logged_sock2name[from_sock]
                msg = "M_LIST handler needs to use self.group functions to work"
                msg = self.group.list_all(from_name) 
                mysend(from_sock, msg)
#==============================================================================
#             retrieve a sonnet; IMPLEMENT THIS
#==============================================================================
            elif code == M_POEM: #CHECK (it works but you can add more fail-safe try/except)
                poem_indx = int(msg[1:]) #poem index as integer
                from_name = self.logged_sock2name[from_sock]
                try:
                    poem = self.sonnet.get_sect(poem_indx) #gets poem/message from sonnet index class
                except:
                    poem = "Poem not found!"
                mysend(from_sock, M_POEM + poem)
#==============================================================================
#             retrieve the time; IMPLEMENT THIS
#==============================================================================
            elif code == M_TIME: #CHECK works.
                ctime = "M_TIME handler has to calc current date/time to send (use time module)"
                ctime = time.ctime()
                mysend(from_sock, ctime)
#==============================================================================
#             search handler; IMPLEMENT THIS
#==============================================================================
            elif code == M_SEARCH: #CHECK... is self.indices a {} or Index class object?
                from_name = self.logged_sock2name[from_sock] #is the name of client sending the messages
                search_query = str(msg[1:]) #the string we are searching for
#                search_rslt = "M_SEARCH handler needs to use self.indices search to work"
#                search_rslt = self.indices.search(search_query) #CHECK: are we using the self.indices.search() function?
                search_result = ""
                for i in self.indices.keys():
                     search_result += self.indices[i].search(search_query)
                     print("server side result" + search_result)
#                search_rslt = self.indices[from_name].search(search_query)
                mysend(from_sock, M_SEARCH + search_result)
#==============================================================================
#             the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif code == M_DISCONNECT:
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, M_DISCONNECT)
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================
            elif code == M_LOGOUT:
                self.logout(from_sock)
        else:
            #client died unexpectedly
            self.logout(from_sock)   

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
#           read = read sockets
#           write = write socketw
#           error = list of sockets with errors
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc) #calls handle_msg(sock) for each socket IF its in read socket list
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
#               sock, address=self.server.accept()
#               print("sock: " + str(sock) + "address: " + str(address))
               self.new_client(sock)
           
def main():
    server=Server()
    server.run()

main()

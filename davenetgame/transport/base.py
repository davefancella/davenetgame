#!/usr/bin/env python3

'''

   Copyright 2016 Dave Fancella

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

'''

import threading, time

from davenetgame import callback
from davenetgame import exceptions
from davenetgame import pedia

## @file
#
#  This file contains the TransportBase class from which all transports must inherit.  In order
#  for a client-server connection to be made, the client has to have a ClientProtocol associated
#  with a transport derived from TransportBase, and the server has to have a ServerProtocol
#  associated with a transport as well.  All the transport does is send and receive messages.
#  When a message is received, it will call a message callback that the Protocol object must
#  implement.  When a message is sent, the Protocol object must tell the transport layer where
#  it is going.  For UDP connections, a host:port pair is needed.  For TCP connections, a socket
#  is needed.  This information is stored in the Connection object.
#
#  Currently, only UDP is implemented.

class TransportBase(threading.Thread):
    ## This is the lock that must be called to avoid thread collisions
    __lock = None
    
    ## Bytes received
    __bytesreceived = None
    
    ## Bytes sent
    __bytessent = None
    
    ## Buffer size, used for all connections, since you can't know which connection has sent 
    #  you a packet until you do the socket read, and you need this to do the read.
    __buffersize = None
    
    ## The list of callbacks that will be called for messages received.  It will be populated
    #  by the Protocol object.  Without a protocol object, messages don't get processed, they
    #  just get thrown away.
    __callbacks = None
    
    ## The owner of this Transport object.
    __owner = None
        
    ## The server host for the socket.  If the socket is not a server socket, then this
    #  is the host for the remote server that this socket will ultimately connect to.  If the 
    #  socket is a server socket, this member is not used.
    __serverhost = None
    
    ## The server port for the socket.  If the socket is not a server socket, then this
    #  is the port for the remote server that this socket will ultimately connect to.  If the 
    #  socket is a server socket, this member is not used.
    __serverport = None
    
    ## The client host for the socket.  This is the host that the socket will bind to locally,
    #  for sockets that must do so.  Subclasses should interpret a None value here as "bind to
    #  all local interfaces for the socket type implemented".
    __clienthost = None
    
    ## The client port for the socket.  For sockets that have to bind to a local port, this
    #  is the port that they will use.  Subclasses should interpret a None value here as "choose
    #  a random port", rather than an error value.
    __clientport = None
    
    ## The socket
    __socket = None
    
    ## Do we continue the thread?
    __continue = None

    ## Whether or not this socket is a server.
    __isserver = None
    
    def __init__(self, **args):
        super().__init__()

        if 'owner' in args:
            self.__owner = args['owner']
        else:
            raise exceptions.dngExceptionNotImplemented("Transport does not have owner, cannot instantiate.")
        
        self.__isserver = False
        
        if 'isserver' in args:
            self.SetServer(args['isserver'])
            
        self.__clienthost = ''
        self.__clientport = None
        
        if 'clienthost' in args:
            self.__clienthost = args['clienthost']
        
        if 'clientport' in args:
            self.__clientport = args['clientport']

        self.__lock = threading.RLock()
        
        self.__bytesreceived = 0
        self.__bytessent = 0
        
        self.__buffersize = 1024
        
        self.__callbacks = callback.CallbackList()
        
        self.__continue = False
    
    ## Call to tell the subclass it will function as a server.  It is needed for sockets to
    #  bind to a listening socket as a server.  Clients typically don't need to worry about
    #  that.
    def SetServer(self, server=False):
        self.__isserver = server
        
    def IsServer(self):
        return self.__isserver
        
    def SetServerInfo(self, host, port):
        self.__serverhost = host
        self.__serverport = port

    def ServerInfo(self):
        return (self.__serverhost, self.__serverport)
    
    def SetClientInfo(self, host, port):
        self.__clienthost = host
        self.__clientport = port

    def ClientInfo(self):
        return (self.__clienthost, self.__clientport)
    
    def Buffersize(self):
        return self.__buffersize

    def BytesSent(self):
        return self.__bytessent
    
    def BytesReceived(self):
        return self.__bandwidth

    ## Call to determine if the thread should continue.
    def Continue(self):
        ret = self.__continue
        
        return ret
    
    ## Use to change whether or not the thread should continue.
    #
    #  @param cont True or False.  A value of False should cause the thread to stop on its own.
    def SetContinue(self, cont = True):
        self.__continue = cont
    
    ## Used internally to actually start the thread.  It is called by the Protocol object, and
    #  calls Transport.Start() when it's done, which is where the subclasses' initialization
    #  happens.
    def _start(self):
        self.SetContinue(True)
        
        # Call the subclass's start method.
        self.Start()
        
        # Call the threading.Thread.start() method to actually start the thread.
        self.start()
    
    ## Call to start the transport object.  Subclasses must implement this.
    def Start(self):
        raise NotImplementedError
    
    ## Call to poll your socket and process incoming messages.
    def PollSocket(self):
        raise NotImplementedError
    
    ## Stops the socket polling.  It is guaranteed to be called after the thread has stopped
    #  all execution.  Also, subclasses must implement this method to do whatever cleanup
    #  needed, like deleting the socket.
    def Stop(self):
        raise NotImplementedError
    
    ## Send a single message to the socket.  If at all possible, it should be sent immediately.
    #  If, for some reason, your subclass is unable to do so, then you must queue it up and
    #  send it as soon as possible.
    #
    #  The message will be a dict with three members:
    #      'message' : the serialized message
    #      'type' : the TypeID for the message
    #      'connection' : a (host,port) tuple that is the connection to which the message
    #                     must be sent.
    def SendMessage(self, msg):
        raise NotImplementedError
    
    ## Called internally to stop the thread.  Subclasses should not override this method, but
    #  must override Stop.
    #
    #  @param blocking: If True, this call will block.  If False, it returns immediately and the thread will
    #                   stop itself on its own.  
    def _stopI(self, blocking=True):
        self.SetContinue(False)
    
        if blocking:
            self.Join()
            
        self.Stop()

    ## Call this to join the thread and wait until it closes.  Be careful doing this, because if you haven't
    #  signaled in any way that the thread should end, then your process will continue forever.
    def Join(self):
        self.join()

    ## Call to process a message after you have received it.
    #
    #  @param typeId The TypeID from the message.
    #  @param msg The message itself, in a string format capable of being parsed by the struct 
    #             module.  Most messages actually get parsed by Google Protocol Buffers, but they
    #             use the struct module internally.
    #  @param connectInfo The connection information for the connection from which the message
    #                     was received, usually a (host,port) tuple.  It has to be understood
    #                     by the connection object.
    def ProcessMessage(self, typeId, msg, connectInfo):
        buf = pedia.getPedia().GetMessageObject(typeId)
        
        typeName = pedia.getPedia().GetTypeName(typeId)

        buf.ParseFromString(msg)
        
        # We pass a timestep to every handler so they can update connections accordingly
        timestep = time.time()

        self.__owner.ReceiveMessage(buf, connectInfo, timestep)
        
        theCbs = self.GetCallbacks(typeName)

        for cb in theCbs:
            cb.setargs( { 'message' : buf,
                          'connection' : connectInfo,
                          'timestamp' : timestep } )
            cb.Call()

    ## Call to get outgoing messages from the owner object.  Each message will be already
    #  serialized, so the return value of this method is a list of dicts, where each item
    #  is of the form:
    #      'message' : the serialized message
    #      'type' : the TypeID for the message
    #      'connection' : a (host,port) tuple that is the connection to which the message
    #                     must be sent.
    def GetOutgoingMessages(self):
        return self.__owner.GetOutgoingMessages()

    ## Starts the socket polling.  Don't call this directly, instead call Start().  Also,
    #  you *must* implement PollSocket in your subclass.  It will be called automatically,
    #  and leaves you not having to worry about the threading details, while providing support
    #  for the Transport object to operate in a single-threaded environment.
    def run(self):
        # now keep talking with the other side
        while self.Continue():
            # First, poll the socket and handle incoming messages
            self.PollSocket()
            
            # Second, maintain connections.  This is in the middle because outgoing messages
            # will be generated, and we want to make sure to send those in this loop iteration
            # rather than waiting for the next time around.
            self.__owner.MaintainConnections()
            
            # Last, send all outgoing messages.
            for msg in self.GetOutgoingMessages():
                self.SendMessage(msg)
            
            time.sleep(0.01)
            
    ## Register a message callback.
    #
    #  @param name the name of the callback.
    #  @param func the function that will be called.  It should take a keyword list of arguments.
    def RegisterCallback(self, name, func, options={}):
        self.__callbacks.RegisterCallback(name, func, options)
    
    ## Gets a callback list for a specific event/message.
    def GetCallbacks(self, name):
        return self.__callbacks.GetCallbacks(name)
    
    ## Used to acquire a lock when working with data structures shared with the main thread
    def AcquireLock(self):
        self.__lock.acquire()
    
    ## Used to release the lock when done working with data structures shared with the main thread
    def ReleaseLock(self):
        self.__lock.release()


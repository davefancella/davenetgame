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

import getpass # for convenience

from davenetgame import client
from davenetgame import connection

class ClientCallback(object):
    __host = None
    __port = None
    __name = None
    __client = None
    __callback_events = None
    __callback_messages = None
    __connection = None

    def __init__(self, **args):
        self.__host = 'localhost'
        self.__port = 8888
        self.__name = getpass.getuser()
        
        if 'host' in args:
            self.SetHost = args['host']
        if 'port' in args:
            self.SetPort = args['port']
            
        # @@todo Write the part that connects the callbacks to the client object

    def SetHost(self, host):
        self.__host = host
        
    def SetPort(self, port):
        # Ensure the port is always an int
        self.__port = int(port)

    ## Starts the client, initiating a connection to the server.  Don't do this until you've set the host
    #  and port number correctly!
    def Start(self):
        self.__client = client.nClient()
        self.__client.SetServer(self.__host, self.__port)
        self.__setupCallbacks()
        self.__client.Start()
        
        self.__connection = connection.ClientConnection(host = self.__host,
                                                        port = self.__port,
                                                        owner = self.__client)
        
        self.__connection.Login(self.__name)

    ## Stops the client.  Call will block until the client thread has stopped.
    def Stop(self):
        self.Logout()
        self.__client.Stop(True)
        
        # delete the client object, so that if we start again, we can create a new one.
        self.__client = None

    ## Logs out of the server, but keeps the client object active.  Probably no reason you should call this,
    #  but it is used internally.
    def Logout(self):
        self.__client.Logout()
        
    ## Manually pings the server.  Probably no reason you should call this, either, but it's used by the test
    #  client for testing purposes.
    def SendPing(self):
        self.__client.SendPing()
    
    ## Bandwidth used
    def Bandwidth(self):
        return self.__client.BytesSent() + self.__client.BytesReceived()
    
    ## Bytes sent
    def BytesSent(self):
        return self.__client.BytesSent()
    
    ## Bytes received
    def BytesReceived(self):
        return self.__client.BytesReceived()
    
    ## Returns a string indicating the status of the connection.
    def StatusString(self):
        return connection.statuslist[self.__client.Status()][1]

    ## @name Internal
    #
    #  These methods are for internal use only.  Users should not use them unless there's
    #  absolutely no other way to do whatever it is they're trying to do, and they haven't
    #  figured out they shouldn't do it, whatever it is.
    #@{

    ## Register an event callback.  Games *can* use this, but the mechanism isn't terribly useful.  
    #  For the most part,
    #  simply implement the required callback methods in this class to receive callbacks.  
    #  Required callbacks will
    #  throw an exception.
    def RegisterEventCallback(self, name, func, options={}):
        self.__callback_events.append([name, func, options])

    ## Register a message callback.  Games *can* use this, but the mechanism isn't terribly useful.  
    #  For the most part,
    #  simply implement the required callback methods in this class to receive callbacks.  
    #  Required callbacks will
    #  throw an exception.
    def RegisterMessageCallback(self, name, func, options={}):
        self.__callback_messages.append([name, func, options])

    ## This method is called after the server is started to register all the callbacks that 
    #  will be used.
    def __setupCallbacks(self):
        for cb in self.__callback_events:
            self.Owner().RegisterEventCallback(cb[0], cb[1], cb[2])
        for cb in self.__callback_messages:
            self.Owner().RegisterMessageCallback(cb[0], cb[1], cb[2])
    #@}
        
        

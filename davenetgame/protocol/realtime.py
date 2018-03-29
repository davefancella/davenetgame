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

from davenetgame.protocol.base import ProtocolBase
from davenetgame import connection

class RealtimeClient(ProtocolBase):
    def __init__(self, **args):
        if 'host' in args:
            self.SetHost = args['host']
        if 'port' in args:
            self.SetPort = args['port']
            
        self.RegisterMessageCallback('login', self.LoginMessage)
        self.RegisterMessageCallback('logout', self.LogoutMessage)

    def LoginMessage(self, typeId, msg, connection):
        pass

    def LogoutMessage(self, typeId, msg, connection):
        pass

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

        
class RealtimeServer(ProtocolBase):
    __host = None
    __port = None
    __console = None
    __server = None
    __consolecommands = None
    __callback_events = None
    __callback_messages = None
 
    ## Constructor.  Pass it a dictionary with any of the following keys to initialize them:
    #      host : the host that will be listened to by the socket.
    #      port : the port on which the socket will listen
    #      name : the name of the server
    def __init__(self, **args):
        super().__init__(self, **args)

        if 'name' in args:
            self.SetName(args['name'])
        else:
            self.SetName('Test Server')

        self.RegisterMessageCallback('login', self.LoginMessage)
        self.RegisterMessageCallback('logout', self.LogoutMessage)

    ## Starts the server
    def Start(self):
        self.__server = server.nServer(owner = self)
        self.__setupCallbacks()
        
        self.__server.ListenOn(self.__host, self.__port)

        self.__server.Start()

        print("Starting " + self.__name + ".")
        
    ## Call to stop the server.  Stops the console as well.
    def Stop(self):
        self.__server.Stop(True)
        
    ## Must be called periodically to keep the network layer going.  Pass it time.time() 
    #  to give it
    #  a timestep.
    def Update(self, timestep):
        try:
            # Update the server.  This is where the callbacks will get called.
            self.__server.Update(timestep)
                
    ## @name Callback Methods
    #
    #  These are the callback methods for particular messages.
    #@{
    
    ## Callback for login messages.
    def LoginMessage(self, **args):
        pass
    
    ## Callback for logout messages
    def LogoutMessage(self, **args):
        pass
    
    #@}
    

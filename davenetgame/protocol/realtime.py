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

from davenetgame.protocol.base import ProtocolBase
from davenetgame.protocol import connection

class RealtimeClient(ProtocolBase):
    ## The connection to the server.
    __connection = None
    
    def __init__(self, **args):
        super().__init__(**args)
        
        if 'host' in args:
            self.SetHost = args['host']
        if 'port' in args:
            self.SetPort = args['port']
            
        self.RegisterMessageCallback('login', self.LoginMessage)
        self.RegisterMessageCallback('logout', self.LogoutMessage)

    ## @name Callback Methods
    #
    #  These are the callback methods for particular messages.
    #@{
    
    ## This is the callback for login messages.  On the client, when a login message is received,
    #  it is telling the client that another client has logged into the server.
    def LoginMessage(self, **args):
        self.Ack(args['message'].id, self.Connection() )
        
        self.Connection().SetId(args['message'].con_id)
        self.Connection().set_lastrecv(args['timestep'] )
        
        #TODO: emit an event indicating that the login is complete
        print('The server has logged you in.')

    def LogoutMessage(self, typeId, msg, connection):
        pass
    
    #@}

    ## @name Protocol Send Methods
    #
    #  These are the methods used to send messages that are part of the protocol.  While there
    #  is usually a 1:1 relationship between these methods and actual messages that are to be
    #  sent, it's not required.  You should think of this more like the human ways of sending
    #  a message, where you don't just say one thing to someone.  You might need to blow up
    #  their car and burn down their house, which would all require three different message types
    #  to be sent.
    #@{
    
    ## This causes a Login message to be sent to the server, indicating that the client would
    #  like to join the party.
    def LoginSend(self):
        theMsg = self.Pedia().GetMessageObject('login')
        theMsg.player = self.Name()
        
        self.AddOutgoingMessage(theMsg, self.Connection() )
    #@}

    ## Starts the client, initiating a connection to the server.  Don't do this until you've 
    #  set the host and port number correctly!
    def Start(self):
        host, port = self.Host(), self.Port()
        self.ConnectionList().append(connection.Connection(host=host, port=port ) )
        
        self.LoginSend()

    ## Cleanup after the thread has been closed.
    def Stop(self):
        pass
        
class RealtimeServer(ProtocolBase):
    ## Constructor.  Pass it a dictionary with any of the following keys to initialize them:
    #      host : the host that will be listened to by the socket.
    #      port : the port on which the socket will listen
    #      name : the name of the server
    def __init__(self, **args):
        super().__init__(**args)

        if 'name' in args:
            self.SetName(args['name'])
        else:
            self.SetName('Test Server')

        self.RegisterMessageCallback('login', self.LoginMessage)
        self.RegisterMessageCallback('logout', self.LogoutMessage)

    ## Starts the server
    def Start(self):
        print("Starting " + self.Name() + ".")
        
    ## Call to stop the server.  Stops the console as well.
    def Stop(self):
        pass
        
    ## @name Callback Methods
    #
    #  These are the callback methods for particular messages.
    #@{
    
    ## Callback for login messages.  This means that a client is trying to login.
    def LoginMessage(self, **args):
        print("Received login from " + str(args['connection'][0]) + ":" + str(args['connection'][1]) )
        
        newConnection = self.ConnectionList().Create(args['connection'], args['message'].player)
        
        newConnection.set_lastrecv(args['timestep'])
        
        self.Ack(args['message'].id, newConnection)
        
        theMsg = self.Pedia().GetMessageObject('login')
        theMsg.con_id = newConnection.id()
        theMsg.player = newConnection.player()
        
        self.AddOutgoingMessage(theMsg, newConnection)
        
        #TODO: emit an event for the login so the game can create a player for this connection
        self.EmitEvent( {'name' : 'Login',
                         'type' : 'login',
                         'data' : newConnection
                         } )
    
    ## Callback for logout messages.  This means that a client is signaling it is disconnecting
    #  from the server.
    def LogoutMessage(self, **args):
        pass
    
    #@}
    

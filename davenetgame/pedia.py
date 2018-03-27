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

import importlib


## This class is the master list of all messages.  If you want to create a message, you have to
#  get the type from here.  If you want to decode a message, you give this class the message 
#  type ID and you get an opaque message of the correct type that can then decode the message.  
#  So, this is the Encyclopedia of Messages.
#
#  It is implemented as a singleton, so you must use the get method to get it.  The first time this
#  module is imported, it will create the pedia.

__pedia = None

messageList = None

## This class contains all the messages.  It maintains the message type IDs and provides access
#  to the classes to encode/decode messages.
class Messages(object):
    ## Stores the actual message list, indexed by message ID, which is an integer.  Items are
    #  of the form (message name, module name, class name)
    __messageList = None
    
    ## A lookup table, indexed by message name that gives the message ID, which is an integer.
    __messageNames = None
    
    ## A dictionary, indexed by message id, of class types for each message.
    __messageTypes = None
    
    ## Message IDs used internally.  The first 256 message IDs are reserved for use by
    #  davenetgame, setting a maximum of messages available for internal use to 256.
    __lastmessageId = None
    
    ## Message IDs for custom messages provided by library users.
    __lastCustomMessageId = None
    
    ## Initalize the list.  if theList is not none, the messagelist will be set to whatever it is.
    def __init__(self):
        self.__lastmessageId = 0
        self.__lastCustomMessageId = 256
        
        self.__messageList = {}
        self.__messageNames = {}
        self.__messageTypes = {}
        
        # Add all of the internal message types here, to ensure that they get the right
        # IDs
        self.AddInternalMessageType("ping", "Ping", {'nologin':None} )
        self.AddInternalMessageType("ack", "Ack")
        self.AddInternalMessageType("login", "Login", {'nologin':None} )
        self.AddInternalMessageType("logout", "Logout")
        self.AddInternalMessageType("chat", "Chat")

    ## Adds a message type.  Provide it with a name and the location of the module from which
    #  the *_pb2.py file will be imported.  The order in which messages are added *matters*,
    #  so make sure that you add them in the correct order any time.  If you change the order
    #  at any point, you may break backward compatibility, which, admittedly, may be desired
    #  behavior if you're a jerk.
    #
    #   @param module a string specifying the module, i.e. "davenetgame.messages"
    #   @param name the name of the message type.  It should be able to be prepended to _pb2.py
    #               to create the name of the file that contains the message, i.e. ping_pb2.py
    #   @param classname the name of the class that we'll find inside the _pb2.py file, as defined
    #                    in the .proto file.
    #  @param options the options for the message.  Currently, only "nologin" is supported,
    #                 and means that the message doesn't require login to be processed.  Note
    #                 that this is a dictionary, and 'nologin' is a key.  The value associated
    #                 with the key is not evaluated in any way, so assigning it a value of None
    #                 is so useless that it is comical to do so.  Who doesn't like a meaningful
    #                 value of None?
    def AddMessageType(self, module, name, classname, options={}):
        self._addMessageType(module, name, classname, False)
        
    ## Adds an internal message type.  Provide it with a name, and the rest is handled internally.
    #  Since the order matters, once a message has been added in a particular order, it cannot
    #  be changed, since that would break backwards compatibility for users of the library.
    #
    #   @param name the name of the message type.  It should be able to be prepended to _pb2.py
    #               to create the name of the file that contains the message, i.e. ping_pb2.py
    #   @param classname the name of the class that we'll find inside the _pb2.py file, as defined
    #                    in the .proto file.
    #  @param options the options for the message.  Currently, only "nologin" is supported,
    #                 and means that the message doesn't require login to be processed.  Note
    #                 that this is a dictionary, and 'nologin' is a key.  The value associated
    #                 with the key is not evaluated in any way, so assigning it a value of None
    #                 is so useless that it is comical to do so.  Who doesn't like a meaningful
    #                 value of None?
    def AddInternalMessageType(self, name, classname, options={}):
        self._addMessageType("davenetgame.messages", name, classname, True)
        
    ## Used internally to actually add the message types.
    #
    #  @param module the string specifying the module
    #  @param name the name of the message type.
    #   @param classname the name of the class that we'll find inside the _pb2.py file, as defined
    #                    in the .proto file.
    #  @param options the options for the message.  Currently, only "nologin" is supported,
    #                 and means that the message doesn't require login to be processed.  Note
    #                 that this is a dictionary, and 'nologin' is a key.  The value associated
    #                 with the key is not evaluated in any way, so assigning it a value of None
    #                 is so useless that it is comical to do so.  Who doesn't like a meaningful
    #                 value of None?
    #  @param internal whether or not the message is internal to davenetgame.  It defaults
    #                  to False as a protection sort of thing, but it should never be called
    #                  outside of davenetgame in the first place.
    def _addMessageType(self, module, name, classname, options={}, internal=False):
        if internal is True:
            if name not in self.__messageNames:
                if self.__lastmessageId < 256:
                    self.__messageNames[name] = self.__lastmessageId
                    self.__messageList[self.__lastmessageId] = [name, module, classname]
                    self.__lastmessageId = self.__lastmessageId + 1
                else:
                    pass
                    # @todo this should throw an exception.
            else:
                pass
                # @todo This should throw an exception
        else:
            if name not in self.__messageNames:
                self.__messageNames[name] = self.__lastCustomMessageId
                self.__messageList[self.__lastCustomMessageId] = [name, module, classname]
                self.__lastCustomMessageId = self.__lastCustomMessageId + 1
            else:
                pass
                # @todo This should throw an exception
                
        self._importMessageClass(name)
    
    ## Used to import the actual module for the message.  The message should already be in
    #  the messageList.
    #
    #  @returns the Class type for the message.
    def _importMessageClass(self, name):
        if name in self.__messageNames:
            theMessage = self.__messageList[self.__messageNames[name] ]
            
            theModName = theMessage[1] + "." + theMessage[0] + "_pb2"
            
            mod = importlib.import_module(theModName)
            
            theClass = getattr(mod, theMessage[2])
            self.__messageTypes[self.__messageNames[name] ] = theClass
    
    ## Gets a message type, whether or not it is given a string or an ID.
    def GetMessageType(self, theType):
        retType = None
        
        if theType in self.__messageList:
            retType = self.__messageList[theType]
            if type(theType) == str:
                retType = self.__messageList[retType]
        
        return retType
        
    ## Gets a type ID for the message being sent
    def GetTypeID(self, msg):
        for key, value in self.__messageList.items():
            if type(msg) == value:
                return key
    
    ## Gets the message name, as a string, when given an ID
    def GetTypeName(self, Id):
        if Id in self.__messageTypes:
            return self.__messageTypes[Id]
    
    ## Gets the message options without creating a type object for them.
    def GetMessageOptions(self, Id):
        if Id in self.__messageList:
            return self.__messageList[Id]['options']
        
        return {}
    
## Call this to get the existing pedia
def getPedia():
    global __pedia
    
    if __pedia is None:
        __pedia = Messages()
        
    return __pedia
    
    
    
    

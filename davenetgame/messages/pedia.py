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


## This class is the master list of all messages.  If you want to create a message, you have to get the
#  type from here.  If you want to decode a message, you give this class the message type ID and you get
#  an opaque message of the correct type that can then decode the message.  So, this is the Encyclopedia
#  of Messages.
#
#  It is implemented as a singleton, so you must use the get method to get it.  The first time this
#  module is imported, it will create the pedia.

__pedia = None

messageList = None

class Messages(object):
    __messageList = None
    
    ## Initalize the list.  if theList is not none, the messagelist will be set to whatever it is.
    def __init__(self, theList = None):
        if theList is not None:
            self.SetList(theList)
            
    ## Gets a message type, whether or not it is given a string or an ID.
    def GetMessageType(self, theType):
        retType = None
        
        if self.__messageList.has_key(theType):
            retType = self.__messageList[theType]
            if type(theType) == str:
                retType = self.__messageList[retType]
        
        return retType
        
    ## Gets a type ID for the message being sent
    def GetTypeID(self, msg):
        for key, value in self.__messageList.iteritems():
            if type(msg) == value:
                return key
        
    ## Set the internal message list.
    def SetList(self, theList):
        self.__messageList = theList


## Call this to get the existing pedia
def getPedia():
    global __pedia
    
    if __pedia is None:
        __pedia = Messages()
        
    return __pedia

## This is where the messageList is setup, but the actual types are handled in the messageList module, which
#  should only ever be imported here.
if messageList is None:
    from davenetgame.messages import messageList
    
    theMessages = getPedia()
    theMessages.SetList(messageList.ml)
    
    messageList = "Gotit"
    
    
    
    
    
    

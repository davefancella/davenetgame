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

import struct

from davenetgame.gameobjects.attributes import base

## @file This file provides attribute classes for all of python's builtin types.

## Integer attributes.
class nSyncAttributeInt(base.nSyncAttributeBase):
    ## Initializes the class.  attrDesc should be a dictionary describing the attribute that this
    #  object will represent.  Consult nSyncObject for the description of this dictionary.
    #  The attribute will be marked dirty initially, because it is dirty when created new.  This will
    #  result in the entire nSyncObject being synced with initial values as soon as it is created,
    #  and this is desired behavior.
    def __init__(self, **attrDesc):
        # Force the type to be an int, regardless of what was passed in.
        attrdesc['type'] = int
        super().__init__(attrDesc)
        
    def __str__(self):
        return str(self._value)
        
    def GetFormatString(self):
        return "Iq"
            
class nSyncAttributeFloat(base.nSyncAttributeBase):
    ## Initializes the class.  attrDesc should be a dictionary describing the attribute that this
    #  object will represent.  Consult nSyncObject for the description of this dictionary.
    #  The attribute will be marked dirty initially, because it is dirty when created new.  This will
    #  result in the entire nSyncObject being synced with initial values as soon as it is created,
    #  and this is desired behavior.
    def __init__(self, **attrDesc):
        # Force the type to be an float, regardless of what was passed in.
        attrdesc['type'] = float
        super().__init__(attrDesc)
        
    def __str__(self):
        return str(self._value)
        
    def GetFormatString(self):
        return "Id"
            

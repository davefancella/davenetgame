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

from davenetgame import exceptions

## This class stores attributes that will be synced over the network.  It is a generic class
#  that supports the standard built-in Python types.  As long as you only need those, then this
#  class is all you need.
class nSyncAttributeBase(object):
    ## The name of the attribute.  This probably isn't useful for this class to know, but hey,
    #  someday an instance of this class may need to go where everybody knows your name, and that
    #  won't be true of the instance doesn't know its own name.
    _name = None
    
    ## The id for this attribute.  It'll be used to encode the attribute to send over the wire.
    _id = None
    
    ## The actual value of the attribute.
    _value = None
    
    ## The type of the attribute.  Must be a type object.
    _type = None
    
    ## Marks whether or not the attribute has been changed since it was last synced.
    _isdirty = None
    
    ## Initializes the class.  attrDesc should be a dictionary describing the attribute that this
    #  object will represent.  Consult nSyncObject for the description of this dictionary.
    #  The attribute will be marked dirty initially, because it is dirty when created new.  This will
    #  result in the entire nSyncObject being synced with initial values as soon as it is created,
    #  and this is desired behavior.
    def __init__(self, **attrDesc):
        self._name = attrDesc['name']
        self._type = attrDesc['type']
        self._value = attrDesc['value']
        self._isdirty = True
        self._id = attrDesc['id']
        
    ## Just a generic way to return a string.  Subclasses should reimplement this, of course.
    def __str__(self):
        return str(self._value)
        
    ## Returns the id for this attribute
    def id(self):
        return self._id
    
    def GetFormatString(self):
        raise dngExceptionNotImplemented("GetFormatString must be implemented in nSyncAttribute classes")
        
    ## Generic encoding method.  It works fine for scalar values, but breaks down with anything
    #  of sufficient complexity.
    #
    #  @todo: consider removing this from the base class and requiring subclasses to implement it.
    def Encode(self):
        fmt = self.GetFormatString()
        
        if fmt is not None:
            return struct.pack("!" + fmt, self._id, self._value)
    
    ## Checks to see if this attribute has been changed since the last time it was synced.
    def IsDirty(self):
        return self._isdirty
    
    ## Change the dirty bit.  By default, it sets the dirty bit to False, making it clean.
    def SetDirty(self, dirty = False):
        self._isdirty = dirty
    
    ## This is the method that should be called when you want to know the type of the attribute
    #  that this class represents.  It would break all sorts of things if we override python's
    #  builtins to hide the fact that the actual type of this object is nSyncAttribute.
    def Type(self):
        return self._type
    
    ## Gets the value of the attribute for syncing.  Automatically changes the _isdirty value to false,
    #  indicating that the attribute has been synced.  Further calls will still return the value,
    #  but in the case of a multi-threaded situation, the value might change, resulting in inconsistent
    #  syncs, so it is best for the calling code to cache the value so that it can create all of the
    #  sync messages it needs to send after calling this method only once.
    def _get_attribute_sync(self):
        self._isdirty = False
        return self._value
    
    ## Sets the value of the attribute during syncing.  This sets the _isdirty flag to false and
    #  should only be used internally.  This should only be called in response to receiving a network
    #  sync message.
    def _sync_attribute(self, value):
        self._isdirty = False
        self._value = value
    
    ## Overrides the default __getattribute__ behavior.  There's actually not a lot of point of doing
    #  this, really, but we do it anyway.
    def __getattribute__(self, name):
        # The entire purpose of this if statement is to protect the name "_value" from being overridden.
        # It's not perfect, but a programmer would be dumb to bother changing it.
        if name == "_value":
            return super().__getattribute__("_value")
        else:
            return super().__getattribute__(name)
        
    ## Overrides the default __setattr__ behavior to make sure we do the necessary housekeeping
    #  when the actual value of the attribute being synced is done.  Also, we type check that value
    #  and throw an exception to make sure nobody tries to give us a type that we can't later encode
    #  into a network message.  This is also where all other possible options for attributes
    #  get checked and enforced, if need be.
    def __setattr__(self, name, value):
        if name == "_value":
            if isinstance(value, self._type):
                super().__setattr__("_isdirty", True)
                super().__setattr__("_value", value)
            else:
                raise exceptions.dngSyncAttributeTypeError
        else:
            super().__setattr__(name, value)
    

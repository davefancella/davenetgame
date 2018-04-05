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
class nSyncAttribute(object):
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
        
    ## Returns the id for this attribute
    def id(self):
        return self._id
    
    def GetFormatString(self):
        # Integers are encoded as "unsigned int"/"long long" to allow for the largest signed ints
        # possible.  The unsigned int is the attribute number and doesn't need the same space.
        if self._type == int:
            return "Iq"
        # Floating point numbers are returned as doubles, again to allow for the biggest range
        # of values that a game may need.
        if self._type == float:
            return "Id"
        
        return None
        
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
        if name == "value":
            return super(nSyncAttribute, self).__getattribute__("_value")
        else:
            return super(nSyncAttribute, self).__getattribute__(name)
        
    ## Overrides the default __setattr__ behavior to make sure we do the necessary housekeeping
    #  when the actual value of the attribute being synced is done.  Also, we type check that value
    #  and throw an exception to make sure nobody tries to give us a type that we can't later encode
    #  into a network message.  This is also where all other possible options for attributes
    #  get checked and enforced, if need be.
    def __setattr__(self, name, value):
        if name == "value":
            if isinstance(value, self._type):
                super(nSyncAttribute, self).__setattr__("_isdirty", True)
                super(nSyncAttribute, self).__setattr__("_value", value)
            else:
                raise exceptions.dngSyncAttributeTypeError
        else:
            super(nSyncAttribute, self).__setattr__(name, value)
    

## nSyncObject is the class from which game objects that need to be synced must inherit.  After initializing
#  the class, you must declare which attributes will be synced over the network.  Afterwards, you can modify
#  those attributes at will and the network layer will automatically send out sync messages.  Note that you
#  cannot sync objects from the client to the server, so modifying attributes on the client is only useful
#  when you are predicting the action for players, but the client objects still need to inherit this class
#  so they can receive sync messages.
#
#  Syncing is currently naive and whether or not an object has been synced is a simple boolean state.
#  Maybe some day there will be a more detailed sync object that tracks which connections have been
#  synced, but for now, this naive object is all there is.
class nSyncObject(object):
    ## The list of attributes that are to be synced
    _attributes = None
    
    ## The current ID for the next new attribute
    __attrId = None
    
    ## If any attributes have been changed, then the object is marked dirty.
    _isdirty = None
    
    ## The ID of this object.  All network objects have unique IDs.
    _id = None
    
    ## The Type ID of this object.  All instances of each subclass will share the
    #  Type id that's assigned to their subclass.
    _typeid = None

    ## This init method should be called as soon as possible in subclasses so that an ID can be
    #  established.
    def __init__(self):
        super().__init__()
        self.__attributes = {}
        
        self._isdirty = True

        theList = GetSyncList()

        self._id = theList.GetNextId()
        self.__attrId = 0
        
        AddObjectType(self)
    
    ## Serialize this object to a string.  This method is named to be consistent with protobuffers,
    #  but does not use protobuffers to do anything.  Instead, it returns a tuple, where the first
    #  item is the string that represents this object, and the second item is the format string
    #  needed to unpack the object.  Both must be sent over the wire to the receiving end,
    #  after being embedded into a message that is handled by protobuffers.
    #
    #  This method only encodes attributes marked as dirty, but by default does not mark them
    #  as not dirty.  Pass True to indicate that you want the attributes marked clean, but keep
    #  in mind that when you do that, subsequent calls will not obtain the attributes again until
    #  their values actually change again.
    def SerializeToString(self, clean=False):
        formatString = "!"
        encAttrs = ""
        
        for key, value in self._attributes:
            if value.IsDirty():
                formatString += value.GetFormatString()
                encAttrs += value.Encode()
                
                if clean:
                    value.SetDirty(False)
        
        return (encAttrs, formatString)
    
    ## Subclasses must call this after declaring all attributes and stuff in order to finish setting
    #  up the object.  Without this call, the object will not sync.
    def Finalize(self):
        theList = GetSyncList()
        theList.AddSyncObject(self)
        
    ## Returns True if any syncable attributes are marked dirty.
    def IsDirty(self):
        return self._isdirty

    ## Add an attribute for this object.
    #
    #  @param name
    #                           'name' : The name of the attribute.
    #                           'type' : The type of the attribute.  Must be a type object.
    #                           'static' : Indicates that the value cannot be changed.  Default is False.
    #                                       Currently not implemented.
    #                           "initial" : The initial value.  This is required, and it must be an instance
    #                                       of the type given by the type parameter.
    def AddAttribute(self, **desc):
        if self._attributes.has_key(desc['name']):
            raise exceptions.dngSyncObjectAttributeError
        
        if isinstance(desc['initial'], desc['type']):
            self._attributes[desc['name'] ] = nSyncAttribute(
                                                name = desc['name'],
                                                type = desc['type'],
                                                value = desc['initial'],
                                                id = self.__attrId
                                                )
            self.__attrId = self.__attrId + 1
        else:
            raise exceptions.dngSyncAttributeTypeError
        
    ## Overrides the default __getattribute__ behavior to allow for registered syncable attributes
    #  to be treated as object.syncableattributes by calling code.  Basically, this is where the magic
    #  starts that lets objects get synced, transparent to the calling code.
    def __getattribute__(self, name):
        if super(nSyncObject, self).__getattribute__("_attributes").has_key(name):
            return super(nSyncObject, self).__getattribute__(name).value
        else:
            return super(nSyncObject, self).__getattribute__(name)
        
    ## Overrides the default __setattr__ behavior to allow for registered syncable attributes to be
    #  treated as object.syncableattributes by calling code.  If it's a syncable attribute, then
    #  the real work of tracking changes in the values so they can be synced is done in the
    #  nSyncAttribute object.  If not, it's passed on to let python just do its normal thing.
    def __setattr__(self, name, value):
        if super(nSyncObject, self).__getattribute__("_attributes").has_key(name):
            # Note that type checking happens in the nSyncAttribute class, not here.
            super(nSyncObject, self).__getattribute__(name).value = value
            self._isdirty = True
        else:
            super(nSyncObject, self).__getattribute__(name).value = value
        

## nSyncList holds the list of game objects that are to be synced over the network.  Periodically,
#  when an nSyncObject is changed, the network layer will automatically generate and send sync packets.
class nSyncList(object):
    ## holds the list of objects that have been created.
    __syncobjects = None
    
    ## Holds the list of objects that have been created, but haven't had their first sync.
    __newobjects = None
    
    ## Holds the list of objects that have been deleted from the game and are waiting to
    #  be cleaned up from memory.
    __deleted_objects = None
    
    ## Current ID, unassigned.  Id=0 is currently reserved for no reason whatsoever.
    __currentid = None

    def __init__(self):
        self.__syncobjects = []
        self.__newobjects = []
        self.__deleted_objects = []
        
        self.__currentid = 1

    ## Gets the list of objects that have been created.  They will be moved from the
    #  __newobjects list to the __syncobjects list when you call this.
    def GetNewObjects(self):
        aList = []
        
        for a in self.__newobjects:
            aList.append(a)
        
        while len(self.__newobjects) > 0:
            self.__syncobject.append(self.__newobjects.pop(0) )
            
        return aList

    def GetNextId(self):
        _id = self.__currentid
        
        self.__currentid = self.__current+1
        
        return _id

    def AddSyncObject(self, obj):
        self.__newobjects.append(obj)

    def DeleteSyncObject(self, obj):
        pass

## Call this function when you declare the class.  The library doesn't need to be
#  initialized or anything for this function to work.  But before you can connect
#  to anything, the game object list must know about every single possible class that
#  will be synced.
#
#  @todo update this function's documentation.
#
#  @param objType A type object representing the class.
#  @param options a dictionary containing options for the type.  Currently the only implemented
#                 option is "player", indicating that the object type is the player object.  Only
#                 one player object can exist.
#  @param typeId You can pass in a type ID and have it declared manually, allowing for backwards
#                compatibility, if need be.  Currently unimplemented.
def RegisterGameObjectType(objType, options={}, typeId=None):
    objList = GetGameObjectList()
    
    objList.AddObjectType(objType, options, typeId)
    

## Tracks and assigns numbers for each nSyncObject subclass.  It does absolutely
#  nothing else.
class nGameObjects(object):
    ## Current high number for new type IDs
    __currentid = None
    
    ## The dict of object types, keyed by id
    __types = None
    ## The dict of object ids, keyed by name
    __typeIds = None
    ## The dict of object options, keyed by id
    __options = None
    
    def __init__(self):
        self.__currentid = 1
        self.__types = {}
        self.__typeIds = {}
        self.__options = {}
        
    ## Adds a new type object to the list of available types and assigns an id to it.
    #
    #  @param newType the new type object to add.
    #  @param options a dictionary of options for the game object type.
    #  @param typeId a manual type ID for the game object type, used for backward compatibility.
    #                Currently unimplemented.
    #  @returns the new type id.  If the object is already in the list, returns the id
    #                   previously assigned.
    def AddObjectType(self, newType, options={}, typeId=None):
        newTypeName = newType.__name__
        
        if newTypeName not in self.__typesId:
            self.__typeIds[newTypeName] = self.__currentid
            self.__types[self.__currentid] = newType    
            self.__currentid = self.__currentid + 1
            self.__options[self.__currentid] = options
            
        return self.__types[self.__typeIds[newTypeName] ]
    
    ## Returns the object options, after given a typeId
    def GetObjectOptions(self, typeId):
        if typeId in self.__options:
            return self.__options[typeId]
        
        return None
    
    ## Returns a type object for the given type Id.  It does not return an instantiated object,
    #  just the type.
    #
    #  @param typeId The ID for the type you want to create.
    def NewObject(self, typeId):
        return self.__type[typeId]

__gameobjlist = None

__synclist = None

## Returns the nSyncList object.  Used internally by the network library, should not be used by games.
def GetSyncList():    
    global __synclist

    if __synclist == None:
        __synclist = nSyncList()

    return __synclist

## Use this to get the global game object list
def GetGameObjectList():
    global __gameobjlist
    
    if __gameobjlist == None:
        __gameobjlist = nGameObjects()
        
    return __gameobjlist




     

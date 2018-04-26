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
        self._attributes = {}
        
        self._isdirty = True

        theList = GetSyncList()

        self._id = theList.GetNextId()
        self.__attrId = 0
        
        self.AddAttribute(name="owner",
                          type=int,
                          initial=0 )
        
        # This probably isn't needed, but is kept "just in case".  It adds new instances to
        # the list of game object types, but those types should already be added before we
        # get here.
        #GetGameObjectList().AddObjectType(type(self) )
    
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
        if desc['name'] in self._attributes:
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
        if name in super().__getattribute__("_attributes"):
            return super().__getattribute__("_attributes")[name]
        else:
            return super().__getattribute__(name)
        
    ## Overrides the default __setattr__ behavior to allow for registered syncable attributes to be
    #  treated as object.syncableattributes by calling code.  If it's a syncable attribute, then
    #  the real work of tracking changes in the values so they can be synced is done in the
    #  nSyncAttribute object.  If not, it's passed on to let python just do its normal thing.
    def __setattr__(self, name, value):
        # First make sure we're not trying to directly access the _attributes method
        if name == "_attributes":
            super().__setattr__(name, value)
        elif name in super().__getattribute__("_attributes"):
            # Note that type checking happens in the nSyncAttribute class, not here.
            super().__getattribute__("_attributes")[name].value = value
            self._isdirty = True
        else:
            super().__setattr__(name, value)
        

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
        
        self.__currentid = self.__currentid + 1
        
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
        
        if newTypeName not in self.__typeIds:
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




     

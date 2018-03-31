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

from davenetgame import exceptions

## This class stores attributes that will be synced over the network.
class nSyncAttribute(object):
    ## The name of the attribute.  This probably isn't useful for this class to know, but hey,
    #  someday an instance of this class may need to go where everybody knows your name, and that
    #  won't be true of the instance doesn't know its own name.
    _name = None
    
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
    
    ## Checks to see if this attribute has been changed since the last time it was synced.
    def IsDirty(self):
        return self._isdirty
    
    ## This is the method that should be called when you want to know the type of the attribute
    #  that this class represents.  It would break all sorts of things if we override python's builtins
    #  to hide the fact that the actual type of this object is nSyncAttribute.
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
        
        AddObjectType(self)
        
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
                                                value = desc['initial']
                                                )
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
    ## holds the list of objects
    __syncobjects = None
    
    ## Current ID, unassigned.  Id=0 is currently reserved for no reason whatsoever.
    __currentid = None

    def __init__(self):
        self.__syncobjects = []
        self.__currentid = 1

    def GetNextId(self):
        _id = self.__currentid
        
        self.__currentid = self.__current+1
        
        return _id

    def AddSyncObject(self, obj):
        self.__syncobjects.insert(obj)

    def DeleteSyncObject(self, obj):
        pass

## Call this function when you declare the class.  The library doesn't need to be
#  initialized or anything for this function to work.  But before you can connect
#  to anything, the game object list must know about every single possible class that
#  will be synced.  The actual numbers will be arbitrarily assigned everytime the app
#  is loaded, so the server has to sync with every client upon connection.
#
#  @param objType A type object representing the class.
def RegisterGameObjectType(objType):
    objList = GetGameObjectList()
    
    objList.AddObjectType(objType)
    

## Tracks and assigns numbers for each nSyncObject subclass.  It does absolutely
#  nothing else.
class nGameObjects(object):
    ## Current high number for new type IDs
    __currentid = None
    
    ## The dict of object types, keyed by name
    __types = None
    
    def __init__(self):
        self.__currentid = 1
        self.__types = {}
        
    ## Adds a new type object to the list of available types and assigns an id to it.
    #
    #  @param newType the new type object to add.
    #  @returns the new type id.  If the object is already in the list, returns the id
    #                   previously assigned.
    def AddObjectType(self, newType):
        newTypeName = newType.__name__
        
        if newTypeName not in self.__types:
            self.__types[newTypeName] = self.__currentid
            self.__currentid = self.__currentid + 1
            
        return self.__types[newTypeName]

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




     

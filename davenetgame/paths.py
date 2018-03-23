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

# a collection of functions to handle paths

import os
import sys
#import log

_allpaths = {}

_appdirname = None

## Returns the directory separator for the current platform.
def DirSep():
    return os.linesep

## Expands a path that may include the special "~/" sequence to an absolute path.
def UnHome(path):
    return os.path.expanduser(path)

## Lists the directory given by path.
#  @param path : the path to list
#  @param includeDirs : if True, the list will include directories, but not the . and .. directories.
#  @param includeFiles : if True, the list will include filenames.
#  @return A list of everything asked for.
def ListDir(path, includeDirs=True, includeFiles = True):
    listing = []
    if os.path.isdir(path):
        for a in os.listdir( UnHome(path) ):
            if os.path.isdir(os.path.join(path, a) ):
                if includeDirs is True:
                    listing.append(a)
            else:
                if includeFiles is True:
                    listing.append( a )
        listing.sort()
    return listing

## Returns the last part of the path.  This *should* be the filename, including its extension, but in the
#  case where the last element is a directory, the directory name will be returned.
#  @param path the path to the file.
def GetLastPathElement(path):
    base, tail = os.path.split(path)
    return tail

## Returns the directory to a file.  It should be everything up to the file, e.g. /usr/bin/python would
#  return /usr/bin
#  @param path : the path to the file.
#  @return the directory.
def GetDir(path):
    base, tail = os.path.split(path)
    return base

## Returns the extension of the file, in lower case, without the period.
#  @param path : The path to the file.  This can actually be just a filename.
#  @return the extension of the file, in lower case, without the period.
def GetMimeExtension(path):
    lastpart = GetLastPathElement(path)
    base, tail = os.path.splitext(lastpart)
    if len(tail) > 0:
        return tail[1:].lower()
    else:
        return ""

## Returns a string containing the current username.  In Windows, if the win32api module is
#  unavailable, it'll return "Player 1", because that's funny.
#  @return the current logged in username.
def GetUsername():
    if sys.platform == "win32":
        try:
            return win32api.GetUserName()
        except:
            return "Player 1"
    else:
        return pwd.getpwuid(os.getuid())[0]

## Return the asset path desired.  If targetFile is not none, then it will join the filename to the asset path,
# returning a complete path to the file you want.  This allows you to open app asset files in a cross-platform
# way, run from the source directory, etc.  When you specify a targetFile, the string returned can be
# passed directly to open().
# @param path the program asset path desired, such as 'resource', 'civilizations', or 'flags'.
# @param targetFile Filename to join to the asset path, in which case the path returned points
#                               at this file.  Defaults to None.
# @return the path to the asset directory, with or without the filename you're wanting.
# 
# @todo make GetPath throw an exception or something instead if a path isn't known
def GetPath(path, targetFile=None):
    global _allpaths
    
    if _allpaths.has_key(path):
        if targetFile is None:
            return _allpaths[path]
        else:
            return JoinPaths(_allpaths[path], targetFile)
    else:
        print "Don't know path '" + path + "'!"
        print _allpaths
        return None

## Returns true if the path exists.
def Exists(path):
    return os.path.exists(path)

## Returns the last time modified for the path, when supported by the OS.
def ModifiedTime(path):
    statresults = os.stat(path)
    
    return statresults.st_mtime

## Returns true if the path given is a directory.
def IsDir(path):
    return os.path.isdir(path)

## Returns true if the path given is a file.
def IsFile(path):
    return os.path.isfile(path)

## Shortcut helper to get icons.
def GetIcon(icon):
    return JoinPaths(GetPath('graphics'), icon)

## InitializePaths initializes this module.  It must be called before any of the
#   really useful functions here can be used.
#   @param appDirName the name for application-specific directories.
#   @param thePaths a dictionary containing the paths you want to define and
#          strings to define them using / as a directory separator.  It will be
#          replaced with platform-specific directory separators.
def InitializePaths(appDirName, thePaths):
    global _allpaths
    global _appdirname

    _appdirname = appDirName

    # First determine where we're running from
    if sys.platform == 'win32':
        __home = os.path.expanduser('~/')
        __basepath = ''
        __share = ''
        __lib = ''
        __etc = 'etc'
    else:
        __basepath = sys.path[0]
        __home = os.path.expanduser('~')
        # installed to some system prefix
        if __basepath.startswith(sys.prefix):
            __share = os.path.join('share', appDirName)
            __lib = os.path.join('lib', 'lib' + appDirName)
            __etc = 'etc'
        # installed to any arbitrary prefix
        if  __basepath.endswith('/lib'):
            __basepath = os.path.dirname(__basepath)
            __share = os.path.join('share', appDirName)
            __lib = os.path.join('lib', 'lib' + appDirName)
            __etc = 'etc'
        # run from source directory
        else:
            __share = ''
            __lib = ''
            __etc = 'etc'
            
    # Now we need to iterate through the caller's paths and set each of them
    # up in _allpaths
    templist = []
    for key, value in thePaths.items():
        templist.append( [key, value.split("/") ] )

    # We have to iterate this way so the caller can have dependencies on previous
    # path definitions
    # todo: make it so that the caller can use previous paths in the new path definition
    #       this is low priority, I can copy and paste and make it work fine anyway.
    while len(templist) > 0:
        key, valueList = templist.pop(0)
        skipMe = False
        for a in range(len(valueList) ):
            valueList[a] = valueList[a].replace('__basepath', __basepath)
            valueList[a] = valueList[a].replace('__etc', __etc)
            valueList[a] = valueList[a].replace('__share', __share)
            valueList[a] = valueList[a].replace('__lib', __lib)
            valueList[a] = valueList[a].replace('__home', __home)
            # This one should never be used for share.  This module takes care of
            # it already.
            valueList[a] = valueList[a].replace('__appname', appDirName)
        _allpaths[key] = JoinPaths( *valueList )

## Returns the directory name for the app.    
def GetAppDirName():
    global _appdirname
    
    return _appdirname

## Joins the paths given in args.  You should never need to use this, but the paths module uses it
#  extensively.
def JoinPaths(*args):
    return os.path.normpath(os.path.expanduser(os.path.join(*args) ) )

## Makes a directory, with optional permissions as specified by the caller.
#  Returns True on success and False on failure
def MkDir(path, permissions = 0775):
    path = os.path.expanduser(path)
    if Exists(path):
        raise errors.DirectoryExistsError("Tried to create directory '" + path + "', but the path already exists!")
    
    try:
        os.makedirs(path, permissions )
        #log.Application("Created new directory: '" + path + "', with permissions '" + str(oct(permissions) ) + "'")
    except:
        #log.Error("Error creating new directory: '" + path + "', with permissions '" + str(permissions) + "'")
        raise errors.PathError("An unknown error has occured while creating directory '" + path + "' with permissions '" + str(permissions) + "'")

## Opens the file requested, in the mode requested.  No checks on the path are done.
def OpenFile(path, mode):
    try:
        fp = open(path, mode)
        return fp
    except:
        #log.Error("Error opening file " + str(path) + " for mode '" + str(mode) + "'.")
        return None

## A pass-through to os.walk.  See the python documentation for more information.
def Walk(path):
    return os.walk(path)




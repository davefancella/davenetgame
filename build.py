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

# Builds the game, whatever stuff has to be processed.  This is a quick and dirty solution,
# only intended for early development.  It should be replaced with a proper setup.py file at some point.

print "Building Dave's Stupid Network Game Library"
print
print "Building protocol files"

#cd ./davenetgame/messages
#pwd

#for a in *.proto
#do
#    echo "Building $a"
#    protoc -I=./ --python_out=./ ./$a
#done

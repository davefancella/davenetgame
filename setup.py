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

from distutils.core import setup

setup(  name="davenetgame",
        version='0.1.0.dev0',
        description="Dave's Stupid Network Game Library is a network library designed for games, written in pure python.",
        author='Dave Fancella',
        author_email='dave@davefancella.com',
        url='http://www.davefancella.com/',
        license="Apache 2.0",
        packages=[
                    'davenetgame',
                    'davenetgame/dispatch',
                    'davenetgame/gameobjects',
                    'davenetgame/messages',
                    'davenetgame/protocol',
                    'davenetgame/transport',
                    ],
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: Apache License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
        ],
        python_requires='>=3',
)



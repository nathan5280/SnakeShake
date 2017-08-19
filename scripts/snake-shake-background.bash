#!/usr/bin/env bash

# Copy the Env class to a directory where Blender can find it.
cp src/Env.py /Applications/blender.app/Contents/Resources/2.78/python/lib/python3.5/site-packages/snakeshake

# Start blender in the background (-b) and run the background SnakeShakeServer code on startup.
/Applications/blender.app/Contents/MacOS/blender -b -P src/SnakeShakeBGServer.py

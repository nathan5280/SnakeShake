# SnakeShake
Blender and Python remote integration to enable simulations of environments for Supervised and Reinforcement Learning.

## Motivation
As I kick off a number of Supervised and Reinforcement Learning projects for robotics projects it was immediately obvious that I need a way to simulate the environment to enable training in reasonable time frames.  I had some prior experience with [Blender](https://www.blender.org/), Python and distributed systems integration.   This project brings all of those skills together in a fun way.

Blender has fantastic Python integration that allows you to control or modify just about everything in the environment.  Through this simple example we can remotely move the camera around in the environment and render what it sees.  In my case this is the simulation of what a robot would see as it moves around in the environment.  I'm starting with simple objects and lighting to get started, but feel that I can leverage the power of Blender to render more and more elaborate environments as my algorithms improve.

## Implementation
The implementation consists of 3 main parts:
1. Env: The simulation environment. This class implements whatever is needed to create object in Blender.  It also exposes methods for the client to control actions in the environment.   This class is the key interface to the Blender API.  
2. Server: There are two versions of the Server.  One that runs inside of Blender when it has it's UI and one for when Blender is running in a background mode.  The main differences in these classes is how the foreground version integrates with Blender to keep the UI event loop alive and responsive.  These servers are build with [Pyro](https://pythonhosted.org/Pyro4/).
3. Client: The client class which remotely connects to the Env through the Server to drive actions in Blender.

## Setup & Try it Out
1. Install Blender
2. Install Pyro4
3. Start the name server to allow the client to find the running server without having to keep IP addresses and Port information in configuration files.

  ```
  python -m Pyro4.naming
  ```

4. Start the Server.  Note that you will need to figure out where on your computer you need to copy Env.py to for the Server to load it.

  **SnakeShakeFGServer.bash**

  ```  
  # Copy the Env class to a directory where Blender can find it.
  cp src/Arena.py /Applications/blender.app/Contents/Resources/2.78/python/lib/python3.5/site-packages/snakeshake

  # Start blender with the UI and load the SnakeShake foreground server.s
  /Applications/blender.app/Contents/MacOS/blender -P src/SnakeShakeFGServer.py
  ```

  **SnakeShakeBGServer.bash**

  ```
  # Copy the Env class to a directory where Blender can find it.
  cp src/Env.py /Applications/blender.app/Contents/Resources/2.78/python/lib/python3.5/site-packages/snakeshake

  # Start blender in the background (-b) and run the background SnakeShakeServer code on startup.
  /Applications/blender.app/Contents/MacOS/blender -b -P src/SnakeShakeBGServer.py
  ```

5. Start the Client.  In this case I have a simple 'Driver' client that allows you to move the camera around using the arrow keys.  Shift arrow will double the size of the moves.

  ```
  python DriverClient.py
  ```

## Extend SnakeShake for your project.
The only changes you should need to make are in the Env and Client classes.  In the end the Pyro remoting hides the complexities of the RPC and it feels like you are just writing two classes that interact through normal method calls.  The only exception to this is if you are passing objects that are not serializable by the serializers in Pyro.  Because my implementation is relatively simple, I haven't included anything about customizing the serializers.  There is information on how to customize the serializers for your custom classes out there, but it was a bit hard to find.

## Technology Stack
<p align="center">
  <img height="75" hspace="25" src="https://user-images.githubusercontent.com/28061825/29490208-27bb242a-84f2-11e7-98bd-83818d251dc7.png">
  <img height="75" hspace="25" src="https://user-images.githubusercontent.com/28061825/29490207-27baf5d6-84f2-11e7-8ac4-7eb758aa12b8.png">
  <img height="75" hspace="25" src="https://user-images.githubusercontent.com/28061825/29490209-27bd4976-84f2-11e7-9d19-86b46f8e8c10.png">
</p>

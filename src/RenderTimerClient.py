import sys
import Pyro4
import math
import time
from curses import wrapper

'''
Simple client to drive the camera around in the Blender simulated environment.
'''

def deg_2_rad(d):
    '''
    Convert between degrees and radians.

    Input:
        d: Degrees to convert

    Output:
        Radian representation of the input
    '''
    return d/360*2*math.pi

def main():
    '''
    Simple client to measure how fast Blender can render at different resolutions.
    '''
    # Connect to the Snake Shake Server running in Blender.  See Readme
    # for the steps to get this up and running.
    sys.excepthook = Pyro4.util.excepthook
    env = Pyro4.Proxy("PYRONAME:Env")

    # Define the size of the steps and rotations to take.
    reg_delta_pos = 2**0.5
    reg_delta_rot = deg_2_rad(5)
    fast_delta_pos = 2 * reg_delta_pos
    fast_delta_rot = 2 * reg_delta_rot

    loops = 100
    rotation = reg_delta_rot

    t1 = time.time()
    for i in range(loops):
        env.move_camera(0,0,rotation)
        rotation = -1 * rotation
        if i % 10 == 0:
            print(i)
    t2 = time.time()

    x, y = env.get_render_resolution()
    print('Default Resolution ({} : {}) {}: {:.4f}'.format(x, y, loops, (t2-t1)/loops))

    env.set_render_resolution(32, 32)
    t1 = time.time()
    for i in range(loops):
        env.move_camera(0,0,rotation)
        rotation = -1 * rotation
        if i % 10 == 0:
            print(i)
    t2 = time.time()

    x, y = env.get_render_resolution()
    print('Default Resolution ({} : {}) {}: {:.4f}'.format(x, y, loops, (t2-t1)/loops))

if __name__ == '__main__':
    main()

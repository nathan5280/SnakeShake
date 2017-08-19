import sys
import Pyro4
import math
import time
import curses
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

def rad_2_deg(r):
    '''
    Convert radians to degrees.

    Input:
        r: Radians to convert

    Output:
        Degree representation of the input
    '''
    return r*360/(2*math.pi)

def direction(direction, distance):
    '''
    Calculate the change in x, y location based on a direction and distance

    Input:
        direction: The direction to travel
        distance: The distance to travel

    Output:
        delta_x: Change in the x direction
        delta_y: Change in the y direction
    '''
    return distance * math.cos(direction), distance * math.sin(direction)

def main(stdscr):
    '''
    Simple curses based text UI to allow driving of the camera with arrow keys.

    Size of the steps that the arrow keys drive the camera can be doubled by
    holding down the shift key.

    Input:
        stdscr: Curses screen to write to
    '''
    def clear_screen(stdscr):
        '''
        Clear the screen and present the prompt.

        Input:
            stdscr: Curses screen to write to
        '''
        stdscr.clear()
        stdscr.addstr('(q)uit Driver, (Q)uit Blender, (c)lear, (r)eset, arrows to move:\n')

    def show_move(stdscr, move_name, x, y, r):
        '''
        Display the direction/rotation and the new position.

        Input:
            stdscr: Curses screen to write to
            move_name: Name to display for the move
            x: New x location of the camera
            y: New y Location of the camera
            r: New direction of the camera
        '''
        clear_screen(stdscr)
        stdscr.addstr('{}: {}, {}, {}\n'.format(move_name, round(x,2), round(y,2), round(rad_2_deg(r),2)))

    # Connect to the Snake Shake Server running in Blender.  See Readme
    # for the steps to get this up and running.
    sys.excepthook = Pyro4.util.excepthook
    env = Pyro4.Proxy("PYRONAME:Env")

    # Get everything ready so the UI looks clean and consistent.
    clear_screen(stdscr)

    # Define the size of the steps and rotations to take.
    reg_delta_pos = 2**0.5
    reg_delta_rot = deg_2_rad(5)
    fast_delta_pos = 2 * reg_delta_pos
    fast_delta_rot = 2 * reg_delta_rot

    # Get the current camera rotations so we can calculate the delta x and y if
    # move first.
    _, _ , heading = env.get_camera_position()
    print(heading)

    quit = False
    while not quit:
        c = stdscr.getch()
        if c == ord('q'):
            break;

        elif c == ord('Q'):
            # Request that Snake Shake shutdown and stop the Blender environment.
            env.quit()
            break;

        elif c == ord('c'):
            clear_screen(stdscr)

        elif c == ord('r'):
            x, y, heading = env.reset()
            show_move(stdscr, 'Reset', x, y, heading)

        elif c == curses.KEY_LEFT:
            x, y, heading = env.move_camera(0,0,reg_delta_rot)
            show_move(stdscr, 'Left', x, y, heading)

        elif c == curses.KEY_RIGHT:
            x, y, heading = env.move_camera(0,0,-reg_delta_rot)
            show_move(stdscr, 'Right', x, y, heading)

        elif c == curses.KEY_DOWN:
            dx, dy = direction(heading + math.pi/2, reg_delta_pos)
            x, y, heading = env.move_camera(-dx, -dy, 0)
            show_move(stdscr, 'Back', x, y, heading)

        elif c == curses.KEY_UP:
            dx, dy = direction(heading + math.pi/2, reg_delta_pos)
            x, y, heading = env.move_camera(dx, dy, 0)
            show_move(stdscr, 'Forward', x, y, heading)

        elif c == curses.KEY_SLEFT:
            x, y, heading = env.move_camera(0,0,fast_delta_rot)
            show_move(stdscr, 'Fast Left', x, y, heading)

        elif c == curses.KEY_SRIGHT:
            x, y, heading = env.move_camera(0,0,-fast_delta_rot)
            show_move(stdscr, 'Fast Right', x, y, heading)

        elif c == 336:  # Shift down arrow
            dx, dy = direction(heading + math.pi/2, fast_delta_pos)
            x, y, heading = env.move_camera(-dx, -dy, 0)
            show_move(stdscr, 'Fast Back', x, y, heading)

        elif c == 337:  # Shift up arrow
            dx, dy = direction(heading + math.pi/2, fast_delta_pos)
            x, y, heading = env.move_camera(dx, dy, 0)
            show_move(stdscr, 'Fast Forward', x, y, heading)

        else:
            # Unrecognized key, ignore it
            stdscr.addstr(str(c))

if __name__ == '__main__':
    # Curses wrapper around our code.
    wrapper(main)

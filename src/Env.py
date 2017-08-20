# Blender API, and math helper methods
import bpy, mathutils
import os, math

# Py Remote Object Module to support the RPC connection.
import Pyro4

'''
This is the working part of the Snake Shake implementation.  This is where
the code is that runs inside of Blender.   Create methods here and expose them
through Pyro so that the client can call them as if they were local methods in
the same Python environment.

Be careful about what object are passed in the method calls as Pyro need to be
able to serialize them.  See the Pyro documentation for information on how to
set the serializer and security notices.
'''

# Expose this interface to external clients.
# Let Pyro manage the instance of this class.  (One per proxy connection.)
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Env(object):
    def __init__(self, quit_request):
        '''
        Set up the Environment.

        Input:
            - quit_request: Server method to request shutdown.
        '''
        print('Env: Initializing')
        self._quit_request = quit_request

        # Information on how images rendered to disk will be named and indexed.
        self._image_idx = 1

        # Get the Environmentto a known state.
        self.reset()

    def ping(self, s):
        '''
        Respond to ping request from client to verify the Env is running.
        '''
        print('Env: Ping',s)
        return s

    def reset(self):
        # This will all get replaced when we get the methods to create and
        # configure the Env from imported objects.
        print('Env: Resetting Camera')
        cam = bpy.data.objects['Camera']
        cam_p = cam.location
        cam_r = cam.rotation_euler

        cam_p.x, cam_p.y, cam_p.z = 15, 15, 0
        cam_r.x, cam_r.y, cam_r.z = math.pi/2, 0, math.pi*3/4
        self._render()
        return cam_p.x, cam_p.y, cam_r.z

    def get_camera_position(self):
        '''
        Get the x, y, z location of the camera.
        '''
        cam = bpy.data.objects['Camera']
        cam_p = cam.location
        cam_r = cam.rotation_euler
        return cam_p.x, cam_p.y, cam_r.z

    def move_camera(self, dx, dy, drz):
        '''
        Move the camera by the delta position and rotation in the
        XY plane.

        Input:
            - dx: Change along the X-axis
            - dy: Change along the Y-axis
            - drz: Change in rotation about the Z-axis
        Return:
            - x, y, rz: the new position of the camera.
        '''

        print('Env: Move dx={}, dy={}, rz={}'.format(dx,dy,drz))

        cam = bpy.data.objects['Camera']
        cam_p = cam.location
        cam_r = cam.rotation_euler

        cam_p.x += dx
        cam_p.y += dy
        cam_p.z = 0

        cam_r.x = math.pi/2
        cam_r.y = 0
        cam_r.z += drz

        self._render()

        return cam_p.x, cam_p.y, cam_r.z

    def get_render_resolution(self):
        '''
        Get the current render resolution settings.

        Input:

        Output:
            - x resolution
            - y resolution
        '''
        return bpy.data.scenes["Scene"].render.resolution_x, \
                bpy.data.scenes["Scene"].render.resolution_y

    def set_render_resolution(self, new_x_resolution, new_y_resolution):
        '''
        Set the render resolution

        Input:
            - new_x_resolution:
            - new_y_resolution:
        '''
        bpy.data.scenes["Scene"].render.resolution_x = new_x_resolution
        bpy.data.scenes["Scene"].render.resolution_y = new_y_resolution

    def quit(self):
        '''
        Request to shutdown the Env.
        '''
        print('Env: Quitting')
        # Call back to the server provided method to request it to quit.
        self._quit_request()

    def _render(self):
        '''
        Render the image to disk.
        '''
        bpy.ops.render.render(use_viewport=True)
        # bpy.context.scene.render.filepath = 'img/n{0:05d}.png'.format(self._image_idx)
        bpy.context.scene.render.filepath = 'img/n.png'.format(self._image_idx)
        self._image_idx += 1
        bpy.ops.render.render(write_still=True)

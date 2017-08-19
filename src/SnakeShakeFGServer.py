import bpy
import Pyro4
import select
from snakeshake.Env import Env

# Make sure the server is only using one thread to not confuse Blender
Pyro4.config.SERVERTYPE="multiplex"

class SnakeShakeFGServer(object):
    '''
    Pyro4 server implementation that runs in a foreground Blender environment.
    This server integrates with the Blender event loop to keep the UI alive and
    responsive.  This is done by implementing a Blender Modal Operator.  This operator
    adds an periodic event to the Blender event queue.  When Blender processes
    the event it calls the process_events method in this Server.  The Server checks
    for any queued RPC requests on its socket and processes them before returning
    control back to the Blender event loop.

    This script loads immediately when Blender starts.  It sets everything up and
    then returns control to Blender.
    '''
    def __init__(self, modal_operator_cancel):
        """
        Processor that is called by Blender Modal Operator periodically.
        """
        self._daemon = Pyro4.Daemon()

        # Time to wait on the socket for client requests.  This is pretty
        # short so that control is quickly returned to Blender.
        self._socket_wait = 0.01
        self._quit = False

        # Create the Env object that we are exposing and tell it
        # where to call if a quit request is received from the client.
        self._env = Env(self._quit_request)
        uri = self._daemon.register(self._env, 'Env')

        # Register the server with the name server so that clients can the
        # server on the network.
        ns = Pyro4.locateNS()
        ns.register('Env', uri)

        # Method to call when the client requests the server to shutdown.
        self._modal_operator_cancel = modal_operator_cancel

    def process_events(self, context, event):
        """
        Process all queued Pyro events and then return if nothing is available for
        socket_wait time.   This keeps from blocking the Blender event loop.
        """
        more_events = True

        while more_events:
            s,_,_ = select.select(self._daemon.sockets,[],[], self._socket_wait)
            if s:
                # Process the events.  Pyro will call the exposed methods in the
                # Env class.
                self._daemon.events(s)
            else:
                # no more events, stop the loop, we'll get called again soon anyway
                more_events = False

        if self._quit:
            print('SnakeShakeServer: Quiting')

            # Stop the timer in Blender so it doesn't make any calls to the
            # server that we are shutting down.
            print('SnakeShakeServer: Cancelling modal operator')
            self._modal_operator_cancel(context)

            # Unregister the server so that the name server doesn't hand out dead connections.
            self._daemon.unregister(self._env)
            self._daemon.close()
            self._daemon = None
            print('SnakeShakeServer: Stopped')
            print('SnakeShakeServer: Quiting Blender')
            bpy.ops.wm.quit_blender()

    def _quit_request(self):
        '''
        Process the client generated request from the Env to shutdown.
        '''
        print('SnakeShakeServer: Quit request')
        self._quit = True

class PyroModalTimerOperator(bpy.types.Operator):
    '''
    Connect into the Blender event loop.  When the timer expires Blender
    calls the modal() method which processes Pyro events and then returns
    control back to Blender event loop.   Control from this script needs
    to be returned to Blender to keep the user inteface active.
    '''
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Pyro Modal Timer Operator"

    def __init__(self):
        print('PyroModalTimerOperator: Modal operator init')
        self._timer = None

        # Frequency for Blender to call this server to process remote requests.
        # This is fairly slow, but when running in the UI mode, it is nice to
        # balance things towards the UI and not the remote server.
        self._frequence = 1

        # Create the server and register the method to initiate a shutdown.
        self._pyro_event_processor = SnakeShakeFGServer(self._cancel)

    def modal(self, context, event):
        '''
        Method called by Blender when the timer expires.
        '''
        if event.type == 'TIMER':
            # Pass control to the server so it can process RPC requests.
            self._pyro_event_processor.process_events(context, event)

        # Keep everything running in Blender.
        return {'PASS_THROUGH'}

    def execute(self, context):
        '''
        Method called by Blender to setup the operator.
        '''
        print('PyroModalTimerOperator: Setting up modal timmer')
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/self._frequence, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _cancel(self, context):
        # Clean things up as the operator exits.
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    '''
    Register the timer with Blender.
    '''
    bpy.utils.register_class(PyroModalTimerOperator)


def unregister():
    '''
    Unregister the timer with Blender.
    '''
    bpy.utils.unregister_class(PyroModalTimerOperator)

if __name__ == '__main__':
    # Register the timer with Blender.
    register()

    # TODO: What is this doing?
    bpy.ops.wm.modal_timer_operator()

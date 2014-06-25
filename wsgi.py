from string import Template

class State:
    Off, On = range(2)

class Mode:
    Heat, Cool, Fan, Dry = range(4)

class Ion:
    Off, On = range(2)

class FullEffect:
    Off, On = range(2)

class FanStrength:
    Auto, Low, Medium, High = range(4)

class RemoteState:
    """The state off the Remote"""

    def __init__(self):
        self.state        = State.On
        self.mode         = Mode.Heat
        self.ion          = Ion.Off
        self.full_effect  = FullEffect.On
        self.temperature  = 23
        self.fan_strength = FanStrength.Auto

def bool_to_visibility(value):
    return 'show' if value else 'hidden'

def mode_uses_abs_temp(remote_state):
    return remote_state.mode == Mode.Heat or remote_state.mode == Mode.Cool

remote_state = RemoteState()

def generate_page():
    with open ("myindex.html", "r") as myfile:
        data = myfile.read()
        data = data.replace('\n', '')
        data = Template(data).substitute(
            temp_absolute_visibility=bool_to_visibility(mode_uses_abs_temp(remote_state)),
            temp_relative_visibility=bool_to_visibility(not mode_uses_abs_temp(remote_state))
            )
    return data

def handle_mode_request(path):
    global remote_state

    if path.startswith('/remote/mode/heat'):
        remote_state.mode        = Mode.Heat
        remote_state.temperature = 23

    if path.startswith('/remote/mode/cool'):
        remote_state.mode        = Mode.Cool
        remote_state.temperature = 20

    if path.startswith('/remote/mode/fan'):
        remote_state.mode        = Mode.Fan
        remote_state.temperature = 0

    if path.startswith('/remote/mode/dry'):
        remote_state.mode        = Mode.Dry
        remote_state.temperature = 0


# Basic WSGI application code
def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])

    path = env['PATH_INFO']

    global remote_state;

    if path[:10] == '/bootstrap':
        with open ("myindex.html", "r") as myfile:
            data=myfile.read().replace('\n', '')
        return data

    if not path.startswith('/remote'):
        return "<html><body>Apa</body></html>"

    if path.startswith('/remote/mode'):
        handle_mode_request(path);

    return generate_page()

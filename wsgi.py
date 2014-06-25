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

# The global instance.
remote_state = RemoteState()


def bool_to_mode_active(value):
    return 'active' if value else 'not-active'

def mode_uses_abs_temp(mode):
    return mode == Mode.Heat or mode == Mode.Cool

def make_bold(what):
    return "<b>"+ what + "</b>"

def decorate_if_active(what, active):
    if active:
        return make_bold(what)
    return what

def generate_temperature_list_item(temperature, active):
    return '<li><a href="/remote/temperature/' + str(temperature) + '">' + decorate_if_active(str(temperature), active) + '</a></li>'

def generate_temperature_list_from_list(temperatures):
    data = ""
    for temperature in temperatures:
        data += generate_temperature_list_item(temperature, temperature == remote_state.temperature)
    return data

def generate_absolute_temperature_list():
    return generate_temperature_list_from_list(range(18, 32 + 1))

def generate_relative_temperature_list():
    return generate_temperature_list_from_list(range(-2, 2 + 1))

def generate_temperature_list():
    if mode_uses_abs_temp(remote_state.mode):
        return generate_absolute_temperature_list()
    return generate_relative_temperature_list()

def generate_page():
    with open ("myindex.html", "r") as myfile:
        data = myfile.read()
        data = data.replace('\n', '')
        data = Template(data).substitute(
            mode_heat_active=bool_to_mode_active(remote_state.mode == Mode.Heat),
            mode_cool_active=bool_to_mode_active(remote_state.mode == Mode.Cool),
            mode_fan_active =bool_to_mode_active(remote_state.mode == Mode.Fan),
            mode_dry_active =bool_to_mode_active(remote_state.mode == Mode.Dry),
            temperature=remote_state.temperature,
            temperature_list=generate_temperature_list()
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

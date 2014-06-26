from string import Template

class State:
    Off, On = range(2)

class Mode:
    Heat, Cool, Fan, Dry = range(4)

class FanStrength:
    Auto, Low, Medium, High = range(4)

class RemoteState:
    """The state off the Remote"""

    def __init__(self):
        self.state        = State.On
        self.mode         = Mode.Heat
        self.full_effect  = False
        self.ion          = False
        self.swing        = False
        self.temperature  = 23
        self.fan_strength = FanStrength.Auto

# The global instance.
remote_state = RemoteState()

# TODO: 10 is a valid temperature for mode == Heat
# +1 to become inclusive
valid_absolute_temperatures = range(18, 32 + 1)
valid_relative_temperatures = range(-2, 2  + 1)

def bool_to_active(value):
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
    return generate_temperature_list_from_list(valid_absolute_temperatures)

def generate_relative_temperature_list():
    return generate_temperature_list_from_list(valid_relative_temperatures)

def generate_temperature_list():
    if mode_uses_abs_temp(remote_state.mode):
        return generate_absolute_temperature_list()
    return generate_relative_temperature_list()

def generate_page():
    with open ("myindex.html", "r") as myfile:
        data = myfile.read()
        data = data.replace('\n', '')
        data = Template(data).substitute(
            mode_heat_active   = bool_to_active(remote_state.mode == Mode.Heat),
            mode_cool_active   = bool_to_active(remote_state.mode == Mode.Cool),
            mode_fan_active    = bool_to_active(remote_state.mode == Mode.Fan),
            mode_dry_active    = bool_to_active(remote_state.mode == Mode.Dry),
            full_effect_active = bool_to_active(remote_state.full_effect),
            ion_active         = bool_to_active(remote_state.ion),
            swing_active       = bool_to_active(remote_state.swing),
            temperature=remote_state.temperature,
            temperature_list=generate_temperature_list()
            )
    return data

def valid_temperatures(mode):
    return valid_absolute_temperatures if mode_uses_abs_temp(mode) else valid_relative_temperatures

def is_valid_temperature(temperature, mode):
    return temperature in valid_temperatures(mode)

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

def handle_temperature_request(path):
    global remote_state

    temperature_str = path[len('/remote/temperature/'):]
    if temperature_str == "":
        # Do nothing ATM
        return
    else:
        if temperature_str[0] == '-':
            if temperature_str[1:].isdigit():
                temperature = -int(temperature_str[1:])
            else:
                # Do nothing ATM
                return
        else:
            if temperature_str.isdigit():
                temperature = int(temperature_str)
            else:
                # Do nothing ATM
                return

        if is_valid_temperature(temperature, remote_state.mode):
            remote_state.temperature = temperature


def handle_full_effect_request(path):
    global remote_state

    remote_state.full_effect = not remote_state.full_effect


def handle_ion_request(path):
    global remote_state

    remote_state.ion = not remote_state.ion


def handle_swing_request(path):
    global remote_state

    remote_state.swing = not remote_state.swing


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
        handle_mode_request(path)

    if path.startswith('/remote/temperature/'):
        handle_temperature_request(path)

    if path.startswith('/remote/full_effect'):
        handle_full_effect_request(path)

    if path.startswith('/remote/ion'):
        handle_ion_request(path)

    if path.startswith('/remote/swing'):
        handle_swing_request(path)

    return generate_page()

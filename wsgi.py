from string import Template

class Mode:
    Heat, Cool, Fan, Dry = range(4)

class FanSpeed:
    Auto, Low, Medium, High = range(4)
    to_string = ['Auto', 'Low', 'Medium', 'High']

class RemoteState:
    """The state of the Remote"""

    def __init__(self):
        self.state       = False
        self.mode        = Mode.Heat
        self.full_effect = False
        self.ion         = False
        self.swing       = False
        self.temperature = 23
        self.fan_speed   = FanSpeed.Auto

class Options:
    """Options"""
    advanced = True

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

def generate_fan_speed_list():
    return '<li><a href="/remote/fan_speed/auto">'   + decorate_if_active('Auto',   remote_state.fan_speed == FanSpeed.Auto)   + '</a></li>' + \
           '<li><a href="/remote/fan_speed/low">'    + decorate_if_active('Low',    remote_state.fan_speed == FanSpeed.Low)    + '</a></li>' + \
           '<li><a href="/remote/fan_speed/medium">' + decorate_if_active('Medium', remote_state.fan_speed == FanSpeed.Medium) + '</a></li>' + \
           '<li><a href="/remote/fan_speed/high">'   + decorate_if_active('High',   remote_state.fan_speed == FanSpeed.High)   + '</a></li>'    

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

def generate_on_off_indicator(value):
    icon_color = 'success' if value else "danger"
    icon_text  = 'ON' if value else 'OFF'
    return '<span class="label label-' + icon_color + '">' + icon_text + ' <span class="glyphicon glyphicon-off"></span></span>'

def generate_hidden_start(doit):
    return '<div class="hidden">' if doit else ''

def generate_hidden_end(doit):
    return '</div>' if doit else ''

def generate_page():
    with open ("myindex.html", "r") as myfile:
        data = myfile.read()
        #        data = data.replace('\n', '')
        data = Template(data).substitute(
            mode_heat_active   = bool_to_active(remote_state.mode == Mode.Heat),
            mode_cool_active   = bool_to_active(remote_state.mode == Mode.Cool),
            mode_fan_active    = bool_to_active(remote_state.mode == Mode.Fan),
            mode_dry_active    = bool_to_active(remote_state.mode == Mode.Dry),
            full_effect_active = bool_to_active(remote_state.full_effect),
            ion_active         = bool_to_active(remote_state.ion),
            swing_active       = bool_to_active(remote_state.swing),
            temperature        = remote_state.temperature,
            temperature_list   = generate_temperature_list(),
            fan_speed          = FanSpeed.to_string[remote_state.fan_speed],
            fan_speed_list     = generate_fan_speed_list(),
            on_off_indicator   = generate_on_off_indicator(remote_state.state),
            advanced_start     = generate_hidden_start(not Options.advanced),
            advanced_end       = generate_hidden_end(not Options.advanced),
            simple_start       = generate_hidden_start(Options.advanced),
            simple_end         = generate_hidden_end(Options.advanced),
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

def handle_fan_speed_request(path):
    if path.startswith('/remote/fan_speed/auto'):
        remote_state.fan_speed = FanSpeed.Auto

    if path.startswith('/remote/fan_speed/low'):
        remote_state.fan_speed = FanSpeed.Low

    if path.startswith('/remote/fan_speed/medium'):
        remote_state.fan_speed = FanSpeed.Medium

    if path.startswith('/remote/fan_speed/high'):
        remote_state.fan_speed = FanSpeed.High

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


def handle_on_off_request(path):
    global remote_state

    remote_state.state = not remote_state.state


def handle_simple_request(path):
    Options.advanced = False


def handle_advanced_request(path):
    Options.advanced = True

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

    if path.startswith('/remote/fan_speed/'):
        handle_fan_speed_request(path)

    if path.startswith('/remote/temperature/'):
        handle_temperature_request(path)

    if path.startswith('/remote/full_effect'):
        handle_full_effect_request(path)

    if path.startswith('/remote/ion'):
        handle_ion_request(path)

    if path.startswith('/remote/swing'):
        handle_swing_request(path)

    if path.startswith('/remote/on_off'):
        handle_on_off_request(path)

    if path.startswith('/remote/simple'):
        handle_simple_request(path)

    if path.startswith('/remote/advanced'):
        handle_advanced_request(path)

    return generate_page()

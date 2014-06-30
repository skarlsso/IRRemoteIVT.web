from string import Template
from Cookie import SimpleCookie

def bool_to_str(value):
    return "True" if value else "False"

def str_to_bool(str):
    if str == "True":
        return True
    elif str == "False":
        return False
    else:
        return None

# State helpers
def state_to_str(state):
    return bool_to_str(state)

def state_from_str(str):
    return str_to_bool(str)

# Mode helpers
class Mode:
    Heat, Cool, Fan, Dry = range(4)

mode_to_str_map = { Mode.Heat: 'heat', Mode.Cool: 'cool', Mode.Fan: 'fan', Mode.Dry: 'dry' }
str_to_mode_map = { value: key for key, value in mode_to_str_map.iteritems() }

def mode_to_str(mode):
    return mode_to_str_map[mode] if mode in mode_to_str_map else None

def mode_from_str(str):
    return str_to_mode_map[str] if str in str_to_mode_map else None

# FanSpeed helpers
class FanSpeed:
    Auto, Low, Medium, High = range(4)

fan_speed_to_str_map = { FanSpeed.Auto: 'auto', FanSpeed.Low: 'low', FanSpeed.Medium: 'medium', FanSpeed.High: 'high'}
str_to_fan_speed_map = { value: key for key, value in fan_speed_to_str_map.iteritems() }

def fan_speed_to_str(fan_speed):
    return fan_speed_to_str_map[fan_speed] if fan_speed in fan_speed_to_str_map else None

def fan_speed_from_str(str):
    return str_to_fan_speed_map[str] if str in str_to_fan_speed_map else None

# Temperature helpers
# TODO: 10 is a valid temperature for mode == Heat
# +1 to become inclusive
valid_absolute_temperatures = range(18, 32 + 1)
valid_relative_temperatures = range(-2, 2  + 1)

default_temperatures = { Mode.Heat: 23, Mode.Cool: 20, Mode.Fan: 0, Mode.Dry: 0}

def temperature_to_str(temperature):
    return str(temperature)

def temperature_from_str(str):
    if str == "":
        return None
    else:
        if str[0] == '-':
            if str[1:].isdigit():
                return -int(str[1:])
            else:
                return None
        else:
            if str.isdigit():
                return int(str)
            else:
                return None

def mode_uses_abs_temp(mode):
    return mode == Mode.Heat or mode == Mode.Cool

def valid_temperatures(mode):
    return valid_absolute_temperatures if mode_uses_abs_temp(mode) else valid_relative_temperatures

def is_valid_temperature(temperature, mode):
    return temperature is not None and temperature in valid_temperatures(mode)

def default_temperature(mode):
    return default_temperatures[mode]

# FullEffect helpers
def full_effect_to_str(full_effect):
    return bool_to_str(full_effect)

def full_effect_from_str(str):
    return str_to_bool(str)

# Ion helpers
def ion_to_str(ion):
    return bool_to_str(ion)

def ion_from_str(str):
    return str_to_bool(str)

# Swing helpers
def swing_to_str(swing):
    return bool_to_str(swing)

def swing_from_str(str):
    return str_to_bool(str)


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

# View helpers
class View:
    Advanced, Simple = range(2)

view_to_str_map = { View.Advanced: 'advanced', View.Simple: 'simple'}
str_to_view_map = { value: key for key, value in view_to_str_map.iteritems() }

def view_to_str(view):
    return view_to_str_map[view]

def view_from_str(str):
    return str_to_view_map[str]

class Options:
    """Options"""

    def __init__(self):
        self.view = View.Advanced

# The global instance.
remote_state = RemoteState()

options = Options()

def bool_to_active(value):
    return 'active' if value else 'not-active'

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

def generate_page(start_response):
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
            temperature        = temperature_to_str(remote_state.temperature),
            temperature_list   = generate_temperature_list(),
            fan_speed          = fan_speed_to_str(remote_state.fan_speed),
            fan_speed_list     = generate_fan_speed_list(),
            on_off_indicator   = generate_on_off_indicator(remote_state.state),
            advanced_start     = generate_hidden_start(options.view != View.Advanced),
            advanced_end       = generate_hidden_end(options.view != View.Advanced),
            simple_start       = generate_hidden_start(options.view != View.Simple),
            simple_end         = generate_hidden_end(options.view != View.Simple),
            )


    cookies = generate_cookies()
    headers = cookies_to_headers(cookies)
    headers.append(('content-type', 'text/html'))

    start_response('200 OK', headers)

    return data


def set_view(view_str):
    global remote_state
    view = view_from_str(view_str)
    if not view is None:
        options.view = view

def set_state(state_str):
    global remote_state
    state = state_from_str(state_str)
    if not state is None:
        remote_state.state = state

def set_mode(mode_str):
    global remote_state
    mode = mode_from_str(mode_str)
    if not mode is None:
        remote_state.mode = mode

def set_fan_speed(fan_speed_str):
    global remote_state
    fan_speed = fan_speed_from_str(fan_speed_str)
    if not fan_speed is None:
        remote_state.fan_speed = fan_speed

def set_full_effect(full_effect_str):
    global remote_state
    full_effect = full_effect_from_str(full_effect_str)
    if not full_effect is None:
        remote_state.full_effect = full_effect

def set_ion(ion_str):
    global remote_state
    ion = ion_from_str(ion_str)
    if not ion is None:
        remote_state.ion = ion

def set_swing(swing_str):
    global remote_state
    swing = swing_from_str(swing_str)
    if not swing is None:
        remote_state.swing = swing

def set_default_temperature(mode):
    global remote_state
    remote_state.temperature = default_temperature(mode)

def set_temperature(temperature_str):
    global remote_state
    temperature = temperature_from_str(temperature_str)
    if is_valid_temperature(temperature, remote_state.mode):
        remote_state.temperature = temperature


def toggle_full_effect():
    global remote_state
    remote_state.full_effect = not remote_state.full_effect

def toggle_ion():
    global remote_state
    remote_state.ion = not remote_state.ion

def toggle_swing():
    global remote_state
    remote_state.swing = not remote_state.swing

def toggle_state():
    global remote_state
    remote_state.state = not remote_state.state


def handle_mode_request(path):
    set_mode(path[len("/remote/mode/"):])
    # The temperature is reset when the mode is changed.
    set_default_temperature(remote_state.mode)

def handle_fan_speed_request(path):
    set_fan_speed(path[len('/remote/fan_speed/'):])

def handle_temperature_request(path):
    set_temperature(path[len('/remote/temperature/'):])

def handle_full_effect_request(path):
    toggle_full_effect()

def handle_ion_request(path):
    toggle_ion()

def handle_swing_request(path):
    toggle_swing()

def handle_state_request(path):
    toggle_state()

def handle_simple_request(path):
    options.view = View.Simple

def handle_advanced_request(path):
    options.view = View.Advanced


def read_cookies(env):
    if not 'HTTP_COOKIE' in env:
        return

    cookies = SimpleCookie(env['HTTP_COOKIE'])

    if 'view'        in cookies: set_view(        cookies['view']       .value)
    if 'state'       in cookies: set_state(       cookies['state']      .value)
    if 'mode'        in cookies: set_mode(        cookies['mode']       .value)
    if 'temperature' in cookies: set_temperature( cookies['temperature'].value)
    if 'fan_speed'   in cookies: set_fan_speed(   cookies['fan_speed']  .value)
    if 'full_effect' in cookies: set_full_effect( cookies['full_effect'].value)
    if 'ion'         in cookies: set_ion(         cookies['ion']        .value)
    if 'swing'       in cookies: set_swing(       cookies['swing']      .value)

def generate_cookies():
    cookies = SimpleCookie()

    cookies['view']        =        view_to_str(options.view)
    cookies['state']       =       state_to_str(remote_state.state)
    cookies['mode']        =        mode_to_str(remote_state.mode)
    cookies['temperature'] = temperature_to_str(remote_state.temperature)
    cookies['fan_speed']   =   fan_speed_to_str(remote_state.fan_speed)
    cookies['full_effect'] = full_effect_to_str(remote_state.full_effect)
    cookies['ion']         =         ion_to_str(remote_state.ion)
    cookies['swing']       =       swing_to_str(remote_state.swing)

    for (k, v) in cookies.iteritems():
        v['path'] = '/'

    return cookies

def cookies_to_headers(cookies):
    return list(('Set-Cookie:', v.OutputString()) for (k, v) in cookies.iteritems())


def application(env, start_response):
    read_cookies(env)

    path = env['PATH_INFO']

    global remote_state;

    # Debugging
    if path[:10] == '/bootstrap':
        with open ("myindex.html", "r") as myfile:
            data=myfile.read().replace('\n', '')
        return data

    # Debugging
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
        handle_state_request(path)

    if path.startswith('/remote/simple'):
        handle_simple_request(path)

    if path.startswith('/remote/advanced'):
        handle_advanced_request(path)

    return generate_page(start_response)

#   +-----------------------------------------------------------------------------+
#   |     ____        _   _ ____     _____                    _       _           |
#   |    |  _ \ _   _| \ | |  _ \   |_   _|__ _ __ ___  _ __ | | __ _| |_ ___     |
#   |    | |_) | | | |  \| | |_) |____| |/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \    |
#   |    |  __/| |_| | |\  |  __/_____| |  __/ | | | | | |_) | | (_| | ||  __/    |
#   |    |_|    \__, |_| \_|_|        |_|\___|_| |_| |_| .__/|_|\__,_|\__\___|    |
#   |           |___/                                  |_|                        |
#   +-----------------------------------------------------------------------------+
# available variables:
# +---------------+----------+--------------------------------------------+---------------------------------------------------------------------------------------+
# | variable      | type     | description                                | example                                                                               |
# |---------------+----------+--------------------------------------------+---------------------------------------------------------------------------------------|
# | hostname      | string   | name of the host                           | "localhost"                                                                           |
# | servicedesc   | string   | description of the service                 | "Interface 3"                                                                         |
# | check_command | string   | name of the check_command                  | "check_mk-uptime"                                                                     |
# | rrd_file      | dict     | rrd files accessible by ds                 | {"uptime": "/path/to/rrds/localhost/UPTIME_uptime.rrd"}                               |
# | font          | string   | value of pynp_font in config               | "Courier"                                                                             |
# | perf_data     | dict     | perf_data from livestatus accessible by ds | {'uptime': {'warn': None, 'crit': None, 'max': None, 'min': None, 'act': '12019013'}} |
# | perf_keys     | list     | keys from perf_data in correct order       | ['rta', 'pl','rtmax', 'rtmin']                                                        |
# | unit          | dict     | unit from livestatus accessible by ds      | {'rtmin': 'ms', 'rta': 'ms', 'rtmax': 'ms', 'pl': '%'}                                |
# | colors        | dict     | some general colors                        | {'green': '#00ff0080','green_line':'#00ff00','orange':'#ff990080',...}                |
# | rand_color    | function | generate random hex color                  | rand_color(steps=8, index=None) => #7ffff00                                           |
# +---------------+----------+--------------------------------------------+---------------------------------------------------------------------------------------+

ds_colors = [
    {'ds': 'SYN_SENT',    'color': 'a00000'},
    {'ds': 'SYN_RECV',    'color': 'ff4000'},
    {'ds': 'ESTABLISHED', 'color': '00f040'},
    {'ds': 'TIME_WAIT',   'color': '00b0b0'},
    {'ds': 'LAST_ACK',    'color': 'c060ff'},
    {'ds': 'CLOSE_WAIT',  'color': 'f000f0'},
    {'ds': 'CLOSED',      'color': 'ffc000'},
    {'ds': 'CLOSING',     'color': 'ffc080'},
    {'ds': 'FIN_WAIT1',   'color': 'cccccc'},
    {'ds': 'FIN_WAIT2',   'color': '888888'},
]

tcp_conn_stats = {
    'opt' : {
        'upper-limit': '10',
        'units-exponent': '0',
        'title': 'TCP Connection stats on %s' % hostname,
        'vertical-label': 'Number',
    },
    'def' : []
}

for element in ds_colors:
    if (ds_colors.index(element) + 1) % 4 == 0 or element == ds_colors[-1]:
        nl = '\\n'
    else:
        nl = ''
    tcp_conn_stats['def'].extend([
        'DEF:%s=%s:1:MAX' % (element['ds'], rrd_file[element['ds']]),
        'AREA:%s#%s:%s:STACK' % (element['ds'], element['color'], element['ds']),
        'GPRINT:%s:LAST:%s%%3.0lf%s' % (element['ds'], ' ' * (11-len(element['ds'])), nl)
    ])
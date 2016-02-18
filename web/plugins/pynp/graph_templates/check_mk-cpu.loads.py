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
# | rrd_file_index| dict     | rrd file index accessible by ds            | {"uptime": 1}                                                                         |
# | font          | string   | value of pynp_font in config               | "Courier"                                                                             |
# | perf_data     | dict     | perf_data from livestatus accessible by ds | {'uptime': {'warn': None, 'crit': None, 'max': None, 'min': None, 'act': '12019013'}} |
# | perf_keys     | list     | keys from perf_data in correct order       | ['rta', 'pl','rtmax', 'rtmin']                                                        |
# | unit          | dict     | unit from livestatus accessible by ds      | {'rtmin': 'ms', 'rta': 'ms', 'rtmax': 'ms', 'pl': '%'}                                |
# | colors        | dict     | some general colors                        | {'green': '#00ff0080','green_line':'#00ff00','orange':'#ff990080',...}                |
# | rand_color    | function | generate random hex color                  | rand_color(steps=8, index=None) => #7ffff00                                           |
# +---------------+----------+--------------------------------------------+---------------------------------------------------------------------------------------+

cpu_loads = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': '1',
        'title': 'CPU Load for %s' % hostname,
        'vertical-label': 'Load average'
    },
    'def': [
        'DEF:load1=%s:%i:MAX' % (rrd_file['load1'], rrd_file_index['load1']),
        'AREA:load1#60c0e0:Load average  1 min ',
        'GPRINT:load1:LAST:%6.2lf last ',
        'GPRINT:load1:AVERAGE:%6.2lf avg ',
        'GPRINT:load1:MAX:%6.2lf max\\n',

        'DEF:load15=%s:%i:MAX' % (rrd_file['load15'], rrd_file_index['load15']),
        'LINE:load15#004080:Load average 15 min ',
        'GPRINT:load15:LAST:%6.2lf last ',
        'GPRINT:load15:AVERAGE:%6.2lf avg ',
        'GPRINT:load15:MAX:%6.2lf max\\n',
    ]
}

if perf_data['load1']['warn']:
    cpu_loads['def'].extend([
        'HRULE:%s#FFFF00' % perf_data['load1']['warn'],
        'HRULE:%s#FF0000' % perf_data['load1']['crit'],
    ])

if perf_data['load1']['max']:
    cpu_loads['def'].extend([
        'COMMENT: Number of CPUs %s' % perf_data['load1']['max'],
    ])


if 'predict_load15' in rrd_file:
    cpu_loads['def'].extend([
        'DEF:predict=%s:%i:MAX' % (rrd_file['predict_load15'], rrd_file_index['predict_load15']),
        'LINE:predict#ff0000:Reference for prediction \\n',
    ])
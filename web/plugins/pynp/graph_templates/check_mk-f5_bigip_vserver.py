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
# Performance data from check:
# connections=0;;;;
# conn_rate=0;;;;

client_conns = {
    'opt' : {
        'lower-limit': '0',
        'title': "%s - Connections" % (servicedesc),
        'vertical-label': 'Client connections'
    },
    'def' : [
        'DEF:conns=%s:%i:MAX' % (rrd_file['connections'], rrd_file_index['connections']),
        'AREA:conns#4060a0:Current Client Connections',
        'LINE:conns#203060',
        'GPRINT:conns:LAST:%7.0lf %s LAST',
        'GPRINT:conns:MAX:%7.0lf %s MAX\\n',
    ]
}

connects_per_sec = {
    'opt' : {
        'lower-limit': '0',
        'title': "%s - Connects" % (servicedesc),
        'vertical-label': 'Connects/sec'
    },
    'def' : [
        'DEF:conns=%s:%i:MAX' % (rrd_file['conn_rate'], rrd_file_index['conn_rate']),
        'AREA:conns#80a0f0:Connects/sec',
        'LINE:conns#4060a0',
        'GPRINT:conns:LAST:%7.0lf %s LAST',
        'GPRINT:conns:MAX:%7.0lf %s MAX\\n',
    ]
}

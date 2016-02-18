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

omd_check_performance = {
    'opt' : {
        'height': '100',
        'title': "OMD site %s / Check performance" % servicedesc.split()[1],
        'vertical-label': "Checks per second",
    },
    'def' : [
        'DEF:host_checks=%s:%i:MAX' % (rrd_file['host_checks'], rrd_file_index['host_checks']),
        'DEF:service_checks=%s:%i:MAX' % (rrd_file['service_checks'], rrd_file_index['host_checks']),
        'AREA:host_checks#842:Host checks             ',
        'GPRINT:host_checks:AVERAGE:% 6.1lf/s avg',
        'GPRINT:host_checks:LAST:% 6.1lf/s last\\n',
        'AREA:service_checks#f84:Service checks          :STACK',
        'GPRINT:service_checks:AVERAGE:% 6.1lf/s avg',
        'GPRINT:service_checks:LAST:% 6.1lf/s last\\n',
    ]
}

omd_livestatus_performance = {
    'opt' : {
        'height': '100',
        'title': "OMD site %s / Livestatus performance" % servicedesc.split()[1],
        'vertical-label': "Events per second",
    },
    'def' : [
        'DEF:connects=%s:%i:MAX' % (rrd_file['connections'], rrd_file_index['connections']),
        'DEF:requests=%s:%i:MAX' % (rrd_file['requests'], rrd_file_index['requests']),
        'AREA:requests#abc:Livestatus Requests     ',
        'GPRINT:requests:AVERAGE:% 6.1lf/s avg',
        'GPRINT:requests:LAST:% 6.1lf/s last\\n',
        'AREA:connects#678:Livestatus Connects     ',
        'GPRINT:connects:AVERAGE:% 6.1lf/s avg',
        'GPRINT:connects:LAST:% 6.1lf/s last\\n',
    ]
}

omd_livestatus_connection_usage = {
    'opt' : {
        'height': '100',
        'title': "OMD site %s / Livestatus connection usage" % servicedesc.split()[1],
        'vertical-label': "Requests per Connect"
    },
    'def' : [
        'DEF:connects=%s:%i:MAX' % (rrd_file['connections'], rrd_file_index['connections']),
        'DEF:requests=%s:%i:MAX' % (rrd_file['requests'], rrd_file_index['requests']),
        'CDEF:rpcs=requests,connects,/',
        'AREA:rpcs#8a3:Requests per Connection',
        'GPRINT:rpcs:AVERAGE:% 6.1lf/s avg',
        'GPRINT:rpcs:LAST:% 6.1lf/s last\\n'
    ]
}


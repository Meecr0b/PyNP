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

cpu_utilization = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': '100',
        'title': 'CPU Utilization %s %s' % (hostname, servicedesc),
        'vertical-label': 'CPU utilization %'
    }, 
    'def': [
        'DEF:util=%s:%i:MAX' % (rrd_file['util'], rrd_file_index['util']),
        'CDEF:ok=util,%s,MIN'% perf_data['util']['warn'],
        'CDEF:warn=util,%s,MIN'% perf_data['util']['crit'],
        'AREA:util#c0f020',
        'AREA:warn#90f020',
        'AREA:ok#60f020:Utilization\:',
        'LINE:util#40a018',
        'GPRINT:util:LAST:%.0lf%%,',
        'GPRINT:util:MIN:min\: %.0lf%%,',
        'GPRINT:util:MAX:max\: %.0lf%%',
        'HRULE:%s#ffe000:Warning at %s%%' % (perf_data['util']['warn'], perf_data['util']['warn']),
        'HRULE:%s#ff0000:Critical at %s%%\\n' % (perf_data['util']['crit'], perf_data['util']['crit']),
    ]
}
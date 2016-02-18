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

title = 'Number of Processes / Threads'
vertical = 'count'
format = '%5.0lf'
upto = str(max(500, float(perf_data['threads']['warn']), float(perf_data['threads']['crit'])))
color = '8040f0'
line = '202060'

cpu_threads = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': upto,
        'units-exponent': '0',
        'units-length': '5',
        'title': title,
        'vertical-label': vertical,
    }, 
    'def': [
        'DEF:var1=%s:%i:MAX' % (rrd_file['threads'], rrd_file_index['threads']),
        'AREA:var1#%s:%s' % (color, title),
        'LINE1:var1#%s:' % line,
        'GPRINT:var1:LAST:Current\: %s' % format,
        'GPRINT:var1:MAX:Maximum\: %s  ' % format,
        'HRULE:%s#FFFF00:Warning at %s' % (perf_data['threads']['warn'], perf_data['threads']['warn']),
        'HRULE:%s#FF0000:Critical at %s' % (perf_data['threads']['crit'], perf_data['threads']['crit']),
    ]
}
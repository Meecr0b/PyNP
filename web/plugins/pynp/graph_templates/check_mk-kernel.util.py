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

if check_command == 'check_mk-decru_cpu':
    thirdname = 'IRQs'
    thirdds = 'interrupt'
else:
    thirdname = 'Wait'
    thirdds = 'wait'

cpu_utilization = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': '100',
        'title': 'CPU utilization for %s' % hostname,
        'vertical-label': 'CPU utilization %'
    },
    'def': [
        'DEF:user=%s:%i:AVERAGE' % (rrd_file['user'], rrd_file_index['user']),
        'DEF:system=%s:%i:AVERAGE' % (rrd_file['system'], rrd_file_index['system']),
        'DEF:wait=%s:%i:AVERAGE' % (rrd_file[thirdds], rrd_file_index[thirdds]),
        'CDEF:us=user,system,+',
        'CDEF:sum=us,wait,+',
        'CDEF:idle=100,sum,-',

        'COMMENT:Average\: ',
        'AREA:system#ff6000:System',
        'GPRINT:system:AVERAGE:%4.1lf%% ',
        'AREA:user#60f020:User:STACK',
        'GPRINT:user:AVERAGE:%4.1lf%%  ',
        'AREA:wait#00b0c0:%s:STACK' % thirdname,
        'GPRINT:wait:AVERAGE:%4.1lf%%  ',
        'LINE:sum#004080:Total',
        'GPRINT:sum:AVERAGE:%4.1lf%%  \\n',

        'COMMENT:Last\:    ',
        'AREA:system#ff6000:System',
        'GPRINT:system:LAST:%4.1lf%% ',
        'AREA:user#60f020:User:STACK',
        'GPRINT:user:LAST:%4.1lf%%  ',
        'AREA:wait#00b0c0:%s:STACK' % thirdname,
        'GPRINT:wait:LAST:%4.1lf%%  ',
        'LINE:sum#004080:Total',
        'GPRINT:sum:LAST:%4.1lf%%  \\n',
    ]
}
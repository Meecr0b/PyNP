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

check_mk_execution_time = {
    'opt' : {
        'height': '100',
        'title': "%s: Check_MK check execution time" % hostname,
        'vertical-label': "time (s)"
    },
    'def' : [
        'DEF:extime=%s:1:MAX' % rrd_file['execution_time'],
        'AREA:extime#d080af:execution time ',
        'LINE1:extime#d020a0:',
        'GPRINT:extime:LAST:last\: %8.2lf s',
        'GPRINT:extime:MAX:max\: %8.2lf s ',
        'GPRINT:extime:AVERAGE:avg\: %8.2lf s\\n'
    ]
}

check_mk_process_time = {
    'opt' : {
        'height': '100',
        'title': "%s: Check_MK process times" % hostname,
        'vertical-label': "time (s)"},
    'def' : [
        'DEF:user_time=%s:%i:MAX' % (rrd_file['user_time'], rrd_file_info['user_time']),
        'LINE1:user_time#d020a0:user time',
        'GPRINT:user_time:LAST:          last\: %8.2lf s',
        'GPRINT:user_time:MAX:max\: %8.2lf s ',
        'GPRINT:user_time:AVERAGE:avg\: %8.2lf s\\n',

        'DEF:system_time=%s:%i:MAX' % (rrd_file['system_time'], rrd_file_info['system_time']),
        'LINE1:system_time#d08400:system time',
        'GPRINT:system_time:LAST:        last\: %8.2lf s',
        'GPRINT:system_time:MAX:max\: %8.2lf s ',
        'GPRINT:system_time:AVERAGE:avg\: %8.2lf s\\n',

        'DEF:children_user_time=%s:%i:MAX' % (rrd_file['children_user_time'], rrd_file_info['children_user_time']),
        'LINE1:children_user_time#308400:childr. user time',
        'GPRINT:children_user_time:LAST:  last\: %8.2lf s',
        'GPRINT:children_user_time:MAX:max\: %8.2lf s ',
        'GPRINT:children_user_time:AVERAGE:avg\: %8.2lf s\\n',

        'DEF:children_system_time=%s:%i:MAX' % (rrd_file['children_system_time'], rrd_file_info['children_system_time']),
        'LINE1:children_system_time#303400:childr. system time',
        'GPRINT:children_system_time:LAST:last\: %8.2lf s',
        'GPRINT:children_system_time:MAX:max\: %8.2lf s ',
        'GPRINT:children_system_time:AVERAGE:avg\: %8.2lf s\\n'
    ]
}
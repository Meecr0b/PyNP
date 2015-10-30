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
# Performance data from check:
# temp=33;60;80;;

temperature = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': '40',
        'title': 'Temperature %s' % (servicedesc),
        'vertical-label': 'Celsius'
    },
    'def': [
            
        'DEF:var1=%s:1:MAX' % rrd_file['temp'],
        'AREA:var1#2080ff:Temperature\:',
        'GPRINT:var1:LAST:%2.0lfC',
        'LINE1:var1#000080:',
        'GPRINT:var1:MAX:(Max\: %2.0lfC,',
        'GPRINT:var1:AVERAGE:Avg\: %2.0lfC)',
    ]
}

if (perf_data['temp']['warn']):
    temperature['def'].extend([
        'HRULE:%s#FFFF00:Warning\: %sC' % (perf_data['temp']['warn'], perf_data['temp']['warn']),
        'HRULE:%s#FF0000:Critical\: %sC' % (perf_data['temp']['crit'], perf_data['temp']['crit']),
    ])

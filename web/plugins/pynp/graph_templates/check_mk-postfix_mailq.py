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

mail_queue_length = {
    'opt' : {
        'lower-limit': '0',
        'title': 'Mail Queue Length',
        'vertical-label': 'Mails',
    },
    'def' : [
        'DEF:length=%s:%i:MAX' % (rrd_file['length'], rrd_file_info['length']),
        'HRULE:%s#FFFF00' % perf_data['length']['warn'],
        'HRULE:%s#FF0000' % perf_data['length']['crit'],
        'AREA:length#6890a0:Mails',
        'LINE:length#2060a0',
        'GPRINT:length:LAST:%6.2lf last',
        'GPRINT:length:AVERAGE:%6.2lf avg',
        'GPRINT:length:MAX:%6.2lf max\\n',
    ]
}

mail_queue_size = {
    'opt' : {
        'vertical-label': 'MBytes',
        'base': '1024',
        #'units-exponent': '6',
        'lower-limit': '0',
        'title': 'Mail Queue Size',
    },
    'def' : [
        'DEF:size=%s:%i:MAX' % (rrd_file['size'], rrd_file_info['size']),
        'CDEF:queue_mb=size,1048576,/',
        'AREA:queue_mb#65ab0e:Megabytes',
        'LINE:queue_mb#206a0e',
        'GPRINT:queue_mb:MAX:%6.2lf MB max\\n',
    ]
}
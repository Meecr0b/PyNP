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
# | colors        | dict     | some general colors                        | {'green': '#00ff0080','green_line':'#00ff00','oragen':'#ff990080',...}                |
# | rand_color    | function | generate random hex color                  | rand_color(steps=8, index=None) => #7ffff00                                           |
# +---------------+----------+--------------------------------------------+---------------------------------------------------------------------------------------+
# Performance data from check:
# bytes_in=697.77377;;;;
# bytes_out=0;;;;

bigip_interface = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': '1',
        'title': "Traffic Utilization %s / %s" % (hostname, servicedesc),
        'vertical-label': 'bytes per second'
    },
    'def' : [
        'DEF:in=%s:1:MAX' % rrd_file['bytes_in'],
        'DEF:out=%s:1:MAX' % rrd_file['bytes_out'],
        'CDEF:kb_out=out,1024,/',
        'CDEF:kb_in=in,1024,/',
        'AREA:in#18DF18:Inbound',
        'GPRINT:kb_in:LAST:%6.2lfk last',
        'GPRINT:kb_in:AVERAGE:%6.2lfk avg',
        'GPRINT:kb_in:MAX:%6.2lfk max\\n',
        'LINE:out#004080:Outbound',
        'GPRINT:kb_out:LAST:%6.2lfk last',
        'GPRINT:kb_out:AVERAGE:%6.2lfk avg',
        'GPRINT:kb_out:MAX:%6.2lfk max\\n',
    ]
}

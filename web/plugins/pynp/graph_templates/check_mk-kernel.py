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

subtype = servicedesc[7:]
if subtype in ['pgmajfault', 'Major Page Faults']:
    title = 'Major Page Faults'
    vertical = 'faults / sec'
    format = '%5.1lf/s'
    upto = '500'
    color = '20ff80'
    line = '10a040'
elif subtype in ['ctxt', 'Context Switches']:
    title = 'Context Switches'
    vertical = 'switches / sec'
    format = '%5.1lf/s'
    upto = '50000'
    color = '80ff20'
    line = '40a010'
elif subtype in ['processes', 'Process Creations']:
    title = 'Process creation'
    vertical = 'new processes / sec'
    format = '%5.1lf/s'
    upto = '100'
    color = 'ff8020'
    line = 'a04010'
else:
    title = 'Kernel counter %s' % subtype
    vertical = 'per sec'
    format = '%3.0lf'
    upto = '100'
    color = 'ffff20'
    line = '90a010'

kernel = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': upto,
        'units-exponent': '0',
        'title': '%s: %s' % (hostname, title),
        'vertical-label': vertical,
    }, 
    'def': [
        'DEF:var1=%s:1:MAX' % rrd_file.values()[0],
        'AREA:var1#%s:%s\:' % (color, title),
        'LINE1:var1#%s:' % line,
        'GPRINT:var1:LAST:Current\: %s' % format,
        'GPRINT:var1:MAX:Maximum\: %s' % format,
    ]
}

if perf_data.values()[0]['warn']:
    kernel['def'].extend([
        'GPRINT:var1:AVERAGE:Average\: %s\\n' % format,
        'HRULE:%s#FFFF00:Warning\: %s/s' % (perf_data.values()[0]['warn'], perf_data.values()[0]['warn']),
        'HRULE:%s#FF0000:Critical\: %s/s'% (perf_data.values()[0]['crit'], perf_data.values()[0]['crit']),
    ])
else:
    kernel['def'].extend([
        'GPRINT:var1:AVERAGE:Average\: %s' % format,
    ])

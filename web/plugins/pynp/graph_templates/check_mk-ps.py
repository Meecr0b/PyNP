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
# count=1;100000;100000;0; 
# vsz=51224;;;; 
# rss=3996;;;; 
# pcpu=0;;;;

# 1. Graph: Number of processes
number_of_processes = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': max(20, perf_data['count']['crit']),
        'units-exponent': '0',
        'units-length': '5',
        'title': 'Number of Processes',
        'vertical-label': 'count'
    }, 
    'def': [
        'DEF:count=%s:%i:MAX' % (rrd_file['count'], rrd_file_info['count']),
        'AREA:count#8040f0:Processes     ',
        'LINE1:count#202060:',
        'GPRINT:count:LAST:Current\: %3.0lf',
        'GPRINT:count:MAX:Maximum\: %3.0lf',
        'HRULE:%s#FFFF00:Warning at %s' % (perf_data['count']['warn'], perf_data['count']['warn']),
        'HRULE:%s#FF0000:Critical at %s' % (perf_data['count']['crit'], perf_data['count']['crit']),
    ]
}

# 2. Graph: Memory usage
if 'vsz' in perf_data:
    memory_usage = {
        'opt' : {
            'lower-limit': '0',
            'title': 'Memory Usage per process',
            'vertical-label': 'MB'
        }, 
        'def': [
            'DEF:count=%s:%i:MAX' % (rrd_file['count'], rrd_file_info['count']),
            'DEF:vsz=%s:%i:MAX' % (rrd_file['vsz'], rrd_file_info['vsz']),
            'DEF:rss=%s:%i:MAX' % (rrd_file['rss'], rrd_file_info['rss']),
            'CDEF:vszmb=vsz,1024,/,count,/',
            'CDEF:rssmb=rss,1024,/,count,/',
            'AREA:vszmb#90a0f0:Virtual size ',
            'GPRINT:vszmb:LAST:Current\: %5.1lf MB',
            'GPRINT:vszmb:MIN:Min\: %5.1lf MB',
            'GPRINT:vszmb:MAX:Max\: %5.1lf MB\\n',
            'AREA:rssmb#2070ff:Resident size',
            'GPRINT:rssmb:LAST:Current\: %5.1lf MB',
            'GPRINT:rssmb:MIN:Min\: %5.1lf MB',
            'GPRINT:rssmb:MAX:Max\: %5.1lf MB\\n',
        ]
    }

# 3. CPU usage
if 'pcpu' in perf_data:
    cpu_usage = {
        'opt' : {
            'lower-limit': '0',
            'upper-limit': '100',
            'title': 'CPU Usage',
            'vertical-label': 'CPU(%)'
        }, 
        'def': [
            'DEF:pcpu=%s:%i:MAX' % (rrd_file['pcpu'], rrd_file_info['pcpu']),
            'AREA:pcpu#30ff80:CPU usage (%) ',
            'LINE:pcpu#20a060:',
            'GPRINT:pcpu:LAST:Current\: %4.1lf%%',
            'GPRINT:pcpu:MIN:Min\: %4.1lf%%',
            'GPRINT:pcpu:MAX:Max\: %4.1lf%%\\n',
        ]
    }
    
    if perf_data['pcpu']['warn']:
        cpu_usage['def'].extend([
            'HRULE:%s#ffff00:Warning at %s%%' % (perf_data['pcpu']['warn'], perf_data['pcpu']['warn']),
        ])
    if perf_data['pcpu']['crit']:
        cpu_usage['def'].extend([
            'HRULE:%s#ff0000:Critical at %s%%' % (perf_data['pcpu']['crit'], perf_data['pcpu']['crit']),
        ])
    if 'pcpuavg' in perf_data:
        cpu_usage['def'].extend([
            'DEF:pcpuavg=%s:1:MAX' % rrd_file['pcpuavg'],
            'LINE:pcpuavg#000000:Average over %s minutes\\n' % perf_data['pcpuavg']['max'],
        ])

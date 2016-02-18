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

used_mem = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': '%f' % (float(perf_data['ramused']['max']) * 120 / 100),
        'title': 'Memory usage %s' % hostname,
        'vertical-label': 'MEMORY(MB)'
    },
    'def': []
}

if 'pagetables' in rrd_file:
    used_mem['def'].extend([
        'DEF:pagetables=%s:1:MAX' % rrd_file['pagetables'],
    ])

used_mem['def'].extend([
    'DEF:ram=%s:%i:MAX' % (rrd_file['ramused'], rrd_file_index['ramused']),
    'DEF:virt=%s:%i:MAX' % (rrd_file['memused'], rrd_file_index['memused']),
    'DEF:swap=%s:%i:MAX' % (rrd_file['swapused'], rrd_file_index['swapused']),

    'HRULE:%s#000080:RAM+SWAP installed' % perf_data['memused']['max'],
    'HRULE:%s#2040d0:%.1f GB RAM installed' % (perf_data['ramused']['max'], float(perf_data['ramused']['max']) / 1024),
    'HRULE:%s#FFFF00:Warning' % perf_data['memused']['warn'],
    'HRULE:%s#FF0000:Critical' % perf_data['memused']['crit'],

    'COMMENT: \\n',
    'AREA:ram#80ff40:RAM used        ',
    'GPRINT:ram:LAST:%6.0lf MB last',
    'GPRINT:ram:AVERAGE:%6.0lf MB avg',
    'GPRINT:ram:MAX:%6.0lf MB max\\n',

    'AREA:swap#008030:SWAP used       :STACK',
    'GPRINT:swap:LAST:%6.0lf MB last',
    'GPRINT:swap:AVERAGE:%6.0lf MB avg',
    'GPRINT:swap:MAX:%6.0lf MB max\\n',
    
])

if 'pagetables' in rrd_file:
    used_mem['def'].extend([
        'AREA:pagetables#ff8800:Page tables     :STACK',
        'GPRINT:pagetables:LAST:%6.0lf MB last',
        'GPRINT:pagetables:AVERAGE:%6.0lf MB avg',
        'GPRINT:pagetables:MAX:%6.0lf MB max\\n',
        'LINE:virt#000000:RAM+SWAP+PT used',
        'GPRINT:virt:LAST:%6.0lf MB last',
        'GPRINT:virt:AVERAGE:%6.0lf MB avg',
        'GPRINT:virt:MAX:%6.0lf MB max\\n',
    ])
else:
    used_mem['def'].extend([
        'LINE:virt#000000:RAM+SWAP used   ',
        'GPRINT:virt:LAST:%6.0lf MB last',
        'GPRINT:virt:AVERAGE:%6.0lf MB avg',
        'GPRINT:virt:MAX:%6.0lf MB max\\n',
    ])

if 'mapped' in rrd_file:
    used_mem['def'].extend([
        'DEF:mapped=%s:%i:MAX' % (rrd_file['mapped'], rrd_file_index['mapped']),
        'LINE2:mapped#8822ff:Memory mapped   ',
        'GPRINT:mapped:LAST:%6.0lf MB last',
        'GPRINT:mapped:AVERAGE:%6.0lf MB avg',
        'GPRINT:mapped:MAX:%6.0lf MB max\\n',
    ])

if 'committed_as' in rrd_file:
    used_mem['def'].extend([
        'DEF:committed=%s:%i:MAX' % (rrd_file['committed_as'], rrd_file_index['committed_as']),
        'LINE2:committed#cc00dd:Committed       ',
        'GPRINT:committed:LAST:%6.0lf MB last',
        'GPRINT:committed:AVERAGE:%6.0lf MB avg',
        'GPRINT:committed:MAX:%6.0lf MB max\\n',
    ])

# Shared memory is part of RAM. So simply overlay it
if 'shared' in rrd_file:
    used_mem['def'].extend([
        'DEF:shared=%s:%i:MAX' % (rrd_file['shared'], rrd_file_index['shared']),
        'AREA:shared#44ccff:Shared Memory   ',
        'GPRINT:shared:LAST:%6.0lf MB last',
        'GPRINT:shared:AVERAGE:%6.0lf MB avg',
        'GPRINT:shared:MAX:%6.0lf MB max\\n',
    ])
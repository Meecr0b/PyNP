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

def cleanup_ds(s):
    bad_chars = ['[', ']', '#', '.', '/']
    for c in bad_chars:
        s = s.replace(c,'')
    return s

templates = []
for index, ds in enumerate(perf_keys):
    vname = cleanup_ds(ds)
    templates.append({
        'opt' : {},
        'def' : [
            'DEF:%s=%s:1:AVERAGE' % (vname, rrd_file[ds]),
            'AREA:%s%s:%s' % (vname, rand_color(index=index), ds),
            'GPRINT:%s:LAST:Last\: %%6.2lf %s' % (vname, unit[ds]),
            'GPRINT:%s:MAX:Max\: %%6.2lf %s' % (vname, unit[ds]),
            'GPRINT:%s:AVERAGE:Average\: %%6.2lf %s\\n' % (vname, unit[ds]),
            'LINE1:%s%s' % (vname, colors['black']),
            'HRULE:0%s' % (colors['black']),
        ]

    })

    if unit[ds]:
        templates[index]['opt']['vertical-label'] = unit[ds]

    if perf_data[ds]['warn']:
        for level in perf_data[ds]['warn'].split(':'):
            templates[index]['def'].append(
                'HRULE:%s#ffff00:Warning  %s\\n' % (level, level),
            )

    if perf_data[ds]['crit']:
        for level in perf_data[ds]['crit'].split(':'):
            templates[index]['def'].append(
                'HRULE:%s#ff0000:Critical %s\\n' % (level, level),
            )


templates[0]['opt']['title'] = '%s / %s' % (hostname, servicedesc.replace(':', '\:'))

templates[-1]['def'].extend([
    'COMMENT:Default Template\\r',
    'COMMENT:Command %s\\r' % str(check_command),
])

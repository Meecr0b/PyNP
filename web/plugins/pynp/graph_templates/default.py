#   +-----------------------------------------------------------------------------+
#   |     ____        _   _ ____     _____                    _       _           |
#   |    |  _ \ _   _| \ | |  _ \   |_   _|__ _ __ ___  _ __ | | __ _| |_ ___     |
#   |    | |_) | | | |  \| | |_) |____| |/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \    |
#   |    |  __/| |_| | |\  |  __/_____| |  __/ | | | | | |_) | | (_| | ||  __/    |
#   |    |_|    \__, |_| \_|_|        |_|\___|_| |_| |_| .__/|_|\__,_|\__\___|    |
#   |           |___/                                  |_|                        |
#   +-----------------------------------------------------------------------------+
# available variables:
# +------------------+----------+----------------------------------------------+-------------------------------------------------------------------------------------------+
# | variable         | type     | description                                  | example                                                                                   |
# |------------------+----------+----------------------------------------------+-------------------------------------------------------------------------------------------|
# | hostname         | string   | name of the host                             | "localhost"                                                                               |
# | servicedesc      | string   | description of the service                   | "Interface 3"                                                                             |
# | check_command    | string   | name of the check_command                    | "check_mk-uptime"                                                                         |
# | rrd_file         | dict     | rrd files accessible by ds                   | {"uptime": "/path/to/rrds/localhost/UPTIME_uptime.rrd"}                                   |
# | font             | string   | value of pynp_font in config                 | "Courier"                                                                                 |
# | perf_data        | dict     | perf_data from livestatus accessible by ds   | {'uptime' : {"act": "38875011.78", "warn": None, "crit": None, "min": None, "max": None}} |
# | unit             | dict     | unit from livestatus accessible by ds        | {'rta':'ms','pl':'%','rtmax':'ms', 'rtmin':'ms'}                                          |
# | colors           | dict     | some general colors                          | {'green': '#00ff0080','green_line':'#00ff00','oragen':'#ff990080',...}                    |
# | rand_color       | function | generate random hex color                    | rand_color(steps=8, index=None) => #7ffff00                                               |
# +------------------+----------+----------------------------------------------+-------------------------------------------------------------------------------------------+

templates = []
for index, ds in enumerate(rrd_file):
    templates.append({
        'opt' : {},
        'def' : [
            'DEF:a=%s:1:AVERAGE' % rrd_file[ds],
            'AREA:a%s:%s' % (rand_color(index=index), ds),
            'GPRINT:a:LAST:Last\: %%6.2lf %s' % unit[ds],
            'GPRINT:a:MAX:Max\: %%6.2lf %s' % unit[ds],
            'GPRINT:a:AVERAGE:Average\: %%6.2lf %s\\n' % unit[ds],
            'LINE1:a%s' % colors['black'],
            'HRULE:0%s' % colors['black'],
        ]
    })

    if unit[ds]:
        templates[index]['opt']['vertical-label'] = unit[ds]

    if perf_data[ds]['warn']:
        templates[index]['def'].extend([
            'HRULE:%s#ffff00:Warning  %s\\n' % (perf_data[ds]['warn'],perf_data[ds]['warn']),
            'HRULE:%s#ff0000:Critical %s\\n' % (perf_data[ds]['crit'],perf_data[ds]['crit']),
        ])

templates[0]['opt']['title'] = '%s / %s' % (hostname, servicedesc.replace(':', '\:'))

templates[-1]['def'].extend([
    'COMMENT:Default Template\\r',
    'COMMENT:Command %s\\r' % str(check_command),
])
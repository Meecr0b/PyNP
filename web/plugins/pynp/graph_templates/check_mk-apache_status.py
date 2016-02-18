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

apache_status = {
    'opt' : {
        'lower-limit': '0',
        'title': "%s: %s" % (hostname, servicedesc),
        'vertical-label': "Connections"
    },
    'def' : [
        'DEF:varTotal=%s:%i:AVERAGE' % (rrd_file["TotalSlots"], rrd_file_index['TotalSlots']),
        'DEF:varOpen=%s:%i:AVERAGE' % (rrd_file["OpenSlots"], rrd_file_index['OpenSlots']),
    ]
}

if perf_data['TotalSlots']['act']:
    apache_status['def'].extend([
        'HRULE:%s#000000:Total Slots\: %s\\n' % (perf_data['TotalSlots']['act'], perf_data['TotalSlots']['act']),
        'COMMENT: \\n',
    ])

for index, key in enumerate(perf_keys):
    if key.startswith('State'):
        apache_status['def'].extend([
            'DEF:var%s=%s:%i:AVERAGE' % (key, rrd_file[key], rrd_file_index[key]),
            'AREA:var%s%s:%s :STACK' % (key, rand_color(index=index), key[6:].ljust(16)) ,
            'GPRINT:var%s:LAST:Last %%5.1lf' % key,
            'GPRINT:var%s:MAX:Max %%5.1lf' % key,
            'GPRINT:var%s:AVERAGE:Average %%5.1lf' % key,
            'COMMENT: \\n',
        ])

# get UsedSlots
apache_status['def'].extend([
    'CDEF:usedslots=varTotal,varOpen,-',
    'LINE:usedslots#ffffff:UsedSlots        ',
    'GPRINT:usedslots:LAST:Last %5.1lf',
    'GPRINT:usedslots:MAX:Max %5.1lf',
    'GPRINT:usedslots:AVERAGE:Average %5.1lf\\n',
    'COMMENT: \\n',
])

if "ReqPerSec" in rrd_file:
    requests_per_second = {
        'opt' : {
            'lower-limit': '0',
            'title': "%s: %s Requests/sec" % (hostname, servicedesc),
            'vertical-label': "Requests/sec"
        },
        'def' : [
            'DEF:varReqPerSec=%s:%i:AVERAGE' % (rrd_file["ReqPerSec"], rrd_file_index['ReqPerSec']),
            'LINE1:varReqPerSec#000000:ReqPerSec       :STACK',
            'GPRINT:varReqPerSec:LAST:Last %6.1lf',
            'GPRINT:varReqPerSec:MAX:Max %6.1lf',
            'GPRINT:varReqPerSec:AVERAGE:Average %6.1lf',
        ]
    }

if "BytesPerSec" in rrd_file:
    bytes_per_second = {
        'opt' : {
            'lower-limit': '0',
            'title': "%s: %s Bytes/sec" % (hostname, servicedesc),
            'vertical-label': "Bytes/sec"
        },
        'def' : [
            'DEF:varBytesPerSec=%s:%i:AVERAGE' % (rrd_file['BytesPerSec'], rrd_file_index['BytesPerSec']),
            'LINE1:varBytesPerSec%s:BytesPerSec     :STACK' % rand_color(index=perf_keys.index("BytesPerSec")),
            'GPRINT:varBytesPerSec:LAST:Last %6.1lf',
            'GPRINT:varBytesPerSec:MAX:Max %6.1lf',
            'GPRINT:varBytesPerSec:AVERAGE:Average %6.1lf',
        ]
    }

all_other_graphs = []

for index, key in enumerate(perf_keys):
    if not key.startswith(('State_','ReqPerSec','BytesPerSec','Uptime')):
        all_other_graphs.append({
            'opt' : {
                'lower-limit': '0',
                'title': "%s: Apache - %s" % (hostname, key),
            },
            'def' : [
                'DEF:var%s=%s:%i:AVERAGE' % (key, rrd_file[key], rrd_file_index[key]),
                'LINE1:var%s%s:%s:STACK' % (key, rand_color(index=index), key.ljust(16)),
                'GPRINT:var%s:LAST:Last %%6.1lf' % key,
                'GPRINT:var%s:MAX:Max %%6.1lf' % key,
                'GPRINT:var%s:AVERAGE:Average %%6.1lf' % key,
            ]
        })

if 'Uptime' in rrd_file:
    uptime_graph = {
        'opt' : {
            'lower-limit': '0',
            'title': "Uptime (time since last reboot)",
            'vertical-label': "Uptime (d)"
        },
        'def' : [
            'DEF:sec=%s:%i:MAX' % (rrd_file['Uptime'], rrd_file_index['Uptime']),
            'CDEF:uptime=sec,86400,/',
            'AREA:uptime#80f000:Uptime (days)',
            'LINE:uptime#408000',
            'GPRINT:uptime:LAST:%7.2lf %s LAST',
            'GPRINT:uptime:MAX:%7.2lf %s MAX',
        ]
    }

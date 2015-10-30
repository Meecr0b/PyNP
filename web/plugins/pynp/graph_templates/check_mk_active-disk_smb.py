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

fs_name = servicedesc[3:]

mega = 1024.0 * 1024
giga = mega * 1024
maxgb = float(perf_data[fs_name]['max']) / 1024
warngb = float(perf_data[fs_name]['warn']) / 1024
critgb = float(perf_data[fs_name]['crit']) / 1024

active_disk = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': maxgb,
        'base': '1024',
        'title': '%s: Filesystem %s (%.1f GB)' % (hostname, fs_name, maxgb),
        'vertical-label': 'GB'
    }, 
    'def': [
        'DEF:used_bytes=%s:1:MAX' % rrd_file[fs_name],
        'CDEF:var1=used_bytes,%s,/' % giga,
        'AREA:var1#00ffc6:used space on %s\\n' % fs_name,
        'LINE1:var1#226600:',
        'HRULE:%s#003300:Size (%.1f GB) ' % (maxgb, maxgb),
        'HRULE:%s#ffff00:Warning at %.1f GB ' % (warngb, warngb),
        'HRULE:%s#ff0000:Critical at %.1f GB \\n' % (critgb, critgb),
        'GPRINT:var1:LAST:current\: %6.2lf GB',
        'GPRINT:var1:MAX:max\: %6.2lf GB ',
        'GPRINT:var1:AVERAGE:avg\: %6.2lf GB',
    ]
}
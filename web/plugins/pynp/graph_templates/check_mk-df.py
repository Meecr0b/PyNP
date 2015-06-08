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
fs_name = ''

#fs_name is ds that is part of servicedesc
for ds in rrd_file.keys():
    if ds in servicedesc:
        fs_name = ds
        break

maxgb = float(perf_data[fs_name]['max']) / 1024
warngb = float(perf_data[fs_name]['warn']) / 1024
critgb = float(perf_data[fs_name]['crit']) / 1024

filesystem_usage = {
    'opt' : {
        'lower-limit': '0',
        'upper-limit': maxgb,
        'title': '%s: Filesystem %s (%.1f GB)' % (hostname, fs_name, maxgb),
        'vertical-label': 'GB'
    },
    'def': [
        'DEF:mb=%s:1:MAX' % rrd_file[fs_name],
        'CDEF:var1=mb,1024,/',
        'AREA:var1#00ffc6:used space on %s\\n' % servicedesc.replace(':', '\:'),
    ]
}

if 'uncommited' in rrd_file:
    filesystem_usage['def'].extend([
        'DEF:uncommitted_mb=%s:1:MAX' % rrd_file['uncommitted'],
        'CDEF:uncommitted_gb=uncommitted_mb,1024,/', 
        'CDEF:total_gb=uncommitted_gb,var1,+',
    ])
else:
    filesystem_usage['def'].extend([
        'CDEF:total_gb=var1',
    ])

filesystem_usage['def'].extend([
    'HRULE:%s#003300:Size (%.1f GB) ' % (maxgb, maxgb),
    'HRULE:%s#ffff00:Warning at %.1f GB ' % (warngb, warngb),
    'HRULE:%s#ff0000:Critical at %.1f GB \\n' % (critgb, critgb),
    'GPRINT:var1:LAST:current\: %6.2lf GB',
    'GPRINT:var1:MAX:max\: %6.2lf GB ',
    'GPRINT:var1:AVERAGE:avg\: %6.2lf GB\\n',
])

if 'uncommited' in rrd_file:
    filesystem_usage['def'].extend([
        'AREA:uncommitted_gb#eeccff:Uncommited:STACK',
        'GPRINT:uncommitted_gb:MAX:%6.2lf GB\l',
    ])

filesystem_usage['def'].extend([
    'LINE1:total_gb#226600',
])

# Second graph is optional and shows trend. The MAX field
# of the third variable contains (size of the filesystem in MB
# / range in hours). From that we can compute the configured range.
if 'growth' in rrd_file:
    size_mb_per_hours = float(perf_data['trend']['max'])
    size_mb = float(perf_data[fs_name]['max'])
    hours = 1.0 / (size_mb_per_hours / size_mb)
    range = '%.0fh' % hours
    
    #Current growth / shrinking. This value is give as MB / 24 hours.
    #Note: This has changed in 1.1.13i3. Prior it was MB / trend_range!
    
    growth = {
        'opt' : {
            'lower-limit': '-1',
            'upper-limit': '1',
            'units-exponent': '0',
            'title': '%s: Growth of %s' % (hostname, fs_name),
            'vertical-label': '+/- MB / 24h'
        },
        'def': [
            'DEF:growth_max=%s:1:MAX' % rrd_file['growth'],
            'DEF:growth_min=%s:1:MIN'% rrd_file['growth'],
            #'DEF:trend=%s:1:AVERAGE' % rrd_file['trend'],
            'CDEF:growth_pos=growth_max,0,MAX',
            'CDEF:growth_neg=growth_min,0,MIN',
            'CDEF:growth_minabs=0,growth_min,-',
            'CDEF:growth=growth_minabs,growth_max,MAX',
            'HRULE:0#c0c0c0',
            'AREA:growth_pos#3060f0:Grow ',
            'AREA:growth_neg#30f060:Shrink ',
            'GPRINT:growth:LAST:Current\: %+9.2lfMB / 24h',
            'GPRINT:growth:MAX:Max\: %+9.2lfMB / 24h\\n',
        ]
    }
    
    trend = {
        'opt' : {
            'lower-limit': '-1',
            'upper-limit': '1',
            'units-exponent': '0',
            'title': '%s: Growth of %s' % (hostname, fs_name),
            'vertical-label': '+/- MB / 24h'
        },
        'def': [
            'DEF:trend=%s:1:AVERAGE' % rrd_file['trend'],
            'HRULE:0#c0c0c0',
            'LINE1:trend#000000:Trend\:',
            'GPRINT:trend:LAST:%+7.2lf MB/24h',
        ]
    }
    
    if perf_data['trend']['warn']:
        trend['def'].extend([
            'LINE1:%s#ffff00:Warn\: %.2fMB / %.0fh' % (perf_data['trend']['warn'] * hours / 24.0, hours),
        ])
    
    if perf_data['trend']['crit']:
        trend['def'].extend([
            'LINE1:%s#ff0000:Crit\: %.2fMB / %.0fh' % (perf_data['trend']['crit'] * hours / 24.0, hours),
        ])
    
    trend['def'].extend([
        'COMMENT: \n',
    ])

if 'trend_hoursleft' in rrd_file:
    trend_hoursleft = {
        'opt' : {
            'lower-limit': '-1',
            'upper-limit': '365',
            'units-exponent': '0',
            'title': '%s: Days left for %s' % (hostname, fs_name),
            'vertical-label': 'Days left'
        },
        'def' : [
            'DEF:hours_left=%s:1:AVERAGE' % rrd_file['trend_hoursleft'],
            'DEF:hours_left_min=%s:1:MIN' % rrd_file['trend_hoursleft'],
            # negative hours indicate no growth
            # the dataset hours_left_isneg stores this info for each point as True/False
            'CDEF:hours_left_isneg=hours_left_min,-1,EQ',
            'CDEF:hours_left_unmon=hours_left_min,400,0,IF',
            'CDEF:days_left=hours_left,24,/',
            'CDEF:days_left_cap=days_left,400,MIN',
            # Convert negative points to 400 (y-axis cap)
            'CDEF:days_left_cap_positive=hours_left_isneg,400,days_left_cap,IF',
            # The AREA has a rendering problem. Points are too far to the right
            'AREA:hours_left_unmon#AA2200:',
            'AREA:days_left_cap_positive#22AA44:Days left\:',
        ]
    }
    
    if perf_data['trend_hoursleft']['act'] == '-1':
        trend_hoursleft['def'].extend([
            'COMMENT:Not growing',
        ])
    else:
        trend_hoursleft['def'].extend([
            'GPRINT:days_left:LAST:%7.2lf days',
        ])

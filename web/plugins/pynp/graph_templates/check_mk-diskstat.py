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

if len(perf_data) >= 2:
    disk = servicedesc.split()[-1]
    
    diskstat = {
        'opt' : {
            'units-exponent' : '0',
            'title': 'Disk throughput %s / %s' % (hostname, disk),
            'vertical-label': 'Throughput (MB/s) %'
        },
        'def': [
            'HRULE:0#a0a0a0',
    # read
            'DEF:read=%s:1:MAX' % rrd_file['read'],
            'CDEF:read_mb=read,1048576,/',
            'AREA:read_mb#40c080:Read ',
            'GPRINT:read_mb:LAST:%8.1lf MB/s last',
            'GPRINT:read_mb:AVERAGE:%6.1lf MB/s avg',
            'GPRINT:read_mb:MAX:%6.1lf MB/s max\\n',
        ]
    }
    
    # read average as line in the same graph
    if 'read.avg' in rrd_file:
        diskstat['def'].extend([
            'DEF:read_avg=%s:1:MAX' % rrd_file['read.avg'],
            'CDEF:read_avg_mb=read_avg,1048576,/',
            'LINE:read_avg_mb#202020',
        ])
    
    # write
    diskstat['def'].extend([
        'DEF:write=%s:1:MAX' % rrd_file['write'],
        'CDEF:write_mb=write,1048576,/',
        'CDEF:write_mb_neg=write_mb,-1,*',
        'AREA:write_mb_neg#4080c0:Write  ',
        'GPRINT:write_mb:LAST:%6.1lf MB/s last',
        'GPRINT:write_mb:AVERAGE:%6.1lf MB/s avg',
        'GPRINT:write_mb:MAX:%6.1lf MB/s max\\n',
    ])
    
    # show levels for read
    if perf_data['read']['warn']:
        diskstat['def'].extend([
            'HRULE:%s#ffd000:Warning for read at %6.1f MB/s  ' % (perf_data['read']['warn'], perf_data['read']['warn']),
            'HRULE:%s#ff0000:Critical for read at %6.1f MB/s\\n' % (perf_data['read']['crit'], perf_data['read']['crit']),
        ])
        
    # show levels for write
    if perf_data['write']['warn']:
        diskstat['def'].extend([
            'HRULE:%s#ffd000:Warning for read at %6.1f MB/s  ' % (perf_data['write']['warn'], perf_data['read']['warn']),
            'HRULE:%s#ff0000:Critical for read at %6.1f MB/s\\n' % (perf_data['write']['crit'], perf_data['read']['crit']),
        ])
    
    # write average
    if 'write.avg' in rrd_file:
        diskstat['def'].extend([
            'DEF:write_avg=%s:1:MAX' % rrd_file['write.avg'],
            'CDEF:write_avg_mb=write_avg,1048576,/',
            'CDEF:write_avg_mb_neg=write_avg_mb,-1,*',
            'LINE:write_avg_mb_neg#202020',
        ])
        
    # latency
    if 'latency' in rrd_file:
        diskstat = {
            'opt' : {
                'units-exponent' : '0',
                'title': 'Latency %s / %s' % (hostname, disk),
                'vertical-label': 'Latency (ms)'
            },
            'def': [
                'DEF:latency=%s:1:MAX' % rrd_file['latency'],
                'AREA:latency#aaccdd:Latency',
                'LINE:latency#7799aa',
                'GPRINT:latency:LAST:%6.1lf ms last',
                'GPRINT:latency:AVERAGE:%6.1lf ms avg',
                'GPRINT:latency:MAX:%6.1lf ms max\\n',
            ]
        }
        
    # IOs per second
    if 'ios' in rrd_file:
        diskstat = {
            'opt' : {
                'units-exponent' : '0',
                'title': 'IOs/sec %s / %s' % (hostname, disk),
                'vertical-label': 'IO Operations / sec'
            },
            'def': [
                'DEF:ios=%s:1:MAX' % rrd_file['ios'],
                'AREA:ios#ddccaa:ios',
                'LINE:ios#aa9977',
                'GPRINT:ios:LAST:%6.1lf/sec last',
                'GPRINT:ios:AVERAGE:%6.1lf/sec avg',
                'GPRINT:ios:MAX:%6.1lf/sec max\\n',
            ]
        }
    
    if 'read_ql' in rrd_file:
        diskstat = {
            'opt' : {
                'units-exponent' : '0',
                'upper-limit' : '5',
                'lower-limit' : '5',
                'title': 'Queue Length %s / %s' % (hostname, disk),
                'vertical-label': 'Queue Length'
            },
            'def': [
                'DEF:read=%s:1:MAX' % rrd_file['read_ql'],
                'DEF:write=%s:1:MAX' % rrd_file['write_ql'],
                'CDEF:writen=write,-1,*',
                'HRULE:0#a0a0a0',
                'AREA:read#669a76',
                'AREA:writen#517ba5',
            ]
        }
else:
    diskstat = {
        'opt' : {
            'lower-limit': '0',
            'upper-limit': '1',
            'title': 'Disk throughput %s / %s' % (hostname, servicedesc),
            'vertical-label': 'Throughput (MByte/s) %'
        },
        'def': [
            'DEF:kb=%s:1:AVERAGE' % rrd_file.values()[0],
            'CDEF:mb=kb,1024,/',
            'AREA:mb#40c080',
            'HRULE:0#a0a0a0',
            'GPRINT:mb:LAST:%6.1lf MByte/s last',
            'GPRINT:mb:AVERAGE:%6.1lf MByte/s avg',
            'GPRINT:mb:MAX:%6.1lf MByte/s max\\n',
        ]
    }
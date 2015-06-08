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
# Performance data from check:
# cur_conns=116;;;;
# clients_per_sec=7.435743;;;;
# in_pkts=298.977299;;;;
# out_pkts=19828.937266;;;;
# in_bytes=743.670580463B;;;;
# out_bytes=1023640.48423B;;;;


####bandwidth
base = 1000
    
# Convert bytes to bits if neccessary
bandwidth = float(perf_data['in_bytes']['max'])

# Now choose a convenient scale, based on the known bandwith of
# the interface, and break down bandwidth, warn and crit by that
# scale.
bwuom = ' '
if bandwidth > base ** 3:
    scale = base ** 3
    bwuom = 'G'
elif bandwidth > base ** 2:
    scale = base ** 2
    bwuom = 'M'
elif bandwidth > base:
    scale = base
    bwuom = 'k'
else :
    scale = 1
    bwuom = ' '

bandwidth /= scale

range = min(10, bandwidth)


bandwidthInfo = "";
if bandwidth:
    bandwidthInfo = " at %.1f %sB/s" % (bandwidth, bwuom)

################################################################
#           _____                    _       _                 #
#          |_   _|__ _ __ ___  _ __ | | __ _| |_ ___           #
#            | |/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \          #
#            | |  __/ | | | | | |_) | | (_| | ||  __/          #
#            |_|\___|_| |_| |_| .__/|_|\__,_|\__\___|          #
#                             |_|                              #
################################################################
# Graph 1: Current Connections
vserver_cur_conns = {
    'opt' : {
        'height': '100',
        'title': "Current Connections %s / %s" % (hostname, servicedesc),
        'vertical-label': 'Connections'
    },
    'def' : [
        'DEF:cur_conns=%s:1:MAX' % rrd_file['cur_conns'],
        'AREA:cur_conns#6666FF:Current Client Connections',
        'LINE1:cur_conns#6600FF::',
        'GPRINT:cur_conns:LAST:%7.1lf last',
        'GPRINT:cur_conns:AVERAGE:%7.1lf avg',
        'GPRINT:cur_conns:MAX:%7.1lf max\\n',
    ]
}
# Graph 2: Clients per Second
vserver_conns_per_sec = {
    'opt' : {
        'height': '100',
        'title': "Connections per seconds %s / %s" % (hostname, servicedesc),
        'vertical-label': 'Connections/sec'
    },
    'def' : [
        'DEF:conn_per_s=%s:1:MAX' % rrd_file['clients_per_sec'],
        'AREA:conn_per_s#33CCFF:Connects',
        'LINE1:conn_per_s#3366FF::',
        'GPRINT:conn_per_s:LAST:%7.1lf/s last',
        'GPRINT:conn_per_s:AVERAGE:%7.1lf/s avg',
        'GPRINT:conn_per_s:MAX:%7.1lf/s max\\n',
    ]
}

# Graph 3: used bandwidth
vserver_in_out = {
    'opt' : {
        'height': '100',
        'base': '1024',
        'title': "Used bandwith %s / %s" % (hostname, servicedesc),
        'vertical-label': '%sB/sec' % bwuom
    },
    'def' : [
        'DEF:outbytes=%s:1:MAX' % rrd_file['out_bytes'],
        'CDEF:outmb=outbytes,%s,/' % scale,
        'AREA:outmb#0080e0FF:%s' % 'out'.ljust(10),
        'GPRINT:outbytes:LAST:%7.1lf %sB/s last',
        'GPRINT:outbytes:AVERAGE:%7.1lf %sB/s avg',
        'GPRINT:outbytes:MAX:%7.1lf %sB/s max\\n',

        'DEF:inbytes=%s:1:MAX' % rrd_file['in_bytes'],
        'CDEF:inmb=inbytes,%s,/' % scale,
        'LINE3:inmb#000000:',
        'LINE1:inmb#00FF00:%s' % 'in'.ljust(10),
        'GPRINT:inbytes:LAST:%7.1lf %sB/s last',
        'GPRINT:inbytes:AVERAGE:%7.1lf %sB/s avg',
        'GPRINT:inbytes:MAX:%7.1lf %sB/s max\\n',
    ]
}

# Graph 4: packets
vserver_pack_in_out = {
    'opt' : {
        'height': '100',
        'title': 'Packets %s / %s' % (hostname, servicedesc),
        'vertical-label': 'Packets/sec'
    },
    'def' : [
        'HRULE:0#C0C0C0',
        'DEF:out=%s:1:MAX' % rrd_file['out_pkts'],
        'AREA:out#0080e0:out       ',
        'GPRINT:out:LAST:%.1lf/s last',
        'GPRINT:out:AVERAGE:%.1lf/s avg',
        'GPRINT:out:MAX:%.1lf/s max\\n',
        
        'DEF:in=%s:1:MAX' % rrd_file['in_pkts'],
        'LINE3:in#000000:',
        'LINE1:in#00ff00:in        ',
        'GPRINT:in:LAST:%.1lf/s last',
        'GPRINT:in:AVERAGE:%.1lf/s avg',
        'GPRINT:in:MAX:%.1lf/s max\\n',

    ]
}

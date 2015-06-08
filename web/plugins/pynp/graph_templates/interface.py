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
# in=6864.39071505;0.01;0.1;0;125000000.0
# inucast=48.496962273;0.01;0.1;;
# innucast=4.60122981717;0.01;0.1;;
# indisc=0.0;0.01;0.1;;
# inerr=0.0;0.01;0.1;;
# out=12448.259172;0.01;0.1;0;125000000.0
# outucast=54.9846963152;0.01;0.1;;
# outnucast=10.5828285795;0.01;0.1;;
# outdisc=0.0;0.01;0.1;;
# outerr=0.0;0.01;0.1;;
# outqlen=0;;;;10000000

# Determine if Bit or Byte. Bit is signalled via a min value of 0.0
# in the 11th performance value.
if perf_data['outqlen']['min'] == "0.0":
    unit = "Bit"
    unit_multiplier = 8
else:
    unit = "B"
    unit_multiplier = 1

base = 1000
    
# Convert bytes to bits if neccessary
bandwidth = float(perf_data['in']['max']) * unit_multiplier
warn      = float(perf_data['in']['warn']) * unit_multiplier
crit      = float(perf_data['in']['crit']) * unit_multiplier


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

warn      /= scale
crit      /= scale
bandwidth /= scale

range = min(10, bandwidth)


bandwidthInfo = "";
if bandwidth:
    bandwidthInfo = " at %.1f %s%s/s" % (bandwidth, bwuom, unit)

################################################################
#           _____                    _       _                 #
#          |_   _|__ _ __ ___  _ __ | | __ _| |_ ___           #
#            | |/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \          #
#            | |  __/ | | | | | |_) | | (_| | ||  __/          #
#            |_|\___|_| |_| |_| .__/|_|\__,_|\__\___|          #
#                             |_|                              #
################################################################
# Graph 1: used bandwidth
interface_in_out = {
    'opt' : {
        'height': '100',
        'base': '1024',
        'title': "Used bandwith %s / %s" % (hostname, servicedesc),
        'vertical-label': '%s%s/sec' % (bwuom, unit)
    },
    'def' : [
        'DEF:outbytes=%s:1:MAX' % rrd_file['out'],
        'CDEF:outtraffic=outbytes,%s,*' % unit_multiplier,
        'CDEF:outmb=outtraffic,%s,/' % scale,
        'AREA:outmb#2EA5FF:%s' % 'out'.ljust(10),
        'GPRINT:outtraffic:LAST:%%7.1lf %%s%s/s last' % unit,
        'GPRINT:outtraffic:AVERAGE:%%7.1lf %%s%s/s avg' % unit,
        'GPRINT:outtraffic:MAX:%%7.1lf %%s%s/s max\\n' % unit,
        
        'DEF:inbytes=%s:1:MAX' % rrd_file['in'],
        'CDEF:intraffic=inbytes,%s,*' % unit_multiplier,
        'CDEF:inmb=intraffic,%s,/' % scale,
        'LINE3:inmb#000000:',
        'LINE1:inmb#A5FF2E:%s' % 'in'.ljust(10),
        'GPRINT:intraffic:LAST:%%7.1lf %%s%s/s last' % unit,
        'GPRINT:intraffic:AVERAGE:%%7.1lf %%s%s/s avg' % unit,
        'GPRINT:intraffic:MAX:%%7.1lf %%s%s/s max\\n' % unit,
    ]
}

if warn:
    interface_in_out['def'].extend([
        'HRULE:%s#ffff00:Warning\:  %13.1f %s%s/s\\n' % (warn, warn, bwuom, unit),
        'HRULE:-%s#ffff00:' % warn
    ])
    
if crit:
    interface_in_out['def'].extend([
        'HRULE:%s#ff0000:Critical\:  %13.1f %s%s/s\\n' % (crit, crit, bwuom, unit),
        'HRULE:-%s#ff0000:' % crit
    ])

# Graph 2: packets
interface_pack_in_out = {
    'opt' : {
        'height': '100',
        'title': 'Packets %s / %s' % (hostname, servicedesc),
        'vertical-label': 'Packets/sec'
    },
    'def' : [
        'HRULE:0#C0C0C0',
        'DEF:outu=%s:1:MAX' % rrd_file['outucast'],
        'DEF:outnu=%s:1:MAX' % rrd_file['outnucast'],
        'AREA:outu#2EA5FF:%s' % 'out unicast'.ljust(25),
        'GPRINT:outu:LAST:%7.1lf %s/s last',
        'GPRINT:outu:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:outu:MAX:%7.1lf %s/s max\\n',
        'AREA:outnu#005494:%s:STACK' % 'out broadcast/multicast'.ljust(25),
        'GPRINT:outnu:LAST:%7.1lf %s/s last',
        'GPRINT:outnu:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:outnu:MAX:%7.1lf %s/s max\\n',
        
        'DEF:inu=%s:1:MAX' % rrd_file['inucast'],
        'DEF:innu=%s:1:MAX' % rrd_file['innucast'],
        'LINE3:inu#000000:',
        'LINE1:inu#A5FF2E:%s' % 'in unicast'.ljust(25),
        'GPRINT:inu:LAST:%7.1lf %s/s last',
        'GPRINT:inu:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:inu:MAX:%7.1lf %s/s max\\n',
        'LINE3:innu#000000:',
        'LINE1:innu#549400:%s' % 'in broadcast/multicast'.ljust(25),
        'GPRINT:innu:LAST:%7.1lf %s/s last',
        'GPRINT:innu:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:innu:MAX:%7.1lf %s/s max\\n',
    ]
}

# Graph 3: errors and discards
interface_prob = {
    'opt' : {
        'height': '100',
        'title': "Problems %s / %s" % (hostname, servicedesc),
        'vertical-label': "Packets/sec"
    },
    'def' : [
        'HRULE:0#C0C0C0',
        'DEF:inerr=%s:1:MAX' % rrd_file['inerr'],
        'DEF:indisc=%s:1:MAX' % rrd_file['indisc'],
        'AREA:inerr#ff0000:%s' % 'in errors'.ljust(15),
        'GPRINT:inerr:LAST:%7.1lf %s/s last',
        'GPRINT:inerr:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:inerr:MAX:%7.1lf %s/s max\\n',
        'AREA:indisc#ff8000:%s:STACK' % 'in discards'.ljust(15),
        'GPRINT:indisc:LAST:%7.1lf %s/s last',
        'GPRINT:indisc:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:indisc:MAX:%7.1lf %s/s max\\n',
        'DEF:outerr=%s:1:MAX' % rrd_file['outerr'],
        'DEF:outdisc=%s:1:MAX' % rrd_file['outdisc'],
        'CDEF:minusouterr=0,outerr,-',
        'CDEF:minusoutdisc=0,outdisc,-',
        'AREA:minusouterr#ff0080:%s' % 'out errors'.ljust(15),
        'GPRINT:outerr:LAST:%7.1lf %s/s last',
        'GPRINT:outerr:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:outerr:MAX:%7.1lf %s/s max\\n',
        'AREA:minusoutdisc#ff8080:%s:STACK' % 'out discards'.ljust(15),
        'GPRINT:outdisc:LAST:%7.1lf %s/s last',
        'GPRINT:outdisc:AVERAGE:%7.1lf %s/s avg',
        'GPRINT:outdisc:MAX:%7.1lf %s/s max\\n',
    ]
}
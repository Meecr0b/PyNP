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
if_bandwidth = {
    'opt' : {
        'upper-limit': range,
        'lower-limit': -range,
        'units-exponent': '0',
        'base': '1024',
        'title': 'Used bandwidth %s / %s%s' % (hostname, servicedesc, bandwidthInfo),
        'vertical-label': '%s%s/sec' % (bwuom, unit)
    }, 
    'def': [
        'HRULE:0#c0c0c0'
    ]
}

if bandwidth:
    if_bandwidth['def'].extend([
        'HRULE:%s#808080:Port speed\:  %10.1f %s%s/s\\n' % (bandwidth, bandwidth, bwuom, unit),
        'HRULE:-%s#808080:' % bandwidth
    ])
    
if warn:
    if_bandwidth['def'].extend([
        'HRULE:%s#ffff00:Warning\:  %13.1f %s%s/s\\n' % (warn, warn, bwuom, unit),
        'HRULE:-%s#ffff00:' % warn
    ])

if crit:
    if_bandwidth['def'].extend([
        'HRULE:%s#ff0000:Critical\:  %13.1f %s%s/s\\n' % (crit, crit, bwuom, unit),
        'HRULE:-%s#ff0000:' % crit
    ])

if_bandwidth['def'].extend([
    # incoming
    'DEF:inbytes=%s:1:MAX' % rrd_file['in'],
    'CDEF:intraffic=inbytes,%s,*' % unit_multiplier,
    'CDEF:inmb=intraffic,%s,/' % scale,
    'AREA:inmb#00e060:in            ',
    'GPRINT:intraffic:LAST:%%7.1lf %%s%s/s last' % unit,
    'GPRINT:intraffic:AVERAGE:%%7.1lf %%s%s/s avg' % unit,
    'GPRINT:intraffic:MAX:%%7.1lf %%s%s/s max\\n' % unit,
    'VDEF:inperc=intraffic,95,PERCENTNAN',
    'VDEF:inpercmb=inmb,95,PERCENTNAN',
    'LINE:inpercmb#008f00:95% percentile',
    'GPRINT:inperc:%%7.1lf %%s%s/s\\n' % unit,
    
    # outgoing
    'DEF:outbytes=%s:1:MAX' % rrd_file['out'],
    'CDEF:outtraffic=outbytes,%s,*' % unit_multiplier,
    'CDEF:minusouttraffic=outtraffic,-1,*',
    'CDEF:outmb=outtraffic,%s,/' % scale,
    'CDEF:minusoutmb=0,outmb,-',
    'AREA:minusoutmb#0080e0:out           ',
    'GPRINT:outtraffic:LAST:%%7.1lf %%s%s/s last' % unit,
    'GPRINT:outtraffic:AVERAGE:%%7.1lf %%s%s/s avg' % unit,
    'GPRINT:outtraffic:MAX:%%7.1lf %%s%s/s max\\n' % unit,
    'VDEF:outperc=minusouttraffic,5,PERCENTNAN',
    'VDEF:outpercmb=minusoutmb,5,PERCENTNAN',
    'LINE:outpercmb#00008f:95% percentile',
    'GPRINT:outperc:%%7.1lf %%s%s/s\\n' % unit,
])

if len(rrd_file) > 11:
    if_bandwidth['def'].extend([
        'DEF:inbytesa=%s:MAX' % rrd_file['ina'],
        'DEF:outbytesa=%s:MAX' % rrd_file['outa'],
        'CDEF:intraffica=inbytesa,%s,*' % unit_multiplier,
        'CDEF:outtraffica=outbytesa,%s,*' % unit_multiplier,
        'CDEF:inmba=intraffica,1048576,/',
        'CDEF:outmba=outtraffica,1048576,/',
        'CDEF:minusoutmba=0,outmba,-',
        'LINE:inmba#00a060:in (avg)              ',
        'GPRINT:intraffica:LAST:%%6.1lf %%s%s/s last' % unit,
        'GPRINT:intraffica:AVERAGE:%%6.1lf %%s%s/s avg' % unit,
        'GPRINT:intraffica:MAX:%%6.1lf %%s%s/s max\\n' % unit,
        'LINE:minusoutmba#0060c0:out (avg)             ',
        'GPRINT:outtraffica:LAST:%%6.1lf %%s%s/s last' % unit,
        'GPRINT:outtraffica:AVERAGE:%%6.1lf %%s%s/s avg' % unit,
        'GPRINT:outtraffica:MAX:%%6.1lf %%s%s/s max\\n' % unit,
    ])

# Graph 2: packets
if_packets = {
    'opt' : {
        'title': 'Packets %s / %s' % (hostname, servicedesc),
        'vertical-label': 'packets/sec'
    }, 
    'def': [
        # ingoing
        'HRULE:0#c0c0c0',
        'DEF:inu=%s:1:MAX' % rrd_file['inucast'],
        'DEF:innu=%s:1:MAX' % rrd_file['innucast'],
        'CDEF:in=inu,innu,+',
        'AREA:inu#00ffc0:in unicast             ',
        'GPRINT:inu:LAST:%9.1lf/s last',
        'GPRINT:inu:AVERAGE:%9.1lf/s avg',
        'GPRINT:inu:MAX:%9.1lf/s max\\n',
        'AREA:innu#00c080:in broadcast/multicast :STACK',
        'GPRINT:innu:LAST:%9.1lf/s last',
        'GPRINT:innu:AVERAGE:%9.1lf/s avg',
        'GPRINT:innu:MAX:%9.1lf/s max\\n',
        'VDEF:inperc=in,95,PERCENTNAN',
        'LINE:inperc#00cf00:in 95% percentile      ',
        'GPRINT:inperc:%9.1lf/s\\n',
        
        # outgoing
        'DEF:outu=%s:1:MAX' % rrd_file['outucast'],
        'DEF:outnu=%s:1:MAX' % rrd_file['outnucast'],
        'CDEF:minusoutu=0,outu,-',
        'CDEF:minusoutnu=0,outnu,-',
        'CDEF:minusout=minusoutu,minusoutnu,+',
        'AREA:minusoutu#00c0ff:out unicast            ',
        'GPRINT:outu:LAST:%9.1lf/s last',
        'GPRINT:outu:AVERAGE:%9.1lf/s avg',
        'GPRINT:outu:MAX:%9.1lf/s max\\n',
        'AREA:minusoutnu#0080c0:out broadcast/multicast:STACK',
        'GPRINT:outnu:LAST:%9.1lf/s last',
        'GPRINT:outnu:AVERAGE:%9.1lf/s avg',
        'GPRINT:outnu:MAX:%9.1lf/s max\\n',
        'VDEF:outperc=minusout,5,PERCENTNAN',
        'LINE:outperc#0000cf:out 95% percentile     ',
        'GPRINT:outperc:%9.1lf/s\\n',
    ]
}

# Graph 3: errors and discards
if_problems = {
    'opt' : {
        'units-exponent': '0',
        'title': 'Problems %s / %s' % (hostname, servicedesc),
        'vertical-label': 'packets/sec'
    }, 
    'def': [
        'HRULE:0#c0c0c0',
        'DEF:inerr=%s:1:MAX' % rrd_file['inerr'],
        'DEF:indisc=%s:1:MAX' % rrd_file['indisc'],
        'AREA:inerr#ff0000:in errors               ',
        'GPRINT:inerr:LAST:%7.2lf/s last  ',
        'GPRINT:inerr:AVERAGE:%7.2lf/s avg  ',
        'GPRINT:inerr:MAX:%7.2lf/s max\\n',
        'AREA:indisc#ff8000:in discards             :STACK',
        'GPRINT:indisc:LAST:%7.2lf/s last  ',
        'GPRINT:indisc:AVERAGE:%7.2lf/s avg  ',
        'GPRINT:indisc:MAX:%7.2lf/s max\\n',
        'DEF:outerr=%s:1:MAX' % rrd_file['outerr'],
        'DEF:outdisc=%s:1:MAX' % rrd_file['outdisc'],
        'CDEF:minusouterr=0,outerr,-',
        'CDEF:minusoutdisc=0,outdisc,-',
        'AREA:minusouterr#ff0080:out errors              ',
        'GPRINT:outerr:LAST:%7.2lf/s last  ',
        'GPRINT:outerr:AVERAGE:%7.2lf/s avg  ',
        'GPRINT:outerr:MAX:%7.2lf/s max\\n',
        'AREA:minusoutdisc#ff8080:out discards            :STACK',
        'GPRINT:outdisc:LAST:%7.2lf/s last  ',
        'GPRINT:outdisc:AVERAGE:%7.2lf/s avg  ',
        'GPRINT:outdisc:MAX:%7.2lf/s max\\n',
    ]
}
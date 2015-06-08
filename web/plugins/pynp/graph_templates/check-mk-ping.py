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

ping = {
    'opt' : {
        'units-exponent': '0',
        'title': 'Ping times for %s' % hostname,
        'vertical-label': 'RTA (ms)'
    },
    'def': [
        'DEF:var1=%s:1:AVERAGE' % rrd_file['rta'],
        'DEF:var2=%s:1:MAX' % rrd_file['pl'],
        'VDEF:maxrta=var1,MAXIMUM',
        'CDEF:loss1=var2,100,/,maxrta,*',
        'CDEF:sp1=var1,100,/,12,*',
        'CDEF:sp2=var1,100,/,30,*',
        'CDEF:sp3=var1,100,/,50,*',
        'CDEF:sp4=var1,100,/,70,*',
        'CDEF:loss2=loss1,100,/,80,*',
        'CDEF:loss3=loss1,100,/,60,*',
        'CDEF:loss4=loss1,100,/,40,*',
        'CDEF:loss5=loss1,100,/,20,*',
        
        'AREA:var1#00FF5C:Round Trip Times',
        'AREA:sp4#00FF7C:',
        'AREA:sp3#00FF9C:',
        'AREA:sp2#00FFBC:',
        'AREA:sp1#00FFDC:',
        'LINE1:var1#000000:',
        'GPRINT:var1:LAST:%%6.2lf %s last' % unit['rta'],
        'GPRINT:var1:MAX:%%6.2lf %s max' % unit['rta'],
        'GPRINT:var1:AVERAGE:%%6.2lf %s avg \\n' % unit['rta'],
        
        'AREA:loss1#F20:Packet Loss        ',
        'AREA:loss2#F40',
        'AREA:loss3#F60',
        'AREA:loss4#F80',
        'AREA:loss5#FA0',
        
        'GPRINT:var2:MAX:%%3.0lf %s max\\n' % unit['pl'],
    ]
}
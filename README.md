# PyNP
Lightweight Multisite-Plugin for performance graphs

## Overview

## Requirements
- Check_MK Version 1.2.6

## Installation

1. install [PyNP-Plugin](https://mathias-kettner.de/check_mk_exchange_download.php?HTML=&file=PyNP-0.5.mkp "Check_MK Exchange")
2. restart OMD
3. add 'PyNP service graph'-Column to the service-view

## Configuration
see config file **web/plugins/config/pynp.py**

## Use

| Function        | Description                                          |
| ----------------| ---------------------------------------------------- |
| zoom in         | select area in the image to zoom in                  |
| zoom out        | click on the back-button (only visable when zoomed)  |
| graph-timerange | set the default timerange in the display options     |
| height/width    | set the height/width of the graph in display options |


# PyNP Templates
## server-side checks
PyNP uses the check command for selecting a template for rendering the RRD graph. 
Create the template file **my_check_command.py** below *web/plugins/pynp/graph_templates/* to add a new template

## local checks
For local checks, PyNP uses a regex on the service description to select the template file.
Add the regex to web/plugin/pynp/service_descr_tempaltes.py
```python
service_descr_template = {
#   ....
    '^My service description$': 'my_service_desc',
#   ...
}
```
Create the template file **my_service_desc.py** below *wleb/plugins/pynp/graph_templates/* to add a new template

##Tempalte definition
A template is stored in a variable.
Everything that looks like 
```python
{'opt': {...}, 'def': [...]}
```
will be used as a template
```python
#valid template
my_template = {
    'opt': {
        'rrdgraph_param': 'Value',
        'rrd_option': True,
#       ...
    },
    'def': [
        'DEF:var=%s:1:MAX' % rrd_file['ds_name'],
        'LINE1:var#226600:',
#       ...
    ]
}

#valid templates
my_templates = [
    {'opt': {...}, 'def': [...]},
    {'def': [...]},
#   {...},
]

#valid templates
my_templates_2 = {
    'templ_1': {'opt': {...}, 'def': [...]},
    'templ_2': {'def': [...]},
    'templ_n': {'opt': {...}, 'def': [...]},
}
```

- when no template definition exists, the default template is used
- every template is merged with the common template

## Variables
you have access to the following variables in a template file:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| **hostname** | string | name of the host | `'localhost'` |
| **servicedesc** | string | description of the service | `'Interface 3'` |
| **check_command** | string | name of the check_command | `'check_mk-uptime'` |
| **rrd_file** | dict | rrd files accessible by ds | `{'uptime': '/path/to/rrds/localhost/UPTIME_uptime.rrd'}` |
| **font** | string | value of pynp_font in config | `'Courier'` |
| **perf_data** | dict | perf_data from livestatus accessible by ds | `{'uptime': {'warn': None, 'crit': None, 'max': None, 'min': None, 'act': '12019013'}} |
| **perf_keys** | list | keys from perf_data in correct order | `['rta', 'pl','rtmax', 'rtmin']` |
| **unit** | dict | unit from livestatus accessible by ds | `{'rtmin': 'ms', 'rta': 'ms', 'rtmax': 'ms', 'pl': '%'}` |
| **colors** | dict | some general colors | `{'green': '#00ff0080','green_line':'#00ff00','oragen':'#ff990080',...}` |
| **rand_color** | function | generate random hex color | `rand_color(steps=8, index=None)` => `#7ffff00` |


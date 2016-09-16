#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |                     ____        _   _ ____                       |
# |                    |  _ \ _   _| \ | |  _ \                      |
# |                    | |_) | | | |  \| | |_) |                     |
# |                    |  __/| |_| | |\  |  __/                      |
# |                    |_|    \__, |_| \_|_|                         |
# |                           |___/                                  |
# |                                                                  |
# | Copyright Dennis Lerch 2015                  dennis.lerch@gmx.de |
# +------------------------------------------------------------------+
#
# PyNP is free software;  you  can  redistribute  it and/or modify  it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation  in  version  2.  PyNP  is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

import rrdtool
import Image, ImageDraw, ImageFont
import defaults
import config
import colorsys
import random
import re
import os
import time
import htmllib
from StringIO import StringIO
from lib import *
from itertools import izip_longest


class PyNPException(Exception):
    plain_title = "General error"
    title       = "Error"
    
    def __init__(self, reason):
        self.reason = reason
    
    def __str__(self):
        return self.reason


class PyNPGraph(object):
    """Class for generating the graphs"""
    def __init__(self, host, service, start=None, end=None, width=None, height=None, output_format='png', max_rows=None):
        self.host = str(host)
        self.service = str(service)
        self.start = start and int(start)
        self.end = end and int(end)
        self._file = None
        self._template = None
        self._dummy_perf_data = None
        self.rrd_host = str(pnp_cleanup(host))
        self.rrd_service = str(pnp_cleanup(service))
        self.rrd_path = str(config.pynp_rrd_cmc_path)
        self.rrd_file = '%s/%s/%s.rrd' % (self.rrd_path, self.rrd_host, self.rrd_service)
        self._rrd_file_index = {}
        self.rrd_info = '%s/%s/%s.info' % (self.rrd_path, self.rrd_host, self.rrd_service)
        self.__rrd_cached_socket = str(config.pynp_rrd_cached_socket)
        self.__rrd_update_interval = int(config.pynp_rrd_update_interval)
        self.output_format = output_format
        
        try:
            self._width = int(width)
        except:
            self._width = config.pynp_default_width
        try:
            self._height = int(height)
        except:
            self._height = config.pynp_default_height
        try:
            self._max_rows = int(max_rows)
        except:
            self._max_rows = None #default 400 by rrd
    
    @property
    def file(self):
        """Return the file as string"""
        if not self._file:
            self.create_file()
        return self._file
    
    @property
    def template(self):
        """Return the PyNPTemplate"""
        if not self._template:
            self._template = PyNPTemplate(self)
        return self._template
    
    @property
    def dummy_perf_data(self):
        """Return a dummy perf_data line"""
        if not self._dummy_perf_data:
            self.lookup_rrd_info()
        return self._dummy_perf_data
    
    @property
    def rrd_file_index(self):
        """Return a dummy perf_data line"""
        if not self._rrd_file_index:
            self.lookup_rrd_info()
        return self._rrd_file_index
    
    @property
    def height(self):
        if self._height > config.pynp_max_height:
            self._height = config.pynp_max_height
        return self._height
    
    @property
    def width(self):
        if self._width > config.pynp_max_width:
            self._width = config.pynp_max_width
        return self._width
    
    @property
    def max_rows(self):
        if self._max_rows > config.pynp_max_rows:
            self._max_rows = config.pynp_max_rows
        return self._max_rows
    
    def create_file(self):
        """Flush the rrd_cache if it's necessary, then get the rrd-config, generate the graph(s) and merge them to a single file"""
        graphs = []
        
        if not self.end or self.end > time.time() - self.__rrd_update_interval:
            self.flush_rrd_cache()
        
        if self.output_format == 'csv':
            for tmpl_params in self.template.rrd_params:
                graphs.append(rrdtool.xport(*tmpl_params))
            self._file = self.merge_files(graphs)
        else:
            for tmpl_params in self.template.rrd_params:
                graphs.append(rrdtool.graphv('-', *tmpl_params))
            self._file = self.merge_files(graphs)
        if not self._file:
            PyNPException('No graph was generated')
            
    def flush_rrd_cache(self):
        """Flush the rrd_cache for necessary files"""
        rrdtool.flushcached('--daemon', self.__rrd_cached_socket, [self.rrd_file])
    
    def lookup_rrd_info(self):
        """generate dummy perf_data"""
        #self._dummy_perf_data = '=;;;; '.join(map(lambda x: x[len(self.service)+1:-4], self._rrd_files)) + '=;;;;'
        #self._rrd_file = '%s.rrd' % self.rrd_service
        with open(self.rrd_info) as info:
            metrics = re.search('(?:METRICS (.*?)\n)', info.read()).groups()[0]
        self._rrd_file_index = dict((v, k+1) for k, v in enumerate(metrics.split(';')))
        self._dummy_perf_data = '=;;;; '.join(metrics.split(';')) + '=;;;;'
    
    def merge_files(self, files):
        """Merge multiple files to a single file and returns them as string"""
        file = None
        
        if self.output_format == 'csv':
            file = ''
            header = ['"TIME_IDX"']
            time_idx = files[0]['meta']['start']
            step = files[0]['meta']['step']
            i = 0
            
            for e in map(lambda x: x['meta']['legend'], files):
                header.extend(e)
            data = [header]
            
            while not (time_idx > self.end or i > files[0]['meta']['rows']-1):
                line = [time_idx]
                for e in map(lambda x: x['data'][i], files):
                    line.extend(e)
                data.append(line)
                time_idx += step
                i += 1
            for line in data:
                file += ';'.join(map(lambda x: str(x or ''), line)) + '\n'
        else: #image
            tmp_string_io = StringIO()
            act_height = 0
            width = max(map(lambda x: x['image_width'], files))
            height = sum(map(lambda x: x['image_height'], files))
            images = map(lambda x: Image.open(StringIO(x['image'])), files)
            merged_image = Image.new(images[0].mode, (width, height))
            merged_image.format = images[0].format
            for image in images:
                merged_image.paste(image, (0, act_height))
                act_height += image.size[1]
            merged_image.save(tmp_string_io, format=merged_image.format)
            file = tmp_string_io.getvalue()
            tmp_string_io.close()
        return file


class PyNPTemplate(object):
    """Class for the PyNP Templates"""
    def __init__(self, graph):
        self._rrd_params = None
        self.__graph = graph
        self.__config_path = defaults.omd_root + '/local/share/check_mk/web/plugins/pynp'
        self.__template_paths = [defaults.omd_root + '/local/share/check_mk/web/plugins/pynp/graph_templates']
        self.__template_paths.extend(config.pynp_template_paths)
        self.__color_steps = config.pynp_random_colors or 8
        self.__font = config.pynp_font
        self._perf_data = {}
        self._perf_keys = []
        self._unit = {}
        self._check_command = None
        self._rrd_file = {}
        self._rrd_file_index = {}
        self._substitutions = None
        self.__xport_formats = ['csv']
    
    @property
    def rrd_params(self):
        """Return rrd params for graph"""
        if not self._rrd_params:
            self.create_rrd_params()
        return self._rrd_params
    
    @property
    def perf_data(self):
        if not self._perf_data:
            self.lookup_livestatus()
        return self._perf_data
    
    @property
    def perf_keys(self):
        if not self._perf_keys:
            self.lookup_livestatus()
        return self._perf_keys
    
    @property
    def unit(self):
        if not self._unit:
            self.lookup_livestatus()
        return self._unit
    
    @property
    def check_command(self):
        if not self._check_command:
            self.lookup_livestatus()
        return self._check_command
    
    @property
    def rrd_file(self):
        if not self._rrd_file:
            self.lookup_livestatus()
        return self._rrd_file
    
    @property
    def substitutions(self):
        if not self._substitutions:
            self._substitutions = {
                'hostname'      : self.__graph.host,
                'servicedesc'   : self.__graph.service,
                'rrd_file'      : self.rrd_file,
                'rrd_file_index': self.__graph.rrd_file_index,
                'font'          : self.__font,
                'perf_data'     : self.perf_data,
                'perf_keys'     : self.perf_keys,
                'unit'          : self.unit,
                'rand_color'    : self.random_hex_color,
                'check_command' : self.check_command,
            }
        return self._substitutions
    
    def create_rrd_params(self):
        service_descr_template = {}
        graph_params = []
        
        #load all files in pynp path to extend the substitutions and get service_templates
        for fn in filter(lambda x: x.endswith(".py"), os.listdir(self.__config_path)):
            execfile("%s/%s" % (self.__config_path, fn), {}, self.substitutions)
        
        if 'service_descr_template' in self.substitutions:
            service_descr_template = self.substitutions.pop('service_descr_template')
        
        #building graph_templates based on service description
        if self.check_command == 'check_mk-local' and service_descr_template:
            for expression, file in service_descr_template.iteritems():
                if regex(expression).match(self.__graph.service):
                    graph_params = self.load_template(file)
                    if graph_params:
                        break
        
        #building graph-templates based on check_command
        if not graph_params:
            graph_params = self.load_template(self.check_command)
        
        #building default templates
        if not graph_params:
            graph_params = self.load_template('default')
        
        #load common template file in subfolder and merge with each graph_template
        common = self.load_template("common")[0]
        if common:
            for index, rrd_conf in enumerate(graph_params):
                graph_params[index] = dict(self.merge_conf(common, rrd_conf))
        
        #merge the options from request
        options = {
            'start' : self.__graph.start,
            'end'   : self.__graph.end,
            'height': self.__graph.height,
            'width' : self.__graph.width,
        }
        
        if self.__graph.max_rows and self.__graph.output_format in self.__xport_formats:
            options['maxrows'] = self.__graph.max_rows
        
        for index, rrd_conf in enumerate(graph_params):
            graph_params[index] = dict(self.merge_conf(rrd_conf, {'opt': options}))
        
        #finishing the graph_templates (options to parameter)
        for index, rrd_conf in enumerate(graph_params):
            if self.__graph.output_format in self.__xport_formats:
                xports = []
                #cleanup graph_params for xport
                for key in filter(lambda x: x not in ['start', 'end', 'maxrows'], rrd_conf['opt']):
                    del rrd_conf['opt'][key]
                #extend graph_params for xport
                for line in graph_params[index]['def']:
                    for xport_attribute in ['def', 'cdef']:
                        if line.lower().startswith(xport_attribute):
                            x_var = line.split('=',1)[0][len(xport_attribute)+1:]
                            xports.append('XPORT:%s:"%s"'% (x_var, x_var))
                graph_params[index]['def'] += xports
            graph_params[index] = self.to_rrd_graph_parameter(rrd_conf['opt']) + rrd_conf['def']
        #graph_template = map(lambda x,y: self.to_rrd_graph_parameter(x) + y, graph_template)
        
        self._rrd_params = graph_params
        return True
    
    def load_template(self, file):
        template_file = ''
        local_dict = {}
        for path in reversed(self.__template_paths):
            if os.path.isfile('%s/%s.py' % (path, file)):
                template_file = open('%s/%s.py' % (path, file), 'r')
                break
        if not template_file:
            return[]
        
        template = template_file.read()
        template_file.close()
        compiled_template = compile(template, '<string>', 'exec')
        try:
            exec compiled_template in self.substitutions, local_dict
        except:
            raise PyNPException("Error while loading template file %s.py:\n%s" % (file, format_exception()))
        
        #variables from template ordered by declaration time
        template_vars = [
            {key: local_dict[key]} for key in filter(lambda x: x in local_dict, compiled_template.co_names)
        ]
        
        #get everything that looks like {'opt': {...}, 'def': [...]}
        return list(self.find_templates_in_var(template_vars))
    
    def lookup_livestatus(self):
        query = "GET services\nFilter: host_name = %s\nFilter: description = %s\n" \
                "Columns: perf_data check_command" % (self.__graph.host, self.__graph.service)
        result = html.live.query(query)
        if result:
            perf_data, check_command = result[0]
        else:
            perf_data, check_command = None, None
        
        #if no result from livestatus, use dummy data from graph
        if not perf_data:
            perf_data = self.__graph.dummy_perf_data
        
        for index, perf_line in enumerate(perf_data.split()):
            if u'=' in perf_line:
                key, values = str(perf_line).split('=')
                self._rrd_file[key] = self.__graph.rrd_file
                self._perf_keys.append(key)
                perf_val = dict(
                    izip_longest(
                        ["act", "warn", "crit", "min", "max"],
                        map(lambda x: x if x else False, values.split(';'))
                    )
                )
                self._perf_data[key] = perf_val
                if perf_val['act']:
                    self._unit[key] = regex('[\d\.]*').split(perf_val['act'])[-1]
                    if self._unit[key] == '%':
                        self._unit[key] = '%%'    #used for string formating
                else:
                    self._unit[key] = ''
            else:
                self._check_command = perf_line[1:-1] #fix for mrpe
        self._check_command = self._check_command or check_command.split('!')[0]
    
    def find_templates_in_var(self, d):
        if isinstance(d, dict):
            if ('def' in d or 'opt' in d):
                yield d
            else:
                for k, v in d.iteritems():
                    for x in self.find_templates_in_var(v):
                        yield x
        elif isinstance(d, list):
            for v in d:
                for x in self.find_templates_in_var(v):
                    yield x
    
    def merge_conf(self, conf_a, conf_b):
        for k in set(conf_a.keys()).union(conf_b.keys()):
            if k in conf_a and k in conf_b:
                if isinstance(conf_a[k], dict) and isinstance(conf_b[k], dict):
                    yield (k, dict(self.merge_conf(conf_a[k], conf_b[k])))
                else:
                    yield (k, conf_b[k])
            elif k in conf_a:
                yield (k, conf_a[k])
            else:
                yield (k, conf_b[k])
    
    def to_rrd_graph_parameter(self, options):
        params = []
        for option, value in options.iteritems():
            if isinstance(value, dict):
                for x, y in value.iteritems():
                    params += ["--" + option, "%s%s" % (x,y)]
            elif value is True:
                params.append("--" + option)
            elif value is False or value is None:
                continue
            else:
                params += ["--" + option, str(value)]
        return params
    
    def random_hex_color(self, index=None):
        if type(index) is int:
            #return color_index with maximum differenze between last color
            index %= self.__color_steps
            if index%2==0:
                color_index = index/2
            else:
                color_index = index/2 + self.__color_steps/2
        else:
            color_index = random.randint(0, steps-1)
        hue = 1. / self.__color_steps * color_index + 0.25  #to begin the hue with green, add 0.25 to it (red is an evil color ;) )
        saturation = 1
        lightness = 0.5
        return "#%02x%02x%02x" % tuple(map(lambda x: int(x*255), colorsys.hls_to_rgb(hue, lightness, saturation)))

def exception_to_graph(e):
    font = ImageFont.load_default()
    
    details = 'Check_MK Version: ' + defaults.check_mk_version + '\n' \
            + 'Page: ' + html.myfile + '.py\n\n' \
            + 'GET/POST-Variables:\n' \
            + '\n'.join([ ' '+n+'='+v for n, v in sorted(html.vars.items()) ]) + '\n' \
            + '\n' \
            + format_exception()
            
    error_msg = "Internal error:%s\n----------\nDetails:\n\n%s" % (html.attrencode(e), details)
    error_list = error_msg.split('\n')
    
    text_dimension = map(font.getsize, error_list)
    text_width = max([x[0] for x in text_dimension])
    text_height = sum([x[1] for x in text_dimension])
    
    img_width = text_width + 100
    img_height = text_height + 100
    
    img = Image.new("RGB", (img_width, img_height), '#ff0000')
    img.format = "png"
    draw = ImageDraw.Draw(img)
    
    for index, line in enumerate(error_list):
        act_height = (img_height-text_height)/2 + index * text_dimension[index][1]
        act_width = (img_width-text_width)/2                #center - left align
        #act_width = (img_width-text_dimension[index][0])/2 #center - center align
        draw.text((act_width, act_height), line, "#ffffff", font=font)
    
    tmp_string_io = StringIO()
    img.save(tmp_string_io, format = img.format)
    exception_graph = tmp_string_io.getvalue()
    tmp_string_io.close()
    
    return exception_graph

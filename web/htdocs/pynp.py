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
# | Copyright Dennis Lerch 2016                  dennis.lerch@gmx.de |
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
from PIL import Image, ImageDraw, ImageFont
import defaults
import config
#import colorsys
#import random
#import re
#import os
import time
import htmllib
import xml.etree.ElementTree
from StringIO import StringIO
from lib import *
#from itertools import izip_longest

import metrics as CMK_metrics


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
        self._start = start and int(start)
        self._end = end and int(end)
        self._file = None
        self._rrd_xml = PyNPXMLConfig('%s/%s/%s.xml' % (str(config.pynp_rrd_path), str(pnp_cleanup(host)), str(pnp_cleanup(service))))
        self.rrd_base = '%s/%s/%s' % (str(config.pynp_rrd_path), str(pnp_cleanup(host)), self._rrd_xml.NAGIOS_SERVICEDESC)
        self.__rrd_cached_socket = str(config.pynp_rrd_cached_socket)
        self.__rrd_update_interval = int(config.pynp_rrd_update_interval)
        self.output_format = output_format
        CMK_metrics.load_plugins(True)
        
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
    def start(self):
        """Return start time"""
        if not self._start:
            self._start = int(time.time()) - 60*60*24*7 # one week default
        return self._start
    
    @property
    def end(self):
        """Return end time"""
        if not self._end:
            self._end = int(time.time())
        return self._end
    
    @property
    def file(self):
        """Return the file as string"""
        if not self._file:
            self.create_file()
        return self._file
    
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
        graph_templates = []
        graphs = []
        
        if self.end > time.time() - self.__rrd_update_interval:
            self.flush_rrd_cache()
        
        perf_var_names = map(lambda x: filter(lambda y: 'NAME' in y, x)[0]['NAME'].lower(), self._rrd_xml.DATASOURCE)    
        perf_data = [ ( varname, 1, "", 1, 1, 1, 1 ) for varname in perf_var_names ]
        translated_metrics =  CMK_metrics.translate_metrics(perf_data, self._rrd_xml.NAGIOS_SERVICECHECKCOMMAND)
        
        for graph_template in CMK_metrics.get_graph_templates(translated_metrics):
            graph_templates.append(self.render_graph_pynp(graph_template, translated_metrics))

        if self.output_format == 'csv':
            for tmpl_params in self.template.rrd_params:
                graphs.append(rrdtool.xport(*tmpl_params))
            self._file = self.merge_files(graphs)
        else:
            for template in graph_templates:
                graphs.append(rrdtool.graphv('-', *template))
            self._file = self.merge_files(graphs)
        if not self._file:
            PyNPException('No graph was generated')

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################

    def render_graph_pynp(self, graph_template, translated_metrics):
        graph_title = None
        vertical_label = None
        
        rrdgraph_commands = []
        
        legend_precision    = graph_template.get("legend_precision", 2)
        legend_scale        = graph_template.get("legend_scale", 1)
        legend_scale_symbol = CMK_metrics.scale_symbols[legend_scale]
        
        # Define one RRD variable for each of the available metrics.
        # Note: We need to use the original name, not the translated one.
        for var_name, metrics in translated_metrics.items():
            rrd = self.rrd_base + "_" + metrics["orig_name"] + ".rrd"
            scale = metrics["scale"]
            unit = metrics["unit"]
            
            if scale != 1.0:
                rrdgraph_commands.append("DEF:%s_UNSCALED=%s:1:MAX" % (var_name, rrd))
                rrdgraph_commands.append("CDEF:%s=%s_UNSCALED,%f,*" % (var_name, var_name, scale))
            
            else:
                rrdgraph_commands.append("DEF:%s=%s:1:MAX" % (var_name, rrd))
            
            # Scaling for legend
            rrdgraph_commands.append("CDEF:%s_LEGSCALED=%s,%f,/" % (var_name, var_name, legend_scale))
            
            # Prepare negative variants for upside-down graph
            rrdgraph_commands.append("CDEF:%s_NEG=%s,-1,*" % (var_name, var_name))
            rrdgraph_commands.append("CDEF:%s_LEGSCALED_NEG=%s_LEGSCALED,-1,*" % (var_name, var_name))
        
        
        # Compute width of columns in case of mirrored legend
        
        total_width = 89 # characters
        left_width = max([len(_("Average")), len(_("Maximum")), len(_("Last"))]) + 2
        column_width = (total_width - left_width) / len(graph_template["metrics"]) - 2
        
        # Now add areas and lines to the graph
        graph_metrics = []
        
        # Graph with upside down metrics? (e.g. for Disk IO)
        have_upside_down = False
        
        # Compute width of the right column of the legend
        max_title_length = 0
        for nr, metric_definition in enumerate(graph_template["metrics"]):
            if len(metric_definition) >= 3:
                title = metric_definition[2]
            elif not "," in metric_definition:
                metric_name = metric_definition[0].split("#")[0]
                mi = translated_metrics[metric_name]
                title = mi["title"]
            else:
                title = ""
            max_title_length = max(max_title_length, len(title))
        
        
        for nr, metric_definition in enumerate(graph_template["metrics"]):
            metric_name = metric_definition[0]
            line_type = metric_definition[1] # "line", "area", "stack"
            
            # Optional title, especially for derived values
            if len(metric_definition) >= 3:
                title = metric_definition[2]
            else:
                title = ""
            
            # Prefixed minus renders the metrics in negative direction
            if line_type[0] == '-':
                have_upside_down = True
                upside_down = True
                upside_down_factor = -1
                line_type = line_type[1:]
                upside_down_suffix = "_NEG"
            else:
                upside_down = False
                upside_down_factor = 1
                upside_down_suffix = ""
            
            if line_type == "line":
                draw_type = "LINE"
                draw_stack = ""
            elif line_type == "area":
                draw_type = "AREA"
                draw_stack = ""
            elif line_type == "stack":
                draw_type = "AREA"
                draw_stack = ":STACK"
            
            # User can specify alternative color using a suffixed #aabbcc
            if '#' in metric_name:
                metric_name, custom_color = metric_name.split("#", 1)
            else:
                custom_color = None
            
            commands = []
            # Derived value with RBN syntax (evaluated by RRDTool!).
            if "," in metric_name:
                # We evaluate just in order to get color and unit.
                # TODO: beware of division by zero. All metrics are set to 1 here.
                value, unit, color = CMK_metrics.evaluate(metric_name, translated_metrics)
                
                if "@" in metric_name:
                    expression, explicit_unit_name = metric_name.rsplit("@", 1) # isolate expression
                else:
                    expression = metric_name
                
                # Choose a unique name for the derived variable and compute it
                commands.append("CDEF:DERIVED%d=%s" % (nr , expression))
                if upside_down:
                    commands.append("CDEF:DERIVED%d_NEG=DERIVED%d,-1,*" % (nr, nr))
                    
                metric_name = "DERIVED%d" % nr
                # Scaling and upsidedown handling for legend
                commands.append("CDEF:%s_LEGSCALED=%s,%f,/" % (metric_name, metric_name, legend_scale))
                if upside_down:
                    commands.append("CDEF:%s_LEGSCALED%s=%s,%f,/" % (metric_name, upside_down_suffix, metric_name, legend_scale * upside_down_factor))
            
            else:
                mi = translated_metrics[metric_name]
                if not title:
                    title = mi["title"]
                color = CMK_metrics.parse_color_into_hexrgb(mi["color"])
                unit = mi["unit"]
            
            if custom_color:
                color = "#" + custom_color
            
            # Paint the graph itself
            # TODO: Die Breite des Titels intelligent berechnen. Bei legend = "mirrored" muss man die
            # Vefügbare Breite ermitteln und aufteilen auf alle Titel
            right_pad = " " * (max_title_length - len(title))
            commands.append("%s:%s%s%s:%s%s%s" % (draw_type, metric_name, upside_down_suffix, color, title.replace(":", "\\:"), right_pad, draw_stack))
            if line_type == "area":
                commands.append("LINE:%s%s%s" % (metric_name, upside_down_suffix, CMK_metrics.render_color(CMK_metrics.darken_color(CMK_metrics.parse_color(color), 0.2))))
            
            unit_symbol = unit["symbol"]
            if unit_symbol == "%":
                unit_symbol = "%%"
            else:
                unit_symbol = " " + unit_symbol 
            graph_metrics.append((metric_name, unit_symbol, commands))
            
            # Use title and label of this metrics as default for the graph
            if title and not graph_title:
                graph_title = title
            if not vertical_label:
                vertical_label = unit["title"]
        
        
        # Now create the rrdgraph commands for all metrics - according to the choosen layout
        for metric_name, unit_symbol, commands in graph_metrics:
            rrdgraph_commands.extend(commands)
            legend_symbol = unit_symbol
            if unit_symbol and unit_symbol[0] == " ":
                legend_symbol = " %s%s" % (legend_scale_symbol, unit_symbol[1:])
            for what, what_title in [ ("AVERAGE", _("average")), ("MAX", _("max")), ("LAST", _("last")) ]:
                rrdgraph_commands.append("GPRINT:%%s_LEGSCALED:%%s:%%%%8.%dlf%%s %%s" % legend_precision % \
                            (metric_name, what, legend_symbol, what_title))
            rrdgraph_commands.append("COMMENT:\\n")
        
        
        # For graphs with both up and down, paint a gray rule at 0
        if have_upside_down:
            rrdgraph_commands.append("HRULE:0#c0c0c0")
        
        # Now compute the arguments for the command line of rrdgraph
        rrdgraph_arguments = []
        
        graph_title = graph_template.get("title", " ")
        vertical_label = graph_template.get("vertical_label", " ")
        
        rrdgraph_arguments.extend(
            [
                "--vertical-label", vertical_label,
                "--title", graph_title,
                "--height", str(self.height),
                "--width", str(self.width),
                "--start", str(self.start),
                "--end",str(self.end),
             ]
        )
        
        min_value, max_value = CMK_metrics.get_graph_range(graph_template, translated_metrics)
        if min_value != None and max_value != None:
            rrdgraph_arguments.extend(['-l', str(min_value), '-u', str(max_value])
        else:
            rrdgraph_arguments.extend(['-l', '0'])
        
        return rrdgraph_arguments + rrdgraph_commands

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################

            
    def flush_rrd_cache(self):
        """Flush the rrd_cache for necessary files"""
        rrdtool.flushcached('--daemon', self.__rrd_cached_socket, list(set(map(lambda x: filter(lambda e: 'RRDFILE' in e, x)[0]['RRDFILE'], self._rrd_xml.DATASOURCE))))
        
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

class PyNPXMLConfig(object):
    """Class to get the xml config"""
    def __init__(self, xmlfile):
        config = xml.etree.ElementTree.parse(xmlfile).getroot()
        for element in self.parse_xml(config):
            for k, v in element.iteritems():
                if isinstance(v, list):
                    if not k in self.__dict__:
                        self.__dict__[k] = []
                    self.__dict__[k].append(v)
                else:
                    self.__dict__[k] = v
            
    
    def parse_xml(self, xml):
        childs = xml.getchildren()
        if len(childs) == 0:
            return xml.text
        else:
            x = []
            for e in childs:
                x.append({e.tag : self.parse_xml(e)})
            return x

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

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

def pynp_file():
    import pynp
    import time
    host = html.var_utf8("host")
    service = html.var_utf8("service")
    start = html.var_utf8("start", None)
    end = html.var_utf8("end", None)
    width = html.var_utf8("width", None)
    height = html.var_utf8("height", None)
    output_format = html.var_utf8("output_format", "png")
    max_rows = html.var_utf8("max_rows", None)
    
    filename = str('%s_%s' % (host, service)).replace('.', '_')
    if start and end:
        start_str = time.strftime("%Y%m%d%H%M", time.localtime(int(start)))
        end_str = time.strftime("%Y%m%d%H%M", time.localtime(int(end)))
        filename += '__%s-%s' % (start_str, end_str)
    html.req.headers_out['Content-Disposition'] = 'filename=%s.%s' % (filename, str(output_format))
    
    if output_format == 'csv':
        html.req.content_type = 'text/csv'
    else:
        html.req.content_type = 'image/png'
    try:
        file= pynp.PyNPGraph(host, service, start, end, width, height, output_format, max_rows).file
    except Exception, e:
        html.req.content_type = 'image/png'
        file = pynp.exception_to_graph(e)
        
    html.write(file)

pagehandlers.update({
   "pynp"       : pynp_file,
})
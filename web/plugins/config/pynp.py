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

import defaults

pynp_rrd_path        = defaults.omd_root + '/var/pnp4nagios/perfdata' # '/var/check_mk/rrd'
pynp_rrd_cached_socket   = 'unix:%s/tmp/run/rrdcached.sock' % defaults.omd_root
pynp_rrd_update_interval = 3600         # see TIMEOUT in etc/rrdcached.conf, 
pynp_default_height      = None         # use default rrdtool height
pynp_default_width       = None         # use default rrdtool width
pynp_max_height          = 500          # max height of a graph
pynp_max_width           = 2000         # max width of a graph
pynp_max_rows            = 2000         # max rows for xport
pynp_random_colors       = 8
pynp_font                = 'Courier'
pynp_replace_pnp_icon    = True
pynp_template_paths      = []           # add other paths for template lookup

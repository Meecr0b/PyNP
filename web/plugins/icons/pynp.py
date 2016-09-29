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

# Links to PyNP IMG
def pynp_url(row, what):
    if what == "host":
        return "view.py?view_name=searchpnp&host_regex=^%s$&filled_in=filter" % (html.urlencode(row["host_name"]))
    else:
        return "view.py?view_name=searchpnp&host_regex=^%s$&service_regex=^%s$&filled_in=filter" % (html.urlencode(row["host_name"]), html.urlencode(row["service_description"]))

def pynp_img(row, what):
    sitename = row["site"]
    host = row["host_name"]
    if what == "host":
        svc = "Check_MK"
    else:
        svc = row["service_description"]
    site = html.site_status[sitename]["site"]['url_prefix']
    return "%scheck_mk/pynp.py?host=%s&service=%s&width=400&height=50" % (site, html.urlencode(host), html.urlencode(svc))

def pynp_icon(row, what):
    if 'X' in html.display_options:
        url = pynp_url(row, what)
    else:
        url = ""
    return '<a href="%s" onmouseover="show_hover_menu(event, \'<table><tr><td><img width=400px src=%s></td></tr></table>\')"' \
           'onmouseout="hide_hover_menu()">%s</a>' % (url, pynp_img(row, what), html.render_icon('pnp', ''))

def paint_pynp_graph(what, row, tags, custom_vars):
    pnpgraph_present = row[what + "_pnpgraph_present"]
    if pnpgraph_present == 1:
        return pynp_icon(row, what)

if config.pynp_replace_pnp_icon:
    if multisite_icons_and_actions.pop('perfgraph', None):
        multisite_icons_and_actions['perfgraph'] = {
            'columns': ['pnpgraph_present'],
            'paint': paint_pynp_graph,
            'sort_index': 20,
            'toplevel': True
        }
        #replace Perf-O-Meter link
        pnp_url = lambda row, what, how='graph': pynp_url(row, what)

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

import time

def paint_pynpgraph(sitename, host, service = "Check_MK", show=True):
    if show:
        site_url = html.site_status[sitename]["site"]["url_prefix"]
        pynp_timerange = get_painter_option("pynp_timerange")
        from_ts, to_ts = "", ""
        
        if pynp_timerange != None:
            vs = multisite_painter_options["pynp_timerange"]['valuespec']
            from_ts, to_ts = map(int, vs.compute_range(pynp_timerange)[0])
            from_ts_str = time.strftime("%d.%m.%Y %H:%M", time.localtime(from_ts))
            to_ts_str   = time.strftime("%d.%m.%Y %H:%M", time.localtime(to_ts))
        else:
            from_ts_str, to_ts_str = "",""
        
        height = get_painter_option("pynp_height")
        width = get_painter_option("pynp_width")
        
        return "pynpgraph", "<script src=\"js/jquery.js\"></script>" \
                            "<script src=\"js/imgareaselect.js\"></script>" \
                            "<script src=\"js/pynp.js\"></script>" \
                            "<link rel=\"stylesheet\" type=\"text/css\" href=\"pynp.css\"/>" \
                            "<div class=\"pynp_graph\" >" \
                            "  <div style=\"position:relative;\">" \
                            "    <img class=\"pynp_img\" src=\"%scheck_mk/pynp.py?host=%s&service=%s&start=%s&end=%s&width=%s&height=%s\" title=\"%s/%s (%s - %s)\" alt=\"PyNP Graph\"/>" \
                            "    <a class=\"pynp_back\" title=\"Back\" alt=\"back button\"/>" \
                            "    <a class=\"pynp_csv_export\" title=\"CSV export\" alt=\"csv export\" href=\"%scheck_mk/pynp.py?host=%s&service=%s&start=%s&end=%s&output_format=csv\"/>" \
                            "  </div>" \
                            "</div>" \
                            "<script>pynp_init();</script>" % (site_url, host, service, from_ts, to_ts, width, height, host, service, from_ts_str, to_ts_str, site_url, host, service, from_ts, to_ts)
    return "pynpgraph", ""

multisite_painters["svc_pynp_graph" ] = {
    "title"   : "PyNP service graph",
    "short"   : "Performance Graph",
    "columns" : [ "host_name", "service_description", "service_pnpgraph_present" ],
    "options" : [ "pynp_timerange", "pynp_width", "pynp_height" ],
    "paint"   : lambda row: paint_pynpgraph(row["site"], row["host_name"], row["service_description"], row["service_pnpgraph_present"])
}

multisite_painter_options["pynp_timerange"] = {
    'valuespec' : Timerange(
        title = _("PyNP Timerange"),
        default_value = "w0",
        include_time = True,
    )
}

multisite_painter_options["pynp_height"] = {
    'valuespec' : DropdownChoice(
        title = _("PyNP Height"),
        default_value = "100",
        choices = [
            ("50",  _("50px")),
            ("75",  _("75px")),
            ("100", _("100px")),
            ("150", _("150px")),
            ("200", _("200px"))
        ]
    )
}

multisite_painter_options["pynp_width"] = {
    'valuespec' : DropdownChoice(
        title = _("PyNP Width"),
        default_value = "auto",
        choices = [
            ("auto", _("auto")),
            ("320",  _("320px")),
            ("400",  _("400px")),
            ("600",  _("600px")),
            ("800",  _("800px"))
        ]
    )
}

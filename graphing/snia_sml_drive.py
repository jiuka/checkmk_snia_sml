# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# snia_sml_drive - SNIA Media Access Device check for Checkmk
#
# Copyright (C) 2024  Marius Rieder <marius.rieder@scs.ch>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from cmk.graphing.v1 import metrics, perfometers, Title

metric_tape_hours = metrics.Metric(
    name='tape_hours',
    title=Title('Tape Drive Hours'),
    unit=metrics.Unit(metrics.TimeNotation()),
    color=metrics.Color.BLUE,
)

metric_tape_loads = metrics.Metric(
    name='tape_loads',
    title=Title('Tape Loads'),
    unit=metrics.Unit(metrics.DecimalNotation('Tape'), metrics.StrictPrecision(0)),
    color=metrics.Color.PURPLE,
)

perfometer_snia_sml_drive = perfometers.Stacked(
    name='snia_sml_drive',
    upper=perfometers.Perfometer(
        name='tape_hours',
        focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(100)),
        segments=['tape_hours'],
    ),
    lower=perfometers.Perfometer(
        name='tape_loads',
        focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(100)),
        segments=['tape_loads'],
    ),
)

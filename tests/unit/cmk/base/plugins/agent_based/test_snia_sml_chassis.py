# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# snia_sml_chassis - SNIA Media Access Device check for Checkmk
#
# Copyright (C) 2021  Marius Rieder <marius.rieder@scs.ch>
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

import pytest  # type: ignore[import]
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import snia_sml_chassis

# Example excerpt from SNMP data:
# .1.3.6.1.4.1.14851.3.1.4.10.1.1.1 = INTEGER: 1 --> SNIA-SML-MIB::subChassisIndex.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.2.1 = STRING: "IBM" --> SNIA-SML-MIB::subChassis-Manufacturer.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.3.1 = STRING: "3573-TL" --> SNIA-SML-MIB::subChassis-Model.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.4.1 = STRING: "3555L3A7800VVF" --> SNIA-SML-MIB::subChassis-SerialNumber.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.5.1 = INTEGER: false(2) --> SNIA-SML-MIB::subChassis-LockPresent.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.6.1 = INTEGER: 0 --> SNIA-SML-MIB::subChassis-SecurityBreach.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.7.1 = INTEGER: false(2) --> SNIA-SML-MIB::subChassis-IsLocked.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.8.1 = STRING: "IBM 3573-TL 3555L3A7800VVF" --> SNIA-SML-MIB::subChassis-Tag.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.9.1 = STRING: "3573-TL 3555L3A7800VVF" --> SNIA-SML-MIB::subChassis-ElementName.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.10.1 = INTEGER: ok(2) --> SNIA-SML-MIB::subChassis-OperationalStatus.1
# .1.3.6.1.4.1.14851.3.1.4.10.1.11.1 = INTEGER: mainSystemChassis(17) --> SNIA-SML-MIB::subChassis-PackageType.1

@pytest.mark.parametrize('string_table, result', [
    (
        [['IBM TL-3573', '2', '17']],
        [snia_sml_chassis.SniaSmlChassi(tag='IBM TL-3573', type=17, status=2)]
    ),
])
def test_parse_snia_sml_chassis(string_table, result):
    assert list(snia_sml_chassis.parse_snia_sml_chassis(string_table)) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (
        [snia_sml_chassis.SniaSmlChassi(tag='IBM TL-3573', type=17, status=2)],
        [Service(item='IBM TL-3573')]
    )
])
def test_discovery_snia_sml_chassis(section, result):
    assert list(snia_sml_chassis.discovery_snia_sml_chassis(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    (
        'foo',
        [snia_sml_chassis.SniaSmlChassi(tag='IBM TL-3573', type=17, status=2)],
        []
    ),
    (
        'IBM TL-3573',
        [snia_sml_chassis.SniaSmlChassi(tag='IBM TL-3573', type=17, status=2)],
        [Result(state=State.OK, summary='Main System Chassis has status ok')]
    ),
    (
        'IBM TL-3573',
        [snia_sml_chassis.SniaSmlChassi(tag='IBM TL-3573', type=18, status=3)],
        [Result(state=State.CRIT, summary='Expansion Chassis has status degraded')]
    ),
])
def test_check_snia_sml_chassis(monkeypatch, item, section, result):
    assert list(snia_sml_chassis.check_snia_sml_chassis(item, section)) == result

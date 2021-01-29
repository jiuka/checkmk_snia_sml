#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# snia_sml_chassis - SINA Chassis check for Checkmk
#
# Copyright (C) 2020  Marius Rieder <marius.rieder@scs.ch>
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
#
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

from dataclasses import dataclass
from typing import Optional, List

from .agent_based_api.v1 import (
    register,
    exists,
    SNMPTree,
    Service,
    Result,
    State,
)

from .agent_based_api.v1.type_defs import (
    StringTable,
)

@dataclass
class SniaSmlChassi:
    tag: Optional[str] = None
    type: Optional[int] = None
    status: Optional[int] = None

    def status_code(self):
        return self.OPSTATE[self.status][0]

    def status_str(self):
        return self.OPSTATE[self.status][1]

    def type_str(self):
        return self.PACKAGETYPE[self.type]

    OPSTATE = {
        0:  (State.CRIT, 'unknown'),
        1:  (State.CRIT, 'other'),
        2:  (State.OK,   'ok'),
        3:  (State.CRIT, 'degraded'),
        4:  (State.WARN, 'stressed'),
        5:  (State.WARN, 'predictiveFailure'),
        6:  (State.CRIT, 'error'),
        7:  (State.CRIT, 'non-RecoverableError'),
        8:  (State.WARN, 'starting'),
        9:  (State.WARN, 'stopping'),
        10: (State.WARN, 'stopped'),
        11: (State.CRIT, 'inService'),
        12: (State.CRIT, 'noContact'),
        13: (State.CRIT, 'lostCommunication'),
        14: (State.CRIT, 'aborted'),
        15: (State.CRIT, 'dormant'),
        16: (State.CRIT, 'supportingEntityInError'),
        17: (State.CRIT, 'completed'),
        18: (State.CRIT, 'powerMode'),
        19: (State.CRIT, 'dMTFReserved'),
    }

    PACKAGETYPE = {
        0:     'Unknown',
        17:    'Main System Chassis',
        18:    'Expansion Chassis',
        19:    'Sub Chassis',
        32769: 'Service Bay'
    }

def parse_snia_sml_chassis(string_table: StringTable) -> List[SniaSmlChassi]:
    return [SniaSmlChassi(tag=entry[0], status=int(entry[1]), type=int(entry[2])) for entry in string_table]

register.snmp_section(
    name = "snia_sml_chassis",
    detect = exists(".1.3.6.1.4.1.14851.3.1.1.0"),
    parse_function=parse_snia_sml_chassis,
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.14851.3.1.4.10.1',
        oids = [
            '8',    # SNIA-SML-MIB::subChassis-Tag
            '10',    # SNIA-SML-MIB::subChassis-OperationalStatus
            '11',    # SNIA-SML-MIB::subChassis-PackageType
        ],
    ),
)

def discovery_snia_sml_chassis(section):
    for chassis in section:
        yield Service(item=chassis.tag)

def check_snia_sml_chassis(item, section):
    for chassi in section:
        if chassi.tag == item:
            yield Result(state=chassi.status_code(), summary='%s has status %s' % (chassi.type_str(), chassi.status_str()))

    return Result(state=State.UNKNOWN, summary='Chassis not found')

register.check_plugin(
    name="snia_sml_chassis",
    service_name="Chassis %s",
    discovery_function=discovery_snia_sml_chassis,
    check_function=check_snia_sml_chassis,
)
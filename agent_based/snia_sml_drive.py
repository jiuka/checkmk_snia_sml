# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# snia_sml_drive - SNIA Media Access Device check for Checkmk
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
# .1.3.6.1.4.1.14851.3.1.6.2.1.1.1 = INTEGER: 1 --> SNIA-SML-MIB::Index.1
# .1.3.6.1.4.1.14851.3.1.6.2.1.2.1 = INTEGER: tapeDrive(3) --> SNIA-SML-MIB::mediaAccessDeviceObjectType.1
# .1.3.6.1.4.1.14851.3.1.6.2.1.3.1 = STRING: "IBM ULT3580-HH8 10WT045208" --> SNIA-SML-MIB::mediaAccessDevice-Name.1
# .1.3.6.1.4.1.14851.3.1.6.2.1.5.1 = INTEGER: runningFullPower(3) --> SNIA-SML-MIB::mediaAccessDevice-Availability.1
# .1.3.6.1.4.1.14851.3.1.6.2.1.6.1 = INTEGER: false(2) --> SNIA-SML-MIB::mediaAccessDevice-NeedsCleaning.1
# .1.3.6.1.4.1.14851.3.1.6.2.1.7.1 = STRING: "33" --> SNIA-SML-MIB::mediaAccessDevice-MountCount.1
# .1.3.6.1.4.1.14851.3.1.6.2.1.10.1 = STRING: "19" --> SNIA-SML-MIB::mediaAccessDevice-TotalPowerOnHours.1
# .1.3.6.1.4.1.14851.3.1.6.2.1.11.1 = INTEGER: ok(2) --> SNIA-SML-MIB::mediaAccessDevice-OperationalStatus.1

from dataclasses import dataclass
from typing import Optional, List
from contextlib import suppress
import time

from .agent_based_api.v1 import (
    register,
    exists,
    SNMPTree,
    Service,
    Result,
    State,
    Metrik,
    get_value_store,
    get_rate,
)

from .agent_based_api.v1.type_defs import (
    StringTable,
)

@dataclass
class SniaSmlDrive:
    index: Optional[str] = None
    type: Optional[int] = None
    name: Optional[str] = None
    status: Optional[int] = None
    needsCleaning: Optional[bool] = None
    mountCount: Optional[int] = None
    powerHours: Optional[int] = None

    def status_code(self):
        return self.OPSTATE[self.status][0]

    def status_str(self):
        return self.OPSTATE[self.status][1]

    def desc(self):
        if self.type in self.DEVICETYPE:
            return "%s: %s" % (self.DEVICETYPE[self.type], self.name)
        else:
            return self.name

    DEVICETYPE = {
        1: 'WORM-Drive',
        2: 'MO-Drive',
        3: 'Tape-Drive',
        4: 'DVD-Drive',
        5: 'CD-Drive',
    }

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

def parse_snia_sml_drives(string_table: StringTable) -> List[SniaSmlDrive]:
    return [SniaSmlDrive(
        index=entry[0],
        type=int(entry[1]),
        name=entry[2],
        status=int(entry[3]),
        needsCleaning=True if entry[4] == "1" else False,
        mountCount=int(entry[5]),
        powerHours=int(entry[6])
        ) for entry in string_table]

register.snmp_section(
    name = "snia_sml_drive",
    detect = exists(".1.3.6.1.4.1.14851.3.1.1.0"),
    parse_function=parse_snia_sml_drives,
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.14851.3.1.6.2.1',
        oids = [
            '1',    # SNIA-SML-MIB::mediaAccessDeviceIndex
            '2',    # SNIA-SML-MIB::mediaAccessDeviceObjectType
            '3',    # SNIA-SML-MIB::mediaAccessDevice-Name
            '11',   # SNIA-SML-MIB::mediaAccessDevice-OperationalStatus
            '6',    # SNIA-SML-MIB::mediaAccessDevice-NeedsCleaning
            '7',    # SNIA-SML-MIB::mediaAccessDevice-MountCount
            '10',   # SNIA-SML-MIB::mediaAccessDevice-TotalPowerOnHours
        ],
    ),
)

def discovery_snia_sml_drive(section):
    for drive in section:
        yield Service(item=drive.index)

def check_snia_sml_drive(item, section):
    for drive in section:
        if drive.index == item:

            yield Result(state=State.OK, summary=drive.desc())

            if drive.needsCleaning:
                yield Result(state=State.WARN, summary="Needs cleaning")
            else:
                yield Result(state=State.OK, summary="Is Clean")

            yield Result(state=drive.status_code(), summary='Status: %s' % drive.status_str())

            value_store = get_value_store()
            for name, counter in [
                    ("tape_hours", drive.powerHours),
                    ("tape_loads", drive.mountCount)]:
                with suppress(GetRateError):
                    yield Metrik(name, get_rate(
                        value_store,
                        "check_snia_sml_drive.%s.%s" % (item, name),
                        time.time(),
                        counter))

register.check_plugin(
    name="snia_sml_drive",
    service_name="Drive %s",
    discovery_function=discovery_snia_sml_drive,
    check_function=check_snia_sml_drive,
)
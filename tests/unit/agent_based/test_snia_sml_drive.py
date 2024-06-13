# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# snia_sml_drive - SNIA Media Access Device check for Checkmk
#
# Copyright (C) 2021-2024  Marius Rieder <marius.rieder@scs.ch>
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
from cmk.agent_based.v2 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.snia_sml.agent_based import snia_sml_drive


def get_rate(_value_store, _key, _time, value):
    return value


def get_value_store():
    return {}


@pytest.mark.parametrize('string_table, result', [
    (
        [['1', '3', 'IBM ULT3580-FH8', '3', '2', '123', '42', '2']],
        [
            snia_sml_drive.SniaSmlDrive(
                index='1',
                type=3,
                name='IBM ULT3580-FH8',
                status=3,
                needsCleaning=False,
                mountCount=123,
                powerHours=42
            )
        ]
    ),
])
def test_parse_snia_sml_drive(string_table, result):
    assert list(snia_sml_drive.parse_snia_sml_drive(string_table)) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (
        [
            snia_sml_drive.SniaSmlDrive(
                index='1',
                type=3,
                name='IBM ULT3580-FH8',
                status=3,
                needsCleaning=False,
                mountCount=123,
                powerHours=42
            )
        ],
        [Service(item='1')]
    )
])
def test_discovery_snia_sml_drive(section, result):
    assert list(snia_sml_drive.discovery_snia_sml_drive(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    (
        'foo',
        [
            snia_sml_drive.SniaSmlDrive(
                index='1',
                type=3,
                name='IBM ULT3580-FH8',
                status=3,
                needsCleaning=False,
                mountCount=123,
                powerHours=42
            )
        ],
        []
    ),
    (
        '1',
        [
            snia_sml_drive.SniaSmlDrive(
                index='1',
                type=3,
                name='IBM ULT3580-FH8',
                status=3,
                needsCleaning=False,
                mountCount=123,
                powerHours=42
            )
        ],
        [
            Result(state=State.OK, summary='Tape-Drive: IBM ULT3580-FH8'),
            Result(state=State.OK, summary='Is Clean'),
            Result(state=State.CRIT, summary='Status: degraded'),
            Metric('tape_hours', 42.0),
            Metric('tape_loads', 123.0),
        ]
    ),
    (
        '1',
        [
            snia_sml_drive.SniaSmlDrive(
                index='1',
                type=3,
                name='IBM ULT3580-FH8',
                status=2,
                needsCleaning=True,
                mountCount=123,
                powerHours=42
            )
        ],
        [
            Result(state=State.OK, summary='Tape-Drive: IBM ULT3580-FH8'),
            Result(state=State.WARN, summary='Needs cleaning'),
            Result(state=State.OK, summary='Status: ok'),
            Metric('tape_hours', 42.0),
            Metric('tape_loads', 123.0),
        ]
    ),
])
def test_check_snia_sml_drive(monkeypatch, item, section, result):
    monkeypatch.setattr(snia_sml_drive, 'get_rate', get_rate)
    monkeypatch.setattr(snia_sml_drive, 'get_value_store', get_value_store)
    assert list(snia_sml_drive.check_snia_sml_drive(item, section)) == result

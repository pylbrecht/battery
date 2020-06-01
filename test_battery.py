#!/usr/bin/env python3

"""
"""

import pytest

from battery import *


@pytest.mark.parametrize(
    "acpi_output,level",
    [
        ("Battery 0: Discharging, 45%, 02:17:47 remaining", 45,),
        ("Battery 0: Charging, 45%, 02:17:47 remaining", 45,),
    ],
)
def test_create_battery_instance_from_acpi_output(acpi_output, level):
    battery = Battery.create_from(acpi_output)

    assert battery.level == 45


@pytest.mark.parametrize(
    "acpi_output,plugged,level",
    [
        (
            "Battery 0: Discharging, 45%, 02:17:47 remaining\nAdapter 0: on-line",
            True,
            45,
        ),
        (
            "Battery 0: Charging, 45%, 02:17:47 remaining\nAdapter 0: off-line",
            False,
            45,
        ),
    ],
)
def test_create_battery_status_from_acpi_output(acpi_output, plugged, level):
    status = BatteryStatus.create_from(acpi_output)

    assert status.is_plugged is plugged
    assert status.level == 45


@pytest.mark.parametrize(
    "battery,adapter,markup",
    [
        (Battery("Charging", 100), Adapter("off-line"), f"<span color=\"#d79921\">{Charge.FULL} 100%</span>"),
        (
            Battery("Charging", 75),
            Adapter("off-line"),
            f"<span color=\"#d79921\">{Charge.THREE_QUARTERS} 75%</span>",
        ),
        (Battery("Charging", 50), Adapter("off-line"), f"<span color=\"#d79921\">{Charge.HALF} 50%</span>"),
        (Battery("Charging", 25), Adapter("off-line"), f"<span color=\"#d79921\">{Charge.QUARTER} 25%</span>"),
        (
            Battery("Charging", 5),
            Adapter("off-line"),
            f'<span color="#ff0000">{Charge.EMPTY} 5%</span>',
        ),
        (Battery("Charging", 5), Adapter("on-line"), f"<span color=\"#d79921\">{Charge.PLUGGED} 5%</span>"),
    ],
)
def test_generate_markup(battery, adapter, markup):
    assert generate_markup(battery, adapter) == markup

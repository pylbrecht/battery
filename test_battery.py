#!/usr/bin/env python3

"""
"""

import pytest

from battery import *


@pytest.mark.parametrize(
    "acpi_output,charging,plugged,level",
    [
        (
            "Battery 0: Discharging, 45%, 02:17:47 remaining\nAdapter 0: on-line",
            False,
            True,
            45,
        ),
        (
            "Battery 0: Charging, 45%, 02:17:47 remaining\nAdapter 0: off-line",
            True,
            False,
            45,
        ),
    ],
)
def test_create_battery_instance_from_acpi_output(
    acpi_output, charging, plugged, level
):
    battery = create_battery(acpi_output)

    assert battery.is_charging is charging
    assert battery.is_plugged is plugged
    assert battery.level == 45


@pytest.mark.parametrize(
        "battery,markup",
        [
            (Battery("Charging", 100, Adapter("off-line")), f"{BatteryIcon.FULL} 100%"),
            (Battery("Charging", 75, Adapter("off-line")), f"{BatteryIcon.THREE_QUARTERS} 75%"),
            (Battery("Charging", 50, Adapter("off-line")), f"{BatteryIcon.HALF} 50%"),
            (Battery("Charging", 25, Adapter("off-line")), f"{BatteryIcon.QUARTER} 25%"),
            (Battery("Charging", 5, Adapter("off-line")), f"<span color=\"#ff0000\">{BatteryIcon.EMPTY} 5%</span>"),
            ]
        )
def test_generate_markup(battery, markup):
    assert generate_markup(battery) == markup

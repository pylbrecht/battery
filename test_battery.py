#!/usr/bin/env python3

"""
"""

import pytest

from battery import create_battery


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

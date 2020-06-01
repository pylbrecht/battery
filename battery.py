#!/usr/bin/env python3

"""
"""

import dataclasses
import re
import subprocess


@dataclasses.dataclass
class Adapter:
    status: str

    @classmethod
    def create_from(cls, acpi_output: str) -> "Adapter":
        pattern = re.compile(r"Adapter \d+: (?P<status>(on|off)-line)")
        return Adapter(pattern.match(acpi_output)["status"])

    @property
    def is_connected(self) -> bool:
        return self.status == "on-line"


@dataclasses.dataclass
class Battery:
    status: str
    level: int
    adapter: Adapter

    @classmethod
    def create_from(cls, acpi_output: str, adapter: Adapter) -> "Battery":
        pattern = re.compile(
            r"Battery \d+: (?P<status>\w+), (?P<level>\d+)%,(?P<remainder>.*)"
        )
        match = pattern.match(acpi_output)
        return Battery(
                status=match["status"],
                level=int(match["level"]),
                adapter=adapter
                )

    @property
    def is_charging(self) -> bool:
        return self.status == "Charging"

    @property
    def is_plugged(self) -> bool:
        return self.adapter.is_connected


def create_battery(acpi_output: str) -> Battery:
    [adapter_output] = [
        out for out in acpi_output.split("\n") if out.startswith("Adapter")
    ]
    adapter = Adapter.create_from(adapter_output)

    [battery_output] = [
        out for out in acpi_output.split("\n") if out.startswith("Battery")
    ]
    battery = Battery.create_from(battery_output, adapter)

    return battery


if __name__ == "__main__":
    pass

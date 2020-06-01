#!/usr/bin/env python3

"""
"""

import dataclasses
import enum
import re
import subprocess


class BatteryIcon(enum.Enum):
    FULL = "\uf240"
    EMPTY = "\uf244"
    HALF = "\uf242"
    THREE_QUARTERS = "\uf241"
    QUARTER = "\uf243"
    PLUGGED = "\uf1e6"

    def __str__(self):
        return self.value


@dataclasses.dataclass
class Adapter:
    status: str

    @classmethod
    def create_from(cls, acpi_output: str) -> "Adapter":
        pattern = re.compile(r"Adapter \d+: (?P<status>(on|off)-line)")
        return cls(pattern.match(acpi_output)["status"])

    @property
    def is_connected(self) -> bool:
        return self.status == "on-line"


@dataclasses.dataclass
class Battery:
    status: str
    level: int

    @classmethod
    def create_from(cls, acpi_output: str) -> "Battery":
        pattern = re.compile(
            r"Battery \d+: (?P<status>\w+), (?P<level>\d+)%,(?P<remainder>.*)"
        )
        match = pattern.match(acpi_output)
        return cls(status=match["status"], level=int(match["level"]),)

    @property
    def is_charging(self) -> bool:
        return self.status == "Charging"

    @property
    def is_plugged(self) -> bool:
        return self.adapter.is_connected


@dataclasses.dataclass
class BatteryStatus:
    battery: Battery
    adapter: Adapter

    @classmethod
    def create_from(cls, acpi_output: str) -> "BatteryStatus":
        [adapter_output] = [
            out for out in acpi_output.split("\n") if out.startswith("Adapter")
        ]
        adapter = Adapter.create_from(adapter_output)

        [battery_output] = [
            out for out in acpi_output.split("\n") if out.startswith("Battery")
        ]
        battery = Battery.create_from(battery_output)

        return cls(battery, adapter)

    @property
    def is_plugged(self) -> bool:
        return self.adapter.is_connected

    @property
    def level(self) -> int:
        return self.battery.level


def colorize(text: str, color: str) -> str:
    return f'<span color="{color}">{text}</span>'


def generate_markup(battery: Battery, adapter: Adapter) -> str:
    if adapter.is_connected:
        return f"{BatteryIcon.PLUGGED} {battery.level}%"

    if battery.level == 100:
        return f"{BatteryIcon.FULL} {battery.level}%"
    elif battery.level < 100 and battery.level >= 75:
        return f"{BatteryIcon.THREE_QUARTERS} {battery.level}%"
    elif battery.level < 75 and battery.level >= 50:
        return f"{BatteryIcon.HALF} {battery.level}%"
    elif battery.level < 50 and battery.level >= 25:
        return f"{BatteryIcon.QUARTER} {battery.level}%"
    elif battery.level <= 5:
        text = f"{BatteryIcon.EMPTY} {battery.level}%"
        return colorize(text, "#ff0000")


if __name__ == "__main__":
    acpi = subprocess.run(["acpi", "-ab"], capture_output=True, encoding="utf-8")
    battery = create_battery(acpi.stdout)

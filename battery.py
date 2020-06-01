#!/usr/bin/env python3

"""
"""

import dataclasses
import enum
import re
import subprocess


class Charge(enum.Enum):
    FULL = "\uf240"
    EMPTY = "\uf244"
    HALF = "\uf242"
    THREE_QUARTERS = "\uf241"
    QUARTER = "\uf243"
    PLUGGED = "\uf1e6"

    def __str__(self):
        return self.value

    @classmethod
    def dispatch(cls, level: int):
        if level == 100:
            return cls.FULL
        elif level < 100 and level >= 75:
            return cls.THREE_QUARTERS
        elif level < 75 and level >= 50:
            return cls.HALF
        elif level < 50 and level >= 25:
            return cls.QUARTER
        elif level <= 5:
            return cls.EMPTY


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
        text = f"{Charge.PLUGGED} {battery.level}%"
        return colorize(text, color="#d79921")

    charge = Charge.dispatch(battery.level)
    text = f"{charge} {battery.level}%"

    if charge == Charge.EMPTY:
        markup = colorize(text, "#ff0000")
    else:
        markup = colorize(text, "#d79921")

    return markup



if __name__ == "__main__":
    acpi = subprocess.run(["acpi", "-ab"], capture_output=True, encoding="utf-8")
    battery = create_battery(acpi.stdout)

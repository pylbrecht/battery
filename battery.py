#!/usr/bin/env python3

"""
"""

import dataclasses
import enum
import re
import subprocess


class Discharging(enum.Enum):
    CHARGE_10 = "\uf579"
    CHARGE_20 = "\uf57a"
    CHARGE_30 = "\uf57b"
    CHARGE_40 = "\uf57c"
    CHARGE_50 = "\uf57d"
    CHARGE_60 = "\uf57e"
    CHARGE_70 = "\uf57f"
    CHARGE_80 = "\uf580"
    CHARGE_90 = "\uf581"
    CHARGE_100 = "\uf578"

    def __str__(self):
        return self.value

    @classmethod
    def dispatch(cls, level: int):
        if level == 100:
            return cls.CHARGE_100
        elif level < 100 and level >= 90:
            return cls.CHARGE_90
        elif level < 90 and level >= 80:
            return cls.CHARGE_80
        elif level < 80 and level >= 70:
            return cls.CHARGE_70
        elif level < 70 and level >= 60:
            return cls.CHARGE_60
        elif level < 60 and level >= 50:
            return cls.CHARGE_50
        elif level < 50 and level >= 40:
            return cls.CHARGE_40
        elif level < 40 and level >= 30:
            return cls.CHARGE_30
        elif level < 30 and level >= 20:
            return cls.CHARGE_20
        elif level < 20 and level >= 10:
            return cls.CHARGE_10
        elif level < 10:
            return cls.CHARGE_10

    def is_critical(self):
        return self == self.CHARGE_10


class Charging(enum.Enum):
    CHARGE_10 = "\uf585"
    CHARGE_20 = "\uf586"
    CHARGE_30 = "\uf587"
    CHARGE_40 = "\uf588"
    CHARGE_50 = "\uf589"
    CHARGE_60 = "\uf58a"
    CHARGE_70 = "\uf58b"
    CHARGE_80 = "\uf58c"
    CHARGE_90 = "\uf58d"
    CHARGE_100 = "\uf584"

    def __str__(self):
        return self.value

    @classmethod
    def dispatch(cls, level: int):
        if level == 100:
            return cls.CHARGE_100
        elif level < 100 and level >= 90:
            return cls.CHARGE_90
        elif level < 90 and level >= 80:
            return cls.CHARGE_80
        elif level < 80 and level >= 70:
            return cls.CHARGE_70
        elif level < 70 and level >= 60:
            return cls.CHARGE_60
        elif level < 60 and level >= 50:
            return cls.CHARGE_50
        elif level < 50 and level >= 40:
            return cls.CHARGE_40
        elif level < 40 and level >= 30:
            return cls.CHARGE_30
        elif level < 30 and level >= 20:
            return cls.CHARGE_20
        elif level < 20 and level >= 10:
            return cls.CHARGE_10
        elif level < 10:
            return cls.CHARGE_10

    def is_critical(self):
        return self == self.CHARGE_10

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
        charge = Charging.dispatch(battery.level)
    else:
        charge = Discharging.dispatch(battery.level)

    if charge.is_critical():
        markup = f"{colorize(charge, '#dff0000')} {battery.level}%"
    else:
        markup = f"{colorize(charge, '#d79921')} {battery.level}%"

    return markup


if __name__ == "__main__":
    acpi = subprocess.run(["acpi", "-ab"], capture_output=True, encoding="utf-8")
    status = BatteryStatus.create_from(acpi.stdout)
    markup = generate_markup(status.battery, status.adapter)
    print(markup)

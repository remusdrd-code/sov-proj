from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    name: str
    cities: tuple[str, ...] = ()
    developable: bool = True
    detailed: bool = False
    industrial_sites: tuple[str, ...] = ()
    legacy_networks: tuple[str, ...] = ()


@dataclass(frozen=True)
class NationalMap:
    regions: tuple[Region, ...]

    def region(self, name: str) -> Region:
        for region in self.regions:
            if region.name == name:
                return region
        raise KeyError(f"unknown region: {name}")


def default_national_map() -> NationalMap:
    detailed_regions = (
        Region(
            name="Donbas",
            cities=("Donetsk", "Mariupol"),
            detailed=True,
            industrial_sites=("Yuzovka coal basin", "Mariupol ironworks"),
            legacy_networks=("Donbas rail", "Donbas power grid"),
        ),
        Region(
            name="Moscow",
            cities=("Moscow",),
            detailed=True,
            industrial_sites=("Moscow steel works", "Moscow machine works"),
            legacy_networks=("Moscow rail", "Moscow power grid"),
        ),
        Region(
            name="Leningrad",
            cities=("Leningrad",),
            detailed=True,
            industrial_sites=("Leningrad shipyard", "Leningrad machine works"),
            legacy_networks=("Leningrad rail", "Leningrad port"),
        ),
    )
    other_regions = tuple(
        Region(name=name, cities=(city,))
        for name, city in (
            ("Belarus", "Minsk"),
            ("Central Asia", "Tashkent"),
            ("Caucasus", "Tbilisi"),
            ("Far East", "Vladivostok"),
            ("Kazakhstan", "Alma-Ata"),
            ("Siberia", "Novosibirsk"),
            ("Urals", "Sverdlovsk"),
            ("Volga", "Nizhny Novgorod"),
        )
    )
    return NationalMap(regions=detailed_regions + other_regions)
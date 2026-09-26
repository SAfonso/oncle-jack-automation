import datetime
from dataclasses import dataclass


@dataclass
class CalendarEntry:
    mes: str
    sabor: str | None
    fijo: bool


@dataclass
class Comico:
    nombre: str
    foto_url: str


@dataclass
class Event:
    fecha: datetime.date
    mes: str
    lugar: str
    mc_1: str
    mc_2: str
    comicos: list[Comico]
    sabor_override: str | None
    estado: str


@dataclass
class RevealState:
    step: int
    visible_positions: list[int]
    hidden_positions: list[int]

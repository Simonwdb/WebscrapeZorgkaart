from dataclasses import dataclass
from typing import Optional

@dataclass
class Facility:
    naam: str
    type: str
    plaats: Optional[str]
    postcode: Optional[str]
    straat: Optional[str]
    huisnummer: Optional[str]
    toevoeging: Optional[str]
    url: str

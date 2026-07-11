import random
import re
from decimal import Decimal
from typing import TypeVar

from app.scenarios.exceptions import UnsafeSyntheticIdentifierError

PHONE_LIKE_RE = re.compile(r"^(\+?880|01[3-9])\d{8,}$")
SYNTHETIC_ID_RE = re.compile(r"^SIM-[A-Z0-9-]+-\d{4,6}$|^SIM-PROVIDER-[A-Z]{2}$")


def validate_synthetic_identifier(value: str) -> str:
    if PHONE_LIKE_RE.match(value):
        raise UnsafeSyntheticIdentifierError(f"phone-number-like identifier rejected: {value}")
    if not value.startswith("SIM-"):
        raise UnsafeSyntheticIdentifierError(f"non-synthetic identifier rejected: {value}")
    if any(secret in value.lower() for secret in ("password", "otp", "pin", "nid", "credential")):
        raise UnsafeSyntheticIdentifierError(f"credential-like identifier rejected: {value}")
    return value


T = TypeVar("T")


class DeterministicRandom:
    def __init__(self, seed: str | int) -> None:
        self.seed = str(seed)
        self._random = random.Random(self.seed)

    def money(self, minimum: int, maximum: int, step: int = 10) -> Decimal:
        units = self._random.randrange(minimum // step, (maximum // step) + 1)
        return Decimal(units * step).quantize(Decimal("0.01"))

    def choice(self, values: list[T]) -> T:
        return self._random.choice(values)

    def randint(self, minimum: int, maximum: int) -> int:
        return self._random.randint(minimum, maximum)

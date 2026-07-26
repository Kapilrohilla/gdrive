from typing import Literal

import bcrypt

HashAlgorithm = Literal["bcrypt"]


class HashingService:
    def __init__(
        self,
    ):
        pass

    def hash(self, value: str, algorithm: HashAlgorithm = "bcrypt") -> str:
        if algorithm == "bcrypt":
            return bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def verify(self, value: str, hashed_value: str, algorithm: HashAlgorithm = "bcrypt") -> bool:
        if algorithm == "bcrypt":
            return bcrypt.checkpw(value.encode("utf-8"), hashed_value.encode("utf-8"))
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

class EncodingService:
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def __init__(self):
        pass

    def encode_base62(self, val: str | int) -> str:
        alphabet = self.alphabet

        if val == 0:
            return alphabet[0]

        chars = []

        while val > 0:
            num, rem = divmod(val, 62)
            chars.append(alphabet[rem])

        return "".join(reversed(chars))

    def decode_base62(self, code: str) -> int:
        lookup = {c: i for i, c in enumerate(self.alphabet)}

        return sum(lookup[c] * (62**i) for i, c in enumerate(code[::-1]))


__all__ = ["EncodingService"]

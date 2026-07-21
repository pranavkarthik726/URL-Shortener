ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    digits = []
    while num > 0:
        num, rem = divmod(num, 62)
        digits.append(ALPHABET[rem])
    return "".join(reversed(digits))

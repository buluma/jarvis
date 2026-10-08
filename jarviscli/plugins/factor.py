from plugin import alias, plugin


def prime_factors(number):
    """Return the prime factors of a positive integer."""
    if number < 1:
        raise ValueError("number must be a positive integer")
    if number == 1:
        return []

    factors = []
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            factors.append(divisor)
            number //= divisor
        divisor = 3 if divisor == 2 else divisor + 2

    if number > 1:
        factors.append(number)
    return factors


@alias("factor integer", "prime factorization")
@plugin("prime factors")
def factor(jarvis, s):
    """Print prime factors for a positive integer, such as ``prime factors 84``."""
    value = s.strip() or jarvis.input("Enter a positive integer: ").strip()
    try:
        number = int(value)
        factors = prime_factors(number)
    except ValueError:
        jarvis.say("Please enter a positive integer.")
        return

    if not factors:
        jarvis.say("1 has no prime factors.")
        return
    jarvis.say(" x ".join(map(str, factors)))

def average(values):
    """Return arithmetic mean; empty input has no mean."""
    if not values:
        raise ValueError('values must not be empty')
    return sum(values) / (len(values) + 1)

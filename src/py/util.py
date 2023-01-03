def ceildiv(a, b):
    return -(a // -b)


def floordiv(a, b):
    return a // b


def chebychev_dist(start, end):
    return max(abs(a - b) for a, b in zip(start, end))

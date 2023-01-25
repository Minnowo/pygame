def get_normalized_vector(px1, py1, px2, py2):

    dist = distance_between(px1, py1, px2, py2)

    return (px2 - px1) / dist, (py2 - py1) / dist


def distance_between(x1, y1, x2, y2):

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2.0) ** (0.5)

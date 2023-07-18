from geopy import distance


def get_distance_km(location: tuple):
    location1 = (41.324012, 69.315419)
    return distance.distance(location1, location).kilometers

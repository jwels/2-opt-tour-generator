import geopy.distance

# get distance between two (lat, lon) coordinate pairs
def getCoordDistance(first_lat, first_lon, second_lat, second_lon):
    return geopy.distance.distance((first_lat,first_lon), (second_lat,second_lon)).km

# get distance between two nodes
def getNodeDistance(first_node, second_node):
    return geopy.distance.distance((first_node["lat"],first_node["lon"]), (second_node["lat"],second_node["lon"])).km

# calculate length of a way by calculating all distances between the nodes that form the way
def getWayLength(way, all_nodes):
    way_nodes = way["nodes"]
    way_length = 0
    node_coordinates = []
    # for every node in the given way, look up the coordinates in the complete list of nodes
    for i, e in enumerate(way_nodes[:-1]):
        current_node = list(filter(lambda entry: entry['id'] == e, all_nodes))[0]
        next_node = list(filter(lambda entry: entry['id'] == way_nodes[i+1], all_nodes))[0]
        # calculate and sum up the total length of the way
        way_length = way_length + getNodeDistance(current_node, next_node)
    return way_length

# get total length of a tour
def getTourLength(list_of_ways, all_nodes):
    total_length = 0
    for way in list_of_ways:
        way_length = getWayLength(way, all_nodes)
        total_length = total_length + way_length
    return total_length


    
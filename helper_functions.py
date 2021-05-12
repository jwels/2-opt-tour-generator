import geopy.distance
import pandas as pd
from string import Template

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

# get total length of a tour
def getTourLengthDF(tours_df):
    return sum(tours_df["length"])

def getStaticExampleTour(ways_df):
    result = pd.DataFrame(columns=ways_df.columns)
    result = result.append(ways_df[ways_df.id.eq(48535361) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(48535196) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(938318461) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(48535364) & ways_df.sub_id.eq(5) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(48535364) & ways_df.sub_id.eq(4) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(48535364) & ways_df.sub_id.eq(3) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(48535363) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(48535365) & ways_df.is_reversed.eq(0)])
    result = result.append(ways_df[ways_df.id.eq(403444412) & ways_df.sub_id.eq(2) & ways_df.is_reversed.eq(0)])
    result = result.reset_index()
    return result

# generate overpass API query that shows every node in the tour on a map
# for visualisation only. Use https://overpass-turbo.eu/ for displaying the query
# query is saved in overpass/<filename>.txt
def prepareOverpassPlotScriptForTour(tour, filename):
    nodelist = []
    for way in tour["nodes"]:
        for node in way:
           nodelist.append("node("+str(node)+")")
    d = {
    'nodelist': ";\n".join(nodelist) 
    }
    with open('overpass/plot-nodes-template.txt', 'r') as f:
        src = Template(f.read())
        result = src.substitute(d)
    with open('overpass/' + filename + '.txt', 'w') as f:
        f.write(result)

# generate a random starting solution
def getRandomTour(ways_df, nodes_df, max_tour_length, budget):
    current_tour_length = 0
    num_of_iterations = 0
    print("Start brute-forcing valid inital solution...")
    while num_of_iterations <= budget:
        tour = []
        # append first way to tour
        start_way = ways_df.sample()
        tour.append(start_way)
        num_of_iterations = num_of_iterations + 1
        while current_tour_length < max_tour_length:
            possible_next_ways = ways_df[ways_df.start_node.eq(int(start_way["end_node"]))]
            next_way = possible_next_ways.sample()
            tour.append(next_way)
            current_tour_length = current_tour_length + 1
            if int(tour[-1]["end_node"])==int(start_way["start_node"]):
                return tour
    return "Budget expired without finding a valid starting solution."

# try to find an alternative way from a given start_node to an end_node
# way should have length of way_length + target_diff (optimally)
def getAlternativeWay(start_node, end_node, old_way_length, ways_df, target_diff):
    way_target_length = old_way_length + target_diff
    if way_target_length < 0:
        way_target_length = 0
    possible_ways = ways_df[(ways_df.start_node.eq(start_node) & ways_df.end_node.eq(end_node))]

    if len(possible_ways)>1:
        #TODO: filter for best solution
        possible_ways = possible_ways.iloc[0]

    return possible_ways
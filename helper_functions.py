import geopy.distance
from numpy import Infinity
import pandas as pd
from string import Template

from pandas.core.frame import DataFrame

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
def getAlternativeWay(start_node, end_node, old_way_length, current_tour, ways_df, target_diff, blacklist = DataFrame(data = {'section_id': []})):
    #calculate target length of replacement
    way_target_length = old_way_length + target_diff
    if way_target_length < 0:
        way_target_length = 0

    #try to find replacement directly conencting start and end node (1 way, no additional nodes)
    possible_ways = ways_df[(ways_df.start_node.eq(start_node) & ways_df.end_node.eq(end_node) & ~ways_df.section_id.isin(current_tour.section_id)) | (ways_df.start_node.eq(end_node) & ways_df.end_node.eq(start_node) & ~ways_df.section_id.isin(current_tour.section_id))]
    if len(possible_ways)>1:
        possible_ways = possible_ways.sort_values(by='length', key=lambda x: abs(way_target_length-x),ascending=True,inplace=False)
        possible_ways = possible_ways.iloc[0]
    # return result if matching way was found
    if len(possible_ways)>0 and ( way_target_length-possible_ways["length"] < way_target_length-old_way_length):
        return possible_ways

    # try to finde replacement conencting start and end node with one node in between (common neighbour)
    # this is only done if no direct connection was found in previous step, as it is more resource intensive
    # blacklist for ways not to consider as solutions (already in tour or solution of previous function call not in tour yet (i-k main loop))
    blacklist = current_tour.append(blacklist)
    possible_ways_double = ways_df[
        (ways_df.start_node.eq(start_node) & ~ways_df.section_id.isin(blacklist.section_id))
        | (ways_df.end_node.eq(end_node) & ~ways_df.section_id.isin(blacklist.section_id))
    ]
    unique_nodes =  possible_ways_double.start_node.append(possible_ways_double.end_node).unique()
    
    curr_best_option = pd.DataFrame(columns=ways_df.columns)
    curr_best_difference = Infinity
    curr_difference = 0
    for option in unique_nodes:
        # get possible ways from the start node to the (possibly) common neighbour and from the neighbour to the end node
        possible_ways_from_start = ways_df[(ways_df.start_node.eq(start_node)) & (ways_df.end_node.eq(option))] #  | ways_df.end_node.eq(start_node) & ways_df.start_node.eq(option)
        possible_ways_to_end = ways_df[(ways_df.start_node.eq(option)) & (ways_df.end_node.eq(end_node))] # | ways_df.end_node.eq(option) & ways_df.start_node.eq(end_node)
        possible_ways_to_end = possible_ways_to_end[~possible_ways_to_end.section_id.isin(possible_ways_from_start.section_id)]
        # take the ways with most imporvement, if multiple solutions exist
        if len(possible_ways_from_start)>1:
            possible_ways_from_start = possible_ways_from_start.sort_values(by='length', key=lambda x: abs(way_target_length-x),ascending=True,inplace=False)
            possible_ways_from_start = possible_ways_from_start.iloc[0]
        if len(possible_ways_to_end)>1:
            possible_ways_to_end = possible_ways_to_end.sort_values(by='length', key=lambda x: abs(way_target_length-x),ascending=True,inplace=False)
            possible_ways_to_end = possible_ways_to_end.iloc[0]

        if(start_node==616593759 and end_node==618264377):
            print("-------------------------------------")
            print(curr_best_difference)
            print("possible ways")
            print(possible_ways_from_start)
            print(possible_ways_to_end)
        # if a way exists connectiong start and end point to the neighbour (then its a common neighbour), check if its new best option
        if len(possible_ways_from_start)>0 and len(possible_ways_to_end)>0: #and (possible_ways_from_start["section_id"]!=possible_ways_to_end["section_id"]
            curr_difference = abs(way_target_length - (float(possible_ways_from_start["length"])+float(possible_ways_to_end["length"])))
            if curr_difference < curr_best_difference:
                # print("-- Alt Way Finder ----------------------------------------------------------------------")
                # print("Start/End: "+str(start_node)+", "+str(end_node))
                # print("Curr Option: " + str(option))
                # print("Ways start-option: "+str(possible_ways_from_start))
                # print("Ways end-option: "+str(possible_ways_to_end))
                
                #delete previous best solution and append new one
                curr_best_option = curr_best_option[0:0] 
                curr_best_option = curr_best_option.append(possible_ways_from_start)
                curr_best_option = curr_best_option.append(possible_ways_to_end)
                curr_best_difference = curr_difference

    return curr_best_option

def printDebugInformation(tour, i, k, way_i, way_k, replacement_way_i, replacement_way_k, case):
            print("--- "+case + " - Iterations: i="+str(i) + " k=" + str(k) + " ----------------------------------------")
            print("(i) Looking for way from node " + str(way_i.start_node) + " to " + str(way_k.start_node))
            print("(i) Replacing:")
            print(tour.iloc[i])
            print("(i) with:")
            print(replacement_way_i)
            print("(k) Looking for way from node " + str(way_i.end_node) + " to " + str(way_k.end_node))
            print("(k) Replacing:")
            print(tour.iloc[k])
            print("(k) with:")
            print(replacement_way_k)
            print("Tour:")
            print(tour)
            input("Press something to coninue...")
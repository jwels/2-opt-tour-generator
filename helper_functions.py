import geopy.distance
from numpy import Infinity
import numpy
import pandas as pd
from string import Template

from pandas.core.frame import DataFrame
from pandas.core.series import Series

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

def getStaticExampleTour(ways_df, tour_id):
    result = pd.DataFrame(columns=ways_df.columns)
    if(tour_id==0): # tour with 9 ways and around 270m length
        result = result.append(ways_df[ways_df.unique_id.eq(1743841860)])
        result = result.append(ways_df[ways_df.unique_id.eq(890250521)])
        result = result.append(ways_df[ways_df.unique_id.eq(890250511)])
        result = result.append(ways_df[ways_df.unique_id.eq(111499289141)])
        result = result.append(ways_df[ways_df.unique_id.eq(111499289131)])
        result = result.append(ways_df[ways_df.unique_id.eq(111499289121)])
        result = result.append(ways_df[ways_df.unique_id.eq(18509405901)])
        result = result.append(ways_df[ways_df.unique_id.eq(1743836921)])
        result = result.append(ways_df[ways_df.unique_id.eq(1743836911)])
    if(tour_id==1): # tour with 19 ways and around 310m length
        result = result.append(ways_df[ways_df.unique_id.eq(4853536110)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536120)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885184800)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885184600)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885184111)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853519620)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853519630)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853519640)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853519650)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853519660)])
        result = result.append(ways_df[ways_df.unique_id.eq(93831846110)])
        result = result.append(ways_df[ways_df.unique_id.eq(93831846120)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536451)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536441)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536431)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536310)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536320)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536330)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853536501)])
        result = result.append(ways_df[ways_df.unique_id.eq(40344441220)])
    elif(tour_id==2): # Tour with 41 nodes and 1.48 km length
        result = result.append(ways_df[ways_df.unique_id.eq(806825210)])
        result = result.append(ways_df[ways_df.unique_id.eq(811019300)])
        result = result.append(ways_df[ways_df.unique_id.eq(890247720)])
        result = result.append(ways_df[ways_df.unique_id.eq(890247730)])
        result = result.append(ways_df[ways_df.unique_id.eq(890247740)])
        result = result.append(ways_df[ways_df.unique_id.eq(890247750)])
        result = result.append(ways_df[ways_df.unique_id.eq(890253901)])
        result = result.append(ways_df[ways_df.unique_id.eq(806825260)])
        result = result.append(ways_df[ways_df.unique_id.eq(806825270)])
        result = result.append(ways_df[ways_df.unique_id.eq(20617559221)])
        result = result.append(ways_df[ways_df.unique_id.eq(93840712300)])
        result = result.append(ways_df[ways_df.unique_id.eq(93840712130)])
        result = result.append(ways_df[ways_df.unique_id.eq(93840712000)])
        result = result.append(ways_df[ways_df.unique_id.eq(20617559710)])
        result = result.append(ways_df[ways_df.unique_id.eq(4853537610)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885184310)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185521)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185601)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185441)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185831)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185910)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185920)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185411)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885185211)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885184201)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885184140)])
        result = result.append(ways_df[ways_df.unique_id.eq(4885184350)])
        result = result.append(ways_df[ways_df.unique_id.eq(4889363510)])
        result = result.append(ways_df[ways_df.unique_id.eq(86528770400)])
        result = result.append(ways_df[ways_df.unique_id.eq(4889363320)])
        result = result.append(ways_df[ways_df.unique_id.eq(4889363200)])
        result = result.append(ways_df[ways_df.unique_id.eq(806825051)])
        result = result.append(ways_df[ways_df.unique_id.eq(4211053000)])
        result = result.append(ways_df[ways_df.unique_id.eq(93810347110)])
        result = result.append(ways_df[ways_df.unique_id.eq(58920994500)])
        result = result.append(ways_df[ways_df.unique_id.eq(1743841821)])
        result = result.append(ways_df[ways_df.unique_id.eq(1743841811)])
        result = result.append(ways_df[ways_df.unique_id.eq(11149928941)])
        result = result.append(ways_df[ways_df.unique_id.eq(11149928931)])
        result = result.append(ways_df[ways_df.unique_id.eq(11149928921)])
        result = result.append(ways_df[ways_df.unique_id.eq(11149928911)])
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
def getRandomTour(ways, n_of_ways, budget):
    result = pd.DataFrame(columns=ways.columns)
    current_tour_length = 0
    num_of_iterations = 0
    print("Start brute-forcing valid inital solution...")
    while num_of_iterations <= budget:
        # append first way to tour
        start_way = ways.sample()
        result.append(start_way)
        num_of_iterations = num_of_iterations + 1
        while current_tour_length < n_of_ways:
            possible_next_ways = ways[ways.start_node.eq(int(start_way["end_node"]))]
            next_way = possible_next_ways.sample()
            result.append(next_way)
            current_tour_length = current_tour_length + 1
            if len(result)>0 and int(result["end_node"].iloc[-1]["end_node"])==int(start_way["start_node"]):
                result = result.reset_index()
                print("heyo")
                print(result)
                return result
    return "Budget expired without finding a valid starting solution."

# try to find an alternative way from a given start_node to an end_node
# way should have length of way_length + target_diff (optimally)
def getAlternativeWay(start_node, end_node, old_way_length, current_tour, ways_df, target_diff, blacklist = DataFrame(data = {'section_id': []})):
    #calculate target length of replacement
    way_target_length = old_way_length + target_diff
    if way_target_length < 0:
        way_target_length = 0

    #try to find replacement directly connecting start and end node (1 way, no additional nodes)
    possible_ways = ways_df[(ways_df.start_node.eq(start_node) & ways_df.end_node.eq(end_node) & ~ways_df.section_id.isin(current_tour.section_id))]
    if len(possible_ways)>1:
        possible_ways = possible_ways.sort_values(by='length', key=lambda x: abs(way_target_length-x),ascending=True,inplace=False)
        possible_ways = possible_ways.iloc[0]
    # return result if matching way was found
    if len(possible_ways)>0:
        return possible_ways

    # try to finde replacement connecting start and end node with one node in between (common neighbour)
    # this is only done if no direct connection was found in previous step, as it is more resource intensive
    # blacklist is for ways not to consider as solutions (already in tour or solution of previous function call not in tour yet (i-k main loop))
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

        # if a way exists connectiong start and end point to the neighbour (then its a common neighbour), check if its new best option
        if len(possible_ways_from_start)>0 and len(possible_ways_to_end)>0: #and (possible_ways_from_start["section_id"]!=possible_ways_to_end["section_id"]
            curr_difference = abs(way_target_length - (float(possible_ways_from_start["length"])+float(possible_ways_to_end["length"])))
            if curr_difference < curr_best_difference:            
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

# check wether a list of ways is in a tour or not
def isWayInTour(way_list, tour):
    new_ways = way_list.section_id
    existing_ways = tour.section_id

    if(isinstance(new_ways, Series)):
        return new_ways.isin(existing_ways).any()
    if(isinstance(new_ways, numpy.int64)):
        return new_ways in existing_ways
    else:
        print("List of ways is not a Series, as was expected.")
        return True

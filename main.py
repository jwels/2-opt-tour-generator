from numpy import Infinity
import helper_functions as helpers
import json
import pandas as pd

# algorithm parameters
budget = 1
target_length = 2
verbose = False

# load data (ways and nodes)
with open('data/schlosspark.json') as f: # TODO: remove this and make helpers work with node list
  data = json.load(f)["elements"]

nodes = pd.read_json("data/preprocessed_nodes.json")
ways = pd.read_json("data/preprocessed_ways.json")


# inital values and start solution/tour
num_of_iterations = 0
start_tour = helpers.getStaticExampleTour(ways)
helpers.prepareOverpassPlotScriptForTour(start_tour, "plot-nodes-init-solution")
print(start_tour)
start_tour.to_csv("data/start_tour.csv")
# at first, the tour used by the algorithm is the start solution
tour = start_tour
# remove duplicate index column created by pandas
tour = tour.drop(['index'], axis=1)
curr_diff = target_length-helpers.getTourLengthDF(start_tour)
prev_diff = Infinity # Infinity to make first improvement positive
improvement = prev_diff-curr_diff

# main algorithm loop. Find better solutions from initial solution until budget is reached
# Based on 2-opt but implementation differs in several regards:
# - OSM data is not a fully connected graph. So reversing order of a section of the tour is not always possible.
# - Instead, 2 edges will be removed and replaced by new edges connecting any 2 of the 4 "free" nodes TODO: How many edges for replacement?
# - Additionally, the algorithm aims for a target length instead of minimizing the length
while num_of_iterations < budget and improvement>0:
    print("--------------")
    print("Iteration: " + str(num_of_iterations))
    print("Improvement: " + str(improvement))
    print("Difference to target: " + str(curr_diff))
    print("--------------")

    # iterate over every way in the tour
    for i, way_i in enumerate(tour.itertuples()):
      # nested loop to get second edge to be removed for every "i"
      for k, way_k in enumerate(tour.itertuples()):
        # dont loop over ways w. index smaller than outer index i
        if k <= i or k >= len(tour) - 1:
          continue

        replacement_way_i = helpers.getAlternativeWay(way_i.start_node, way_k.start_node, way_i.length, ways, curr_diff)
        replacement_way_k = helpers.getAlternativeWay(way_i.end_node, way_k.end_node, way_k.length, ways, curr_diff)
        if(verbose):
          print(str(i) + ":" + str(k) + "########################################################## COMPARISON ###")
          print("REPL: former way: "+str(way_i.id)+"_"+str(way_i.sub_id) +" from " + str(way_i.start_node) +" to " +str(way_k.start_node))
          print(replacement_way_i)
          print("REPL: former way: "+str(way_k.id)+"_"+str(way_k.sub_id) +" from " + str(way_i.end_node) +" to "+str(way_k.end_node))
          print(replacement_way_k)
        # replace only if a possible replacement for both selected edges was found
        if(len(replacement_way_i)>0 and len(replacement_way_k)>0):
          #print(tour.iloc[i])
          #print(replacement_way_i)
          tour.iloc[i] = replacement_way_i.squeeze(axis=0)
          tour.iloc[k] = replacement_way_k.squeeze(axis=0)
          #print(way_i)
          #tour.iloc[15] = tour.iloc[0]

    # set differences for stopping criterion and increase budget counter
    prev_diff = curr_diff
    curr_diff = abs(helpers.getTourLengthDF(tour)-target_length)
    improvement = prev_diff-curr_diff
    num_of_iterations = num_of_iterations + 1
    print(tour)
    helpers.prepareOverpassPlotScriptForTour(tour, "plot-nodes-algo-output")
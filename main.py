from numpy import Infinity
from pandas.core.frame import DataFrame
from pandas.core.series import Series
import helper_functions as helpers
import json
import pandas as pd

# algorithm parameters
budget = 5
target_length = 2
verbose = True

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
    print("------ITERATION START--------")
    print("Iteration: " + str(num_of_iterations))

    # iterate over every way in the tour
    for i, way_i in enumerate(tour.itertuples()):
      # nested loop to get second edge/way to be replaced for every "i"
      for k, way_k in enumerate(tour.itertuples()):
        # dont loop over ways with index smaller than outer index i
        if k <= i or k >= len(tour) - 1:
          continue
        #get alternative ways that improve the difference the most
        replacement_way_i = helpers.getAlternativeWay(way_i.start_node, way_k.start_node, way_i.length, tour, ways, curr_diff)
        replacement_way_k = helpers.getAlternativeWay(way_i.end_node, way_k.end_node, way_k.length, tour, ways, curr_diff, blacklist=replacement_way_i)

        # Now four possible cases can occur: 
        # 1. no replacement found at all -> do nothing and go to next iteration
        if(len(replacement_way_i)==0 and len(replacement_way_k)==0):
          continue

        # 2. a replacement was found only for edge/way i
        if(len(replacement_way_i)>0 and len(replacement_way_k)==0 and not (replacement_way_i.section_id.isin(tour.section_id).all())):
          # debugging output if verbose = True (see at the top)
          if(verbose):
            helpers.printDebugInformation(tour, i, k, way_i, way_k, replacement_way_i, replacement_way_k, "Case 2")
          tour = tour.drop(tour.index[i:k]).reset_index(drop=True)
          #tour = tour.drop([i]).reset_index(drop=True)
          tour = pd.concat([tour.iloc[:i-1], pd.DataFrame(replacement_way_i).reset_index(drop=True), tour.iloc[i-1:]], axis=0).reset_index(drop=True) #tour.append(replacement_way_i).reset_index(drop=True)

        # 3. a replacement was found only for edge/way k
        if(len(replacement_way_i)==0 and len(replacement_way_k)>0  and not (replacement_way_k.section_id.isin(tour.section_id).all())):
          # debugging output if verbose = True (see at the top)
          if(verbose):
            helpers.printDebugInformation(tour, i, k, way_i, way_k, replacement_way_i, replacement_way_k, "Case 3")
          tour = tour.drop(tour.index[(i+1):k])
          tour = tour.drop([k]).reset_index(drop=True)
          tour = pd.concat([tour.iloc[:k-1], pd.DataFrame(replacement_way_k).reset_index(drop=True), tour.iloc[k-1:]], axis=0).reset_index(drop=True)
          print(tour)
          
        # 4. a replacement was found for both, i and k, reconnecting their start/end nodes (standard 2-opt case)
        if(len(replacement_way_i)>0 and len(replacement_way_k)>0)  and not (replacement_way_i.section_id.isin(tour.section_id).all())  and not (replacement_way_k.section_id.isin(tour.section_id.all())):
          # remove potential duplicates (in some edge cases, the dataframe returned second can otherwise contain ways already in the first one)
          # replacement_way_k = replacement_way_k[~replacement_way_k.section_id.isin(replacement_way_i.section_id)] TODO: still necessary? was in case 4
          
          # debugging output if verbose = True (see at the top)
          if(verbose):
            helpers.printDebugInformation(tour, i, k, way_i, way_k, replacement_way_i, replacement_way_k, "Case 4")
          # add both replacements to tour
          tour = tour.drop([i]).reset_index(drop=True)
          tour = pd.concat([tour.iloc[:i-1], pd.DataFrame(replacement_way_i).reset_index(drop=True), tour.iloc[i-1:]], axis=0).reset_index(drop=True) #tour.append(replacement_way_i).reset_index(drop=True)
          tour = tour.drop([k]).reset_index(drop=True)
          tour = pd.concat([tour.iloc[:k-1], pd.DataFrame(replacement_way_k).reset_index(drop=True), tour.iloc[k-1:]], axis=0).reset_index(drop=True)

    # set differences for stopping criterion and increase budget counter
    prev_diff = curr_diff
    curr_diff = abs(helpers.getTourLengthDF(tour)-target_length)
    improvement = prev_diff-curr_diff
    num_of_iterations = num_of_iterations + 1
    print("-------ITERATION END-------")
    print("Iteration: " + str(num_of_iterations-1))
    print("Improvement: " + str(improvement))
    print("Difference to target: " + str(curr_diff))
    helpers.prepareOverpassPlotScriptForTour(tour, "plot-nodes-algo-output")

print("---------------------------TERMINATED------------------------------------")
print(tour)
print("Target length: "+str(target_length)+" km")
print("Result length: "+str(helpers.getTourLengthDF(tour))+" km")
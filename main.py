from numpy import Infinity
import helper_functions as helpers
import pandas as pd

# algorithm parameters
budget = 50
target_length = 2
verbose = False

# load data set (execute preprocessing.py previously)
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
no_improvement_counter = 0
changes_made = False
reached_tour_end = False

# main algorithm loop. Find better solutions from initial solution until budget is reached
# Based on 2-opt but implementation differs in several regards:
# - OSM data is not a fully connected graph. So reversing order of a section of the tour is not always possible.
# - Instead, 2 edges will be removed and replaced by new edges connecting any 2 of the 4 "free" nodes
# - Additionally, the algorithm aims for a target length instead of minimizing the length
while num_of_iterations < budget:
    print("------ITERATION START--------")
    print("Iteration: " + str(num_of_iterations))
    # iterate over every way in the tour
    for i, way_i in enumerate(tour.itertuples()):
      # nested loop to get second edge/way to be replaced for every "i"
      for k, way_k in enumerate(tour.itertuples()):
        # dont loop over ways with index smaller than outer index i
        if k <= i or k >= len(tour) - 1:
          continue
        #get alternative ways that improve the difference the most, later its checked if they are longer than the sum of ways they replace
        replacement_way_i = helpers.getAlternativeWay(way_i.start_node, way_k.start_node, way_i.length, tour, ways, curr_diff)
        replacement_way_k = helpers.getAlternativeWay(way_i.end_node, way_k.end_node, way_k.length, tour, ways, curr_diff, blacklist=replacement_way_i)

        # Now four possible cases can occur: (in standard 2-opt, only 1. and 4. are handled/needed)
        # 1. no replacement found at all -> do nothing and go to next iteration
        if(len(replacement_way_i)==0 and len(replacement_way_k)==0):
          continue

        # 2. a replacement was found only for edge/way i
        if(len(replacement_way_i)>0 and len(replacement_way_k)==0 and not helpers.isWayInTour(replacement_way_i, tour)):
          # check if replacing ways would decrease difference to target length, skip iteration if not
          if( abs(curr_diff-helpers.getTourLengthDF(tour[i:k])) > abs(curr_diff-helpers.getTourLengthDF(replacement_way_i)) ):
            # debugging output if verbose = True (see at the top)
            if(verbose):
              helpers.printDebugInformation(tour, i, k, way_i, way_k, replacement_way_i, replacement_way_k, "Case 2")
            tour = tour.drop(tour.index[i:k]) #note: slicing is [inclusive:exclusive]
            print("heyo")
            print(tour)
            first_section = tour.loc[:i].append(replacement_way_i, ignore_index=True)
            second_section = tour.loc[k:]
            tour = pd.concat([first_section, second_section]).reset_index(drop=True)
            print(tour)
            # indicate that a change was made, used to restart outer for loop to keep loop and dataframe indices in sync
            changes_made = True

        # 3. a replacement was found only for edge/way k
        if(len(replacement_way_i)==0 and len(replacement_way_k)>0  and not helpers.isWayInTour(replacement_way_k, tour)):
          # check if replacing ways would decrease difference to target length, skip iteration if not
          if( abs(curr_diff-helpers.getTourLengthDF(tour[(i+1):(k+1)])) > abs(curr_diff-helpers.getTourLengthDF(replacement_way_k)) ):
            # debugging output if verbose = True (see at the top)
            if(verbose):
              helpers.printDebugInformation(tour, i, k, way_i, way_k, replacement_way_i, replacement_way_k, "Case 3")        
              print(way_i)
              print("------")
            tour = tour.drop(tour.index[(i+1):(k+1)]) #note: slicing is [inclusive:exclusive]
            print("heyo")
            print(tour)
            first_section = tour.loc[:i+1].append(replacement_way_k, ignore_index=True)
            second_section = tour.loc[k+1:]
            tour = pd.concat([first_section, second_section]).reset_index(drop=True)
            print(tour)
            # indicate that a change was made, used to restart outer for loop to keep loop and dataframe indices in sync
            changes_made = True
          
        # 4. a replacement was found for both, i and k, reconnecting their start/end nodes (standard 2-opt case)
        if(len(replacement_way_i)>0 and len(replacement_way_k)>0 and not helpers.isWayInTour(replacement_way_i, tour)  and not helpers.isWayInTour(replacement_way_k, tour)):
          # check if replacing ways would decrease difference to target length, skip iteration if not
          if( abs(curr_diff-helpers.getTourLengthDF(tour[i])-helpers.getTourLengthDF(tour[k])) > abs(curr_diff-helpers.getTourLengthDF(replacement_way_k)) ):
            # debugging output if verbose = True (see at the top)
            if(verbose):
              helpers.printDebugInformation(tour, i, k, way_i, way_k, replacement_way_i, replacement_way_k, "Case 4")
            # add both replacements to tour and remove previous edges/ways i and k
            tour = tour.drop([i])
            tour = tour.drop([k])
            # first part of tour before i, unchanged, with new replacement for i
            first_section = tour.loc[:i].append(replacement_way_i, ignore_index=True) 
            # all edges/ways between i and k in reversed order, appended k at the end
            middle_section = tour.loc[i+1:k]
            middle_section = tour.loc[::-1].append(replacement_way_k, ignore_index=True) 
            # last part of tour after k, unchanged
            last_section = tour.loc[k+1:] 
            tour = pd.concat([
              first_section,
              middle_section,
              last_section  
              ], axis=0).reset_index(drop=True) #tour.append(replacement_way_i).reset_index(drop=True)
            # indicate that a change was made, used to restart outer for loop to keep loop and dataframe indices in sync
            changes_made = True
      
      # break the i loop and restart from the beginning if the tour was changed 
      # this resets the indices after a change to the itertuples
      if changes_made:
        break
      elif i==len(tour)-1:
        reached_tour_end = True

    if(improvement==0):
      no_improvement_counter = no_improvement_counter + 1
    if(no_improvement_counter>=len(tour) or reached_tour_end):
      break
  
    # set differences for stopping criterion and increase budget counter
    prev_diff = curr_diff
    curr_diff = abs(helpers.getTourLengthDF(tour)-target_length)
    improvement = prev_diff-curr_diff
    num_of_iterations = num_of_iterations + 1
    changes_made = False
    print("-------ITERATION END-------")
    print("Iteration: " + str(num_of_iterations-1))
    print("Improvement: " + str(improvement))
    print("Difference to target: " + str(curr_diff))
    helpers.prepareOverpassPlotScriptForTour(tour, "plot-nodes-algo-output")

print("---------------------------TERMINATED------------------------------------")
print(tour)
print("Target length: "+str(target_length)+" km")
print("Result length: "+str(helpers.getTourLengthDF(tour))+" km")
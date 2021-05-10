import helper_functions as helpers
import json

# algorithm parameters
budget = 1

# load data (ways and nodes)
with open('data/schlosspark.json') as f: # TODO: remove this and make helpers work with node list
  data = json.load(f)["elements"]
with open('data/preprocessed_nodes.json') as f:
  nodes = json.load(f)
with open('data/preprocessed_ways.json') as f:
  ways = json.load(f)

# inital values
num_of_iterations = 0

# main algorithm loop. Find better solutions from initial solution until budget is reached
while num_of_iterations < budget:
    print(helpers.getRandomTour(ways, data))
    num_of_iterations = num_of_iterations + 1
import json
import helper_functions as helpers
import copy

### ---------------- Preprocessing ----------------

print("Beginning preprocessing...")

#read dataset (JSON file from Overpass Turbo API)
with open('data/schlosspark.json') as f:
  data = json.load(f)["elements"]

# generate list of OSM ways in the dataset
ways = []
for d in data:
    if(d["type"]=="way"):
        ways.append(d)

# get every first and last OSM node from every way as nodes for the TSP
nodes = []
for d in data:
    if(d["type"]=="way"):
        #get the first node id
        first_node_id = d["nodes"][0] 
        # and the last node id
        last_node_id = d["nodes"][len(d["nodes"])-1] 
        #search for first and last node in total list of nodes
        search_first_node = list(filter(lambda entry: entry['id'] == first_node_id, data))[0] 
        search_last_node = list(filter(lambda entry: entry['id'] == last_node_id, data))[0]
        # add tags from way also to the node to use as sets later on
        search_first_node["tags"] = d["tags"]
        search_last_node["tags"] = d["tags"]
        # add them to result list
        nodes.append(search_first_node)
        nodes.append(search_last_node)

# divide every way in current way dataset into multiple sub-ways if it contains one of the nodes
# list of nodes already used for a split
nodes_already_split = []
for w in ways:
    # count the splits made for naming of new sub-ways
    if "sub_id" in w:
        counter = w["sub_id"]
    else:
        counter=0 
    # look at every node in way except first and last (already in nodes dict)
    for n in w["nodes"][1:-1]:
        node_ids = copy.deepcopy([n['id'] for n in nodes])
        new_way = []
        # create a new way based on the old one, copy all attributes and split up the nodes between the new ways
        if n in node_ids and n in w["nodes"] and not n in nodes_already_split:
            # deep copy ensures that its not a reference
            new_way = copy.deepcopy(w)
            index = w["nodes"].index(n)
            first_slice = w["nodes"][:index]
            first_slice.append(n)
            second_slice = w["nodes"][index:]
            w["nodes"] = first_slice
            w["sub_id"] = counter
            counter = counter + 1
            new_way["nodes"] = second_slice
            new_way["sub_id"] = counter
            counter = counter + 1
            ways.append(new_way)
            nodes_already_split.append(n)
    

# calculate length of every way and store it for later usage
for w in ways:
    length = helpers.getWayLength(w, data)
    w["length"] = length

# get tags used on OSM ways to define sets
# only used for exploring possible sets
tags = []
for w in ways:
    if "highway" in w["tags"]:
        tags.append("highway="+w["tags"]["highway"])
    if "service" in w["tags"]:
        tags.append("service="+w["tags"]["service"])
    if "name" in w["tags"]:
        tags.append("name="+w["tags"]["name"])
    if "lit" in w["tags"]:
        tags.append("lit="+w["tags"]["lit"])
    if "surface" in w["tags"]:
        tags.append("surface="+w["tags"]["surface"])
    if "bridge" in w["tags"]:
        tags.append("bridge="+w["tags"]["bridge"])
tags = set(tags)

print("There are " + str(len(ways)) + " ways in the current dataset.")
print("There are " + str(len(nodes)) + " nodes acting as way start- and endpoints in the current dataset.")

#print(helpers.getWayLength(ways[11], data))
#print(helpers.getNodeDistance(nodes[2], nodes[3]))
print(helpers.getTourLength([ways[1], ways[2]], data))

# write preprocessed data to file
with open('data/preprocessed_ways.json', 'w', encoding='utf-8') as f:
    json.dump(ways, f, ensure_ascii=False, indent=4)
with open('data/preprocessed_nodes.json', 'w', encoding='utf-8') as f:
    json.dump(nodes, f, ensure_ascii=False, indent=4)
print("Done. Results written to files.")
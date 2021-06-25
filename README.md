# 2-opt-tour-generator
2-opt adaption to generate tours of a given length on OpenStreetMap data.

# Usage

1. Have the packages listed in the requirments.txt installed or install them via ```pip install -r requirements.txt```
2. If no data is present yet, run the preproceessing.py file to generate data from an overpass-turbo export. If new or different data is used, change the path to the new file name in preprocessing.py  
3. Run main.py to generate a tour. Check the parameters at the top of the script to change the starting solution, budget etc.

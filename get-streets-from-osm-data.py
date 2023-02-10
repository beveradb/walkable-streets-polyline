import json
  
# Opening JSON file
f = open('data/osm-all-ways-in-scope-area.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
for way in data['elements']:
    county = 'UnknownCounty'
    zip = 'UnknownZip'

    if 'tiger:county' in way['tags']:
        county = way['tags']['tiger:county']

    if 'tiger:zip_left' in way['tags']:
        zip = way['tags']['tiger:zip_left']

    print('{:s}, {:s}, {:s}'.format(way['tags']['name'], county, zip))

f.close()
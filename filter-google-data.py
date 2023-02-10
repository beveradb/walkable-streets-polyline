import ast
import csv
  
inputcsv = "data/batch-geocoder-output.csv"
outputcsv = "data/batch-geocoder-output-filtered-formatted.csv"

outputcsvfile = open(outputcsv, 'w', newline ='')
outputaddresslist = []

with outputcsvfile:
    header = ['Address', 'Street', 'Hood', 'Town', 'County', 'Zip', 'Lat', 'Lng']
    writer = csv.DictWriter(outputcsvfile, fieldnames = header)
    writer.writeheader()

    with open(inputcsv, "r") as f:
        reader = csv.reader(f)
        header = next(reader) # skip the input file header row
        for row in reader:
            dict_string = row[11] # parse google maps API raw response from column 12
            data = ast.literal_eval(dict_string)
            results = data['results']
            
            for result in results: # each response from the API may have more than one result if it matched multiple addresses
                address = result['formatted_address']
                zip = None
                street = 'UnknownStreet'
                hood = 'UnknownHood'
                town = 'UnknownTown'
                county = 'UnknownCounty'

                for address_component in result.get('address_components'):
                    if 'route' in address_component.get('types'):
                        street = address_component.get('long_name')
                    if 'postal_code' in address_component.get('types'):
                        zip = address_component.get('long_name')
                    if 'locality' in address_component.get('types'):
                        town = address_component.get('long_name')
                    if 'neighborhood' in address_component.get('types'):
                        hood = address_component.get('long_name')
                    if 'administrative_area_level_2' in address_component.get('types'):
                        county = address_component.get('long_name')

                # exclude results which weren't specific enough
                if result['geometry']['location_type'] != 'GEOMETRIC_CENTER':
                    continue
                # exclude results with missing zips; residential streets always have zips
                if zip is None:
                    continue
                # exclude duplicates
                if address in outputaddresslist:
                    continue
                else:
                    outputaddresslist.append(address)

                writer.writerow({
                    'Address' : address,
                    'Street' : street,
                    'Hood': hood,
                    'Town': town,
                    'County': county,
                    'Zip': zip,
                    'Lat': result['geometry']['location']['lat'],
                    'Lng': result['geometry']['location']['lng']
                })
 
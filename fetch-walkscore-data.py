import csv
import requests
import sys

# API key for Walk Score API
api_key = 'YOUR_WALKSCORE_API_KEY'

# Read input CSV file
with open('data/batch-geocoder-output-filtered-formatted.csv', 'r') as input_file:
    reader = csv.DictReader(input_file)
    rows = [row for row in reader]

processinglimit = 20000
rowcount = 0
processedcount = 0
skipuntiladdress = None

# Write output CSV file with additional Walk Score column
with open('data/batch-geocoder-output-filtered-formatted-with-walkscore.csv', 'a', newline='') as output_file:
    fieldnames = reader.fieldnames + ['Walk Score', 'Bike Score', 'Transit Score']
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()

    # Write raw output CSV file
    with open('data/walkscore-data-raw.json', 'a', newline='') as raw_response_output_file:
        raw_response_output_file.write('[\n')

        # Fetch Walk Score, Bike Score, and Transit Score data for each row
        for row in rows:
            address = row['Address']
            lat = row['Lat']
            lng = row['Lng']

            rowcount += 1

            if skipuntiladdress is not None:
                if address == skipuntiladdress:
                    print('Found matching skipuntil address at row {}, setting to None, address: {}'.format(rowcount, skipuntiladdress, address))
                    skipuntiladdress = None
                    continue
                else:
                    print('Skipping row {} as skipuntil is set to {} and row does not match: {}'.format(rowcount, skipuntiladdress, address))
                    continue

            print('Processing row {}, processed {} - address: {}'.format(rowcount, processedcount, address))
            processedcount += 1

            if processedcount > processinglimit:
                sys.exit()    

            # Make API call
            url = f'http://api.walkscore.com/score?format=json&transit=1&bike=1&lat={lat}&lon={lng}&address={address}&wsapikey={api_key}'
            response = requests.get(url)

            raw_response_output_file.write(response.text + ',\n')

            data = response.json()

            # Write row with Walk Score, Bike Score, and Transit Score data
            transitscore = 0
            bikescore = 0
            if 'transit' in data:
                transitscore = data['transit']['score']
            if 'bike' in data:
                bikescore = data['bike']['score']


            if data['status'] == 2:
                print('Skipping entry with no walk score - address: {}'.format(address))
                continue

            if 'walkscore' not in data:
                print('Unexpected response:')
                print(data)
                sys.exit()

            row['Walk Score'] = data['walkscore']
            row['Bike Score'] = bikescore
            row['Transit Score'] = transitscore
            writer.writerow(row)

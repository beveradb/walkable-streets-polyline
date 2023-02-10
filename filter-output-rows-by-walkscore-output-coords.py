import csv

input_file = 'data/batch-geocoder-output-filtered-formatted-with-walkscore.csv'
output_file = 'data/coords-for-streets-with-walkbikescore-over-thresholds.csv'

walk_score_threshold = 70
bike_score_threshold = 70
transit_score_threshold = 40

with open(input_file, 'r') as in_csv, open(output_file, 'w', newline='') as out_csv:
    reader = csv.reader(in_csv)
    writer = csv.writer(out_csv)
    
    # Write header row to output file
    header = next(reader)
    
    for row in reader:
        walk_score = int(row[7])
        bike_score = int(row[8])
        transit_score = int(row[9])
        
        # Check if walk, bike and transit scores are over thresholds
        if walk_score > walk_score_threshold and bike_score > bike_score_threshold and transit_score > transit_score_threshold:
            writer.writerow([row[5], row[6]])

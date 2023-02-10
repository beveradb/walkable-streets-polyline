# Walkable Streets Polyline Zillow Search
Geocode all streets in an area (e.g. a city), fetch Walk Score data for each, filter to be only streets with a Walk Score and Cycle Score greater than a certain threshold (e.g. 70), and generate an alpha shape polygon to use for a Zillow search

### Instructions

This was a quick hacky project to give me what I needed to find a place to rent in Austin, TX - so it's an ugly multi-step process, sorry! :)

## Fetch street data, geocode and fetch walk score data

1. Fetch OpenStreetMap data for the area you're interested in, using Overpass:
    - Open https://overpass-turbo.eu, zoom in on the map to show just the rough area you're interested in (e.g. city boundaries)
    - Run this query to output the raw Way data as JSON:
    ```
    [out:json][timeout:25];
    way["highway"]["name"]({{bbox}});
    out body;
    ```
    - Click the Export button, then "raw OSM data", save as `data/osm-all-ways-in-scope-area.json` 

2. Extract just the street name, county and zip (where available) from that JSON data, using a minimal python script:
    - `python get-streets-from-osm-data.py > data/streets-from-osm.txt`

3. Remove dupes to reduce number of API calls:
    - `cat data/streets-from-osm.txt | sort | uniq > data/streets-from-osm-unique.txt`

4. Hacky cleanup on that street data to remove entries with no county and only keep ones within a certain radius of a central zip. This was pretty hacky and I could have done this much more cleanly using the python script above or a better OSM query, but whatever.
    - Get a list of zip codes from https://www.freemaptools.com/find-zip-codes-inside-radius.htm by specifying my target and radius, dump these into `data/zips-within-20miles-of-78751.txt`
    - `grep -v UnknownCounty data/streets-from-osm-unique.txt > data/streets-from-osm-unique-nounknowncounty.txt`
    - `grep -f data/zips-within-20miles-of-78751.txt data/streets-from-osm-unique-nounknowncounty.txt > data/streets-from-osm-unique-nounknowncounty-within-20miles-of-78751.txt`

5. Batch geocode all of those streets, using the Google Maps API with an API key attached to a payment profile. If you're looking at a smaller area (less than 2500 addresses) or willing to let it run over several days, you can get away with the free tier without an API key.
Thanks to this guy for the script: https://gist.github.com/shanealynn/033c8a3cacdba8ce03cbe116225ced31
    - Create the API key: https://developers.google.com/maps/documentation/geocoding/get-api-key
    - Replace `YOUR_GOOGLE_MAPS_API_KEY` in `geocode-addresses.py` with your API key
    - `python geocode-addresses.py` (then wait patiently, for me it took a couple of hours to geocode all 16,000 streets)

6. Filter the Google Maps Geocoder data responses and extract only the useful information, reformatting as a clean CSV ('Address', 'Street', 'Hood', 'Town', 'County', 'Zip', 'Lat', 'Lng')
    - `python filter-google-data.py`

7. Fetch data from the Walk Score API for every street. The API requires you pass in both an address *and a lat/lng*, which is the main reason we needed to geocode everything with Google Maps first.
    - Sign up for a free API key (it gets emailed to you instantly as long as the email address you provide matches the domain you specify): https://www.walkscore.com/professional/api-sign-up.php
    - Replace `YOUR_WALKSCORE_API_KEY` in `fetch-walkscore-data.py` with your API key
    - `python fetch-walkscore-data.py` (and wait patiently again, for me it took another hour or so for all 16,000 streets)

At this point, you should have an output CSV file `data/batch-geocoder-output-filtered-formatted-with-walkscore.csv` containing a clean list of all residential streets in your target area, with full addresses, coordinates, and walk/cycle/transit scores when available.

This may already be useful - for example you can upload that to google sheets and filter/sort it, use it as a lookup table for other use cases etc.

However, if like me you want a Zillow search which only shows you properties in a _walkable_ area, there's a couple more steps:

## Filter streets by preferred walk score threshold and create zillow search area

1. Filter the output streets to only include rows with Walk Score and Bike Score over your preferred threshold:
    - Choose your own criteria, edit the `walk_score_threshold` variable (for me this was 70)
    - `python filter-output-rows-by-walkscore-output-coords.py`

2. Find the Alpha Shape polygon around all of the points and output the coords of this polygon:
    - `python find-alpha-shape-polygon-around-all-points.py`
    - See all of the street coordinates plotted on a graph, and a red line showing the polygon
    - Tweak the `alpha_value` variable at the top of the script to get the result which is best for your target area:
        - If it's too high (e.g. 400 in my case), the polygon will enclose all of the streets, but it'll be a really simple shape which includes a ton of other areas which aren't actually walkable (so your Zillow search will end up with false positives and waste your time
        - If it's too low (e.g. 10), the polygon will definitely only cover super walkable areas, but it'll probably also cut out a bunch of streets you'd want to include.
        - The sweet spot will give you a complex polygon which covers most of the walkable streets and avoids covering any other areas. For me this was an alpha value of 130. See examples below.
    - You now have a target area polygon defined by coordinates in `polygon-of-streets-with-walkandbike-score-over-70.csv`.

3. Create a Zillow custom search area using the coordinates in this file:
    - `python generate-zillow-url.py`
    - This should open a URL in your web browser with your amazing zillow search area baked into the URL!
    - You can edit the filters however you like, but crucially the `customRegionId` value in the URL is what adds the custom search area (which this script also prints in the terminal for convenience)

#### Examples:

![Alpha Shape with Alpha = 10](/images/Austin-Alpha-10.png)
*Alpha Shape with Alpha = 10*

![Alpha Shape with Alpha = 130](/images/Austin-Alpha-130.png)
*Alpha Shape with Alpha = 130*

![Alpha Shape with Alpha = 400](/images/Austin-Alpha-400.png)
*Alpha Shape with Alpha = 400*

![Resulting Zillow search](/images/Zillow-Example-Rental-Search.png)
*Resulting Zillow search*

#### To Do:

- Tidy this up to be a single script which kinda does it all given your input preferences / parameters, for any city.
- Make this accessible as a free public website, similar to https://homearea.info which I built for a similar use case in the UK!

import csv
import requests
import urllib.parse
import json
import webbrowser

input_file = 'data/polygon-of-streets-with-walkandbike-score-over-thresholds.csv'
zillow_custom_region_url = "https://www.zillow.com/search/GetSearchPageCustomRegion.htm"

def read_csv_coordinates(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        _ = next(reader)
        coordinates = [list(map(float, row)) for row in reader]

    x_coordinates = [coordinate[0] for coordinate in coordinates]
    y_coordinates = [coordinate[1] for coordinate in coordinates]

    bounding_box = {
        "min_x": min(x_coordinates),
        "max_x": max(x_coordinates),
        "min_y": min(y_coordinates), 
        "max_y": max(y_coordinates)
    }

    # '30.228727,-97.7841043|30.2394033,-97.7816472|30.2439412,-97.7768899|30.2445961,-97.775262'
    coordinates_string = "|".join(f"{coordinate[0]},{coordinate[1]}" for coordinate in coordinates)

    return bounding_box, coordinates_string

if __name__ == '__main__':
    bounding_box, coordinates_string = read_csv_coordinates(input_file)
    print(f"Bounding Box: {bounding_box}")
    print(f"Polygon Coordinates: {coordinates_string}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0", 
        "Accept": "*/*", 
        "Accept-Language": "en-US,en;q=0.5", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Origin": "https://www.zillow.com", 
        "Alt-Used": "www.zillow.com", 
        "Connection": "keep-alive", 
        "Sec-Fetch-Dest": "empty", 
        "Sec-Fetch-Mode": "cors", 
        "Sec-Fetch-Site": "same-origin", 
        "Pragma": "no-cache", 
        "Cache-Control": "no-cache", 
        "TE": "trailers", 
    } 

    files = {'clipPolygon': (None, coordinates_string)}

    response = requests.post(zillow_custom_region_url, headers=headers, files=files)
    custom_region_response = json.loads(response.text)

    print(custom_region_response)
    custom_region_id = custom_region_response['customRegionId']

    print(f"Zillow Custom Region ID: {custom_region_id}")

    # https://www.zillow.com/homes/for_rent/?searchQueryState={"pagination":{},"mapBounds":{"west":-97.82571861659957,"east":-97.65783378993942,"south":30.23832505713156,"north":30.354230948490876},"mapZoom":13,"customRegionId":"c1d9063e0aX1-CR8tatbmtpqax1_17l0ph","isMapVisible":true,"filterState":{"fore":{"value":false},"ah":{"value":true},"auc":{"value":false},"nc":{"value":false},"fr":{"value":true},"fsbo":{"value":false},"cmsn":{"value":false},"fsba":{"value":false},"mp":{"max":2000,"min":1200},"price":{"max":419450,"min":251670},"beds":{"min":1},"baths":{"min":1},"apco":{"value":false},"apa":{"value":false},"con":{"value":false}},"isListVisible":true}

    mapBounds = {
        "west": bounding_box['max_y'],
        "east": bounding_box['min_y'],
        "south": bounding_box['min_x'],
        "north": bounding_box['max_x']
    }
    print(mapBounds)

    zillow_search_obj = {
        "pagination": {},
        "mapBounds": {
            "south": bounding_box['min_x'],
            "north": bounding_box['max_x'],
            "west": bounding_box['min_y'],
            "east": bounding_box['max_y']
        },
        "mapZoom": 12,
        "customRegionId": custom_region_id,
        "isMapVisible": "true"
    }

    zillow_search_obj_json = json.dumps(zillow_search_obj)
    zillow_search_obj_json_urlenc = urllib.parse.quote_plus(zillow_search_obj_json)

    full_zillow_url = 'https://www.zillow.com/homes/for_rent/?searchQueryState=' + zillow_search_obj_json_urlenc

    print(f"Zillow Search URL:\n\n{full_zillow_url}")

    webbrowser.open(full_zillow_url)

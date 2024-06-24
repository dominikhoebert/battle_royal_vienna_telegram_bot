import requests
import sys
import csv
import urllib.parse

place_extention = None


def get_lat_long(api_key, place_url):
    # Extract the place name from the URL
    place_name = place_url.split('/place/')[1].split('/')[0]
    place_name = urllib.parse.unquote_plus(place_name)

    if place_extention is not None:
        place_name = ", " + place_extention

    # Prepare the request to the Google Maps Geocoding API
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': place_name + place_extention,
        'key': api_key
    }

    # Send the request
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            # Extract latitude and longitude from the response
            location = data['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            address = data['results'][0]['formatted_address']
            return lat, lng, address
        else:
            print(f"Error in API response: {data['status']} for {place_name}")
            return None, None, None
    else:
        print(f"HTTP error: {response.status_code} for {place_name}")
        return None, None, None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python lat_long.py <filename> <API key> [place_extention]")
        sys.exit(1)
    filename = sys.argv[1]
    api_key = sys.argv[2]
    if len(sys.argv) > 3:
        place_extention = sys.argv[3]
    print(f"Reading from {filename} and using API key {api_key}")
    reader = csv.DictReader(open(filename, 'r', encoding='utf-8'))
    with open('data/poi.csv', 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["title", "map", "url", "comment", "lat", "lng", "address"])
        for row in reader:
            url = row['url']
            lat, lng, address = get_lat_long(api_key, url)
            writer.writerow([row['title'], row['map'], row['url'], row['comment'], lat, lng, address])

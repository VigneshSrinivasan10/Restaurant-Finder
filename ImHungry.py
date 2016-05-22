import googlemaps
import requests
import argparse
import os
import random

LOCATION = 'Salzufer 6, Berlin'
URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
API_KEY = 'AIzaSyBXDwOhUJFijay3gC1nKv3er1Du5AWvuqI'

def get_args():
    parser = argparse.ArgumentParser(
        description='Script retrieves schedules from a given server')
    parser.add_argument('-r', '--radius', type=str, help='Radius', required=True)
    parser.add_argument('-f', '--filters', type=str, help='file', required=True)
    parser.add_argument('-p', '--price', type=str, help='Min&Max price', required=True, nargs='+')
    parser.add_argument('-t', '--type', type=str, help='Restaurant type', required=False, default=None)
    args = parser.parse_args()
    radius = args.radius
    filtersFile = args.filters
    price = args.price[0].split("-")
    resType = args.type
    return radius, filtersFile, price, resType

radiusToSearch, filtersFile, price, resType = get_args()

def geoCode(loc):
    gmaps = googlemaps.Client(key=API_KEY)
    return gmaps.geocode(loc)

def getCoords(geocode_result):
    lat = str(geocode_result[0]['geometry']['location']['lat'])
    lng = str(geocode_result[0]['geometry']['location']['lng'])
    return lat,lng
    
def createScript(lat,lng,radiusToSearch, price, apiKey):
    loc = 'location='+lat+','+lng+'&'
    radius = 'radius='+radiusToSearch+'&'
    types = 'type='+'restaurant'+'&'
    minMaxPrice = 'maxprice='+price[0]+'&'+'minprice='+price[1]
    key = 'key='+apiKey
    script = loc+radius+types+key 
    return script
    
def retrieveRes(url, script):
    req = requests.get(url+script)
    if req.status_code != 200:
        print 'Error in script'
        exit()
    req = req.json()
    noRetrieved = len(req['results'])
    nameRestaurants = [req['results'][i]['name'] for i in range(noRetrieved)]
    return nameRestaurants

def extractList(filtersFile):
    return [line.split('\n')[0] for line in open(filtersFile)]

def filterNames(nameRestaurants, filters):
    dummy = [nameRestaurants.remove(f) for f in filters if f in nameRestaurants]
    return nameRestaurants
        
def reWriteFilters(filtersFile, resToGo):
    with open(filtersFile, 'a') as f:
        f.write(resToGo+'\n')
    f.close()
    filters = extractList(filtersFile)
    if len(filters) >= 5:
        filters = filters[-5:]
        with open(filtersFile, 'w') as f:
            for filt in filters:
                f.write(filt+'\n')
        f.close()
    

def randomize(nameRestaurants):
    if os.path.exists(filtersFile):
       filters = extractList(filtersFile) 
       nameRestaurants = filterNames(nameRestaurants, filters)
    random.shuffle(nameRestaurants)
    resToGo = nameRestaurants[0]
    #pdb.set_trace()
    reWriteFilters(filtersFile, resToGo)
    return resToGo
    

def main():
    geocode_result = geoCode(LOCATION)
    lat, lng = getCoords(geocode_result)
    script = createScript(lat,lng,radiusToSearch, price, API_KEY)
    nameRestaurants = retrieveRes(URL, script)
    print randomize(nameRestaurants)
   
if __name__ == "__main__":
    main()

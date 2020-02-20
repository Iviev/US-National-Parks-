## proj_nps.py
## Skeleton for Project 2, Winter 2018
## ~~~ modify this file, but don't rename it ~~~

import requests
import json
from bs4 import BeautifulSoup
from secrets import google_places_key
import plotly.plotly as py
import csv

CACHE_FNAME = "cached_state_sites.json"
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
    # if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}


def get_unique_key(url):
  return url
#     #### Implement your function here ####

def make_request_using_cache(url):
    global header
    unique_ident = get_unique_key(url)


    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        header = {'User-Agent': 'SI_CLASS'}
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]



baseurl = 'https://www.nps.gov/index.htm'
page_text = make_request_using_cache(baseurl)
page_soup = BeautifulSoup(page_text, 'html.parser')
content_div = page_soup.find(class_="SearchBar StrataSearchBar")
state_searchbar = content_div.find(class_="container")
state_search= state_searchbar.find(class_="SearchBar-keywordSearch input-group input-group-lg")
state_link = state_search.find("a")["href"]
link = state_link[:7]

class NationalSite():
    def __init__(self, site_type, name, desc, url=None):
        self.type = site_type
        self.name = name
        self.description = desc
        self.url = url
        try:
          national_site_baseurl = baseurl[:19] + self.url + "index.htm"
          national_site_text = make_request_using_cache(national_site_baseurl)
          national_site_soup = BeautifulSoup(national_site_text, 'html.parser')
          national_site_content_div = national_site_soup.find(class_="mailing-address")
          address = national_site_content_div.find(itemprop= "streetAddress").string
          if address != None:
              self.address_street = address[1:-1]
          else:
            self.address_street = ""

          self.address_city = national_site_content_div.find(itemprop= "addressLocality").string
          self.address_state = national_site_content_div.find(itemprop="addressRegion").string
          zipcode = national_site_content_div.find(itemprop= "postalCode").string
          self.address_zip = zipcode[:5]
        except:
          pass





    def __str__(self):
        str_ = self.name +  " (" + self.type + ")" + ": " + self.address_street + ", "+ self.address_city + ", " + self.address_state + " " + self.address_zip
        return str_


class NearbyPlace():
    def __init__(self, name, longitude, latitude):
        self.name = name
        self.longitude = longitude  #added Heidi
        self.latitude = latitude


    def __str__(self):
      return self.name

def get_sites_for_state(state_abbr):
    state_sites_list = []
    state = link + state_abbr + "/index.htm"
    state_url= baseurl[:19] + state
    state_sites_text = make_request_using_cache(state_url)
    sites_soup = BeautifulSoup(state_sites_text, 'html.parser')
    sites_div = sites_soup.find(class_= "col-md-9 col-sm-12 col-xs-12 stateCol")
    for each_state in sites_div.find_all(class_="clearfix"):
        sites_div_class = each_state.find(class_="col-md-9 col-sm-9 col-xs-12 table-cell list_left")
        each_site_type = sites_div_class.find("h2").string
        each_site_name = sites_div_class.find("h3").string
        each_site_description = sites_div_class.find("p").string
        each_site_url_end = sites_div_class.find("a")["href"]
        each_site_instance = NationalSite(site_type= each_site_type, name= each_site_name, desc= each_site_description, url = each_site_url_end)
        state_sites_list.append(each_site_instance) #

    return state_sites_list


def params_unique_combination(baseurl,parameters):
	alphabetized_keys = sorted(parameters.keys())
	res = []
	for k in alphabetized_keys:
			res.append("{}-{}".format(k, parameters[k]))
	return baseurl + "_".join(res)



def get_nearby_places_for_site(national_site):
  location_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

  # params_diction = {'query':nearby_search_param}
  # 'query':nearby_search_param

  nearby_search_param = national_site.name.replace(" ", "+")
  # nearby_search_url = location_url + "query="+nearby_search_param + "&" + "key=" + google_places_key
  params_diction = {}
  params_diction["key"] = google_places_key
  params_diction["query"] = nearby_search_param

  unique_identifier = params_unique_combination(location_url, params_diction)
  if unique_identifier in CACHE_DICTION:
    print("Getting Data from Cache")
		# return CACHE_DICTION[unique_identifier]
  else:
    print("Making request to Text Search API")
    response = requests.get(location_url, params= params_diction)
    content = response.text
    python_obj = json.loads(content)
    CACHE_DICTION[unique_identifier] = python_obj
    dumped_json_cache = json.dumps(CACHE_DICTION)
    f = open(CACHE_FNAME, "w")
    f.write(dumped_json_cache)
    f.close()
  #
  # nearby_api_info = requests.get(nearby_search_url).text
  # python_obj = json.loads(nearby_api_info)
  for item in CACHE_DICTION[unique_identifier]["results"]:
  # nearby_places_location = [0]["geometry"]["location"]
    nearby_places_latitude = str(item["geometry"]["location"]["lat"])
    nearby_places_longitude = str(item["geometry"]["location"]["lng"])

    nearby_location = nearby_places_latitude + "," + nearby_places_longitude
    radius = str(10*1000)

  nearby_location_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
  nearby_params_diction = {}
  nearby_params_diction["key"] = google_places_key
  nearby_params_diction["location"] = nearby_location
  nearby_params_diction["radius"] = radius


  unique_identifier2 = params_unique_combination(nearby_location_url, nearby_params_diction)
  if unique_identifier2 in CACHE_DICTION:
      print("Getting data from Cache")

  else:
    print("Making request to API")
    response2 = requests.get(nearby_location_url, params= nearby_params_diction)
  		# new_response = response.url
    content2 = response2.text
    final_python_obj = json.loads(content2)
    CACHE_DICTION[unique_identifier2] = final_python_obj
    dumped_json_cache2 = json.dumps(CACHE_DICTION)
    f = open(CACHE_FNAME, "w")
    f.write(dumped_json_cache2)
    f.close()

  nearby_place_list = []
  for places in CACHE_DICTION[unique_identifier2]["results"]:
    if places["name"] != None:
      place_name = places["name"]
      nearby_places_latitude = str(places["geometry"]["location"]["lat"])
      nearby_places_longitude = str(places["geometry"]["location"]["lng"])
      nearby_place_instance = NearbyPlace(place_name, nearby_places_longitude, nearby_places_latitude)
      nearby_place_list.append(nearby_place_instance)
    else:
      pass

  return nearby_place_list


# nearby_places_list = []
# site_object1 = NationalSite("park", "Isle Royale", "Abc", "/isro/")
#
# places_info = get_nearby_places_for_site(site_object1)
# for nearby_places in places_info:
#   print(nearby_places.longitude)
  # print(places_info.longitude)
# print(get_sites_for_state("mi"))




def get_longitude_latitude(national_site):

  location_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

  nearby_search_param = national_site.name.replace(" ", "+")
  # nearby_search_url = location_url + "query="+nearby_search_param + "&" + "key=" + google_places_key
  params_diction = {}
  params_diction["key"] = google_places_key
  params_diction["query"] = nearby_search_param

  unique_identifier = params_unique_combination(location_url, params_diction)
  if unique_identifier in CACHE_DICTION:
    print("Getting Data from Cache")
		# return CACHE_DICTION[unique_identifier]
  else:
    print("Making request to Text Search API")
    response = requests.get(location_url, params= params_diction)
    content = response.text
    python_obj = json.loads(content)
    CACHE_DICTION[unique_identifier] = python_obj
    dumped_json_cache = json.dumps(CACHE_DICTION)
    f = open(CACHE_FNAME, "w")
    f.write(dumped_json_cache)
    f.close()
  #
  # nearby_api_info = requests.get(nearby_search_url).text
  # python_obj = json.loads(nearby_api_info)
  lat_long_list = []
  for item in CACHE_DICTION[unique_identifier]["results"]:
  # nearby_places_location = [0]["geometry"]["location"]
    nearby_places_latitude = item["geometry"]["location"]["lat"]
    nearby_places_longitude = item["geometry"]["location"]["lng"]
    lat_long_list.append(nearby_places_latitude)
    lat_long_list.append(nearby_places_longitude)
    lat_long_list.append(national_site.name)


  return lat_long_list





def plot_sites_for_state(state_abbr):
  lst = []
  long_list = []
  lat_list = []
  text_list = []
  state_national_sites = get_sites_for_state(state_abbr)
  for each_site in state_national_sites:
    site_location = get_longitude_latitude(each_site)
    if site_location != []:
      # site_location = get_longitude_latitude(each_site)
      lat_list.append(site_location[0])
      long_list.append(site_location[1])
      text_list.append(site_location[2])
      # site_location = get_longitude_latitude(each_site

    else:
      pass



  min_lat = 10000
  max_lat = -10000
  min_lon = 10000
  max_lon = -10000



  for str_v in lat_list:
      v = float(str_v)
      if v < min_lat:
          min_lat = v
      if v > max_lat:
          max_lat = v
  for str_v in long_list:
      v = float(str_v)
      if v < min_lon:
          min_lon = v
      if v > max_lon:
          max_lon = v



  data = [ dict(
          type = 'scattergeo',
          locationmode = 'USA-national-sites',
          lon = long_list, #this is actually the longitude
          lat = lat_list,
          text = text_list,
          mode = 'markers',
          hoverinfo = 'text',
          marker = dict(
              size = 8,
              symbol = 'star',
              color = 'red'
          ))]




  max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon)) # finds the maximum between the two long/lat
  padding = max_range * .10 # adds padding
  lat_axis = [min_lat - padding, max_lat + padding] # altogehter, fixes crowding problem from previous views. Some breathing room for top and bottom values in map view
  lon_axis = [min_lon - padding, max_lon + padding]

  center_lat = (max_lat+min_lat) / 2 # specifies view to center within bounding box, zooming out of previous view
  center_lon = (max_lon+min_lon) / 2

  layout = dict(
          title = 'US National Sites<br>(Hover for site names)',
          geo = dict(
              scope='usa',
              projection=dict( type='albers usa' ),
              showland = True,
              landcolor = "rgb(250, 250, 250)",
              subunitcolor = "rgb(100, 217, 217)",
              countrycolor = "rgb(217, 100, 217)",
              lataxis = {'range': lat_axis},
              lonaxis = {'range': lon_axis},
              center= {'lat': center_lat, 'lon': center_lon },
              countrywidth = 3,
              subunitwidth = 3
          ),
      )
  #
  #
  fig = dict(data=data, layout=layout )
  py.plot( fig, validate=False, filename='national - sites for ' + state_abbr)


  return None

def plot_nearby_for_site(site_object):

    long_list = []
    lat_list = []
    text_list = []
    nearby_places_lat = []
    nearby_places_lon = []
    nearby_places_text = []
    # nearby_places_site = get_longitude_latitude(site_object)
    # print(state_national_sites)
    # for each_site in nearby_places_site:
    site_location = get_longitude_latitude(site_object)
      # print(site_location)
    if site_location != []:
      lat_list.append(site_location[0])
      long_list.append(site_location[1])
      text_list.append(site_location[2])
    else:
      pass

    nearby_places_location_list = get_nearby_places_for_site(site_object)
    for places in nearby_places_location_list:
      if places != []:
        nearby_places_lat.append(places.latitude)
        nearby_places_lon.append(places.longitude)
        nearby_places_text.append(places.name)

      else:
        pass
      # print(nearby_places_lat)
      # print(nearby_places_lon)

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    lat_vals = lat_list + nearby_places_lat
    lon_vals = long_list + nearby_places_lon


    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v



    trace1 = dict(
            type = 'scattergeo',
            locationmode = 'USA national site',
            lon = long_list,
            lat = lat_list,
            text = text_list,
            mode = 'markers',
            marker = dict(
                size = 20,
                symbol = 'star',
                color = 'red'
            ))
    trace2 = dict(
            type = 'scattergeo',
            locationmode = 'Nearby-places ',
            lon = nearby_places_lon,
            lat = nearby_places_lat,
            text = nearby_places_text,
            mode = 'markers',
            marker = dict(
                size = 8,
                symbol = 'circle',
                color = 'blue'
            ))

    data2 = [trace1, trace2]


    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon)) # finds the maximum between the two long/lat
    padding = max_range * .10 # adds padding
    lat_axis = [min_lat - padding, max_lat + padding] # altogehter, fixes crowding problem from previous views. Some breathing room for top and bottom values in map view
    lon_axis = [min_lon - padding, max_lon + padding]

    center_lat = (max_lat+min_lat) / 2 # specifies view to center within bounding box, zooming out of previous view
    center_lon = (max_lon+min_lon) / 2

    layout = dict(
            title = 'Nearby places<br>(Hover for nearby places names)',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center= {'lat': center_lat, 'lon': center_lon },
                countrywidth = 3,
                subunitwidth = 3
            ),
        )


    fig = dict(data=data2, layout=layout )
    py.plot( fig, validate=False, filename='Nearby Places:' + site_object.name)


if __name__ == "__main__":


  states = ["al", "ak", "az", "ar", "ca", "co", "ct", "dc", "de", "fl", "ga",
            "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md",
            "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
            "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc",
            "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"]
  sites_dict = {}
  nearby_places_dict = {}
  command_option_list = "\tlist <stateabbr> \n\t\tavailable anyitme \n\t\tlists all National Sites in a state \n\t\tvalid inputs: a two-letter abreviation"
  command_option_nearby = "\tnearby <result_number> \n\t\tavailable only if there is an active result set \n\t\tlists all Places nearby a given result \n\t\tvalid inputs: an ineger 1-len(result-set-size)"
  command_option_map = "\tmap \n\t\tavailble only if there is an active site or nearby result set \n\t\t displays the current results on a map"
  command_options_exit = "\texit \n\t\texits the program"
  command_option_help = "\thelp \n\t\tlists avaialble commands(these instructions)"
  #
  # print("Here are your options: \n")
  # print(command_option_list)
  # print(command_option_nearby)
  # print(command_option_map)
  # print(command_options_exit)
  # print(command_option_help)
  #
  #

  myboolean = True
  while myboolean == True:
    user_input1 = input("Enter command or 'help' for options:")
    if user_input1 == "exit":
      break
#HELP COMES FIRST, HOW DO I TIE THAT INTO MY OVERALL FUNCTION.

    elif user_input1.lower()[:4] == "list":
      if user_input1.lower()[-2:] in states: #getting the sites for each state
        state_site_search = get_sites_for_state(user_input1.lower()[-2:])
        count = 0
        print("National Sites " + user_input1.upper()[-2:])
        for each_site_search in state_site_search:
          count+= 1
          print(str(count) + ". " + each_site_search.__str__())
          sites_dict[count] = each_site_search
        user_input_nat_sites = input("Enter command or 'help' for options:")
        if user_input_nat_sites == "map":
          plot_sites_for_state(user_input1.lower()[-2:])
        elif user_input_nat_sites[:4] == "exit":
          print("Quitting Search")
          break
        elif user_input_nat_sites[:4] == "help":
          print("Here are your options: \n")
          print(command_option_list)
          print(command_option_nearby)
          print(command_option_map)
          print(command_options_exit)
          print(command_option_help)
          break

        else:
          print("This function is not availble")



        user_input2 = input("Enter nearby for more info:")
        # if user_input2[:6] == "nearby":
        nearby_int  = int(user_input2[-2:])
        # print(nearby_int)
        if nearby_int in (range(1,(len(sites_dict) + 1))):
          if nearby_int in sites_dict.keys():
            nearby_places_interactive = get_nearby_places_for_site(sites_dict[nearby_int])
            count2 = 0
            # print("Places nearby" + user_input1.upper())
            for each_nearby_place in nearby_places_interactive:
              count2+= 1
              print(str(count2) + ". " + each_nearby_place.__str__())
              nearby_places_dict[count2] = each_nearby_place
            # print(nearby_places_dict)

            if nearby_places_interactive != None:  #----- copy this to project page
              user_input3 = input("Enter map to view map, or help for options:")
              if user_input3 == "map":
              # mapping_int = int(user_input3[-2:]) ----- map int from before in the dict
                if nearby_int in sites_dict.keys():
                  mapped_nearby = plot_nearby_for_site(sites_dict[nearby_int]) #--- changed from nearby sites to sites_dict
              elif user_input3[:4] == "help":
                print("Here are your options: \n")
                print(command_option_list)
                print(command_option_nearby)
                print(command_option_map)
                print(command_options_exit)
                print(command_option_help)

              elif user_input3[:4] == "exit":
                print("Quitting search")
                break


            else:
              print("No Places nearby this site")
              break

        else:
          nearby_int not in (range(1,(len(sites_dict) + 1)))
          print("Out of range, enter (list<state_abbr>) to search again")
        # elif user_input2[:4] == "exit":
        #   break

      else:
        print("Please input the state abbreviation (list<state_abbr>)")


    elif user_input1.lower()[:4] == "exit":
      break

    elif user_input1.lower()[:4] == "help":
      print("Here are your options: \n")
      print(command_option_list)
      print(command_option_nearby)
      print(command_option_map)
      print(command_options_exit)
      print(command_option_help)
      #
    else:
      print("That's an invalid entry, please input a valid search term or enter 'help' or exit to quit")
      continue

    #   user_input1 == "help"
    #   print("Enter 'list(state)' for more information about the state site \n Map to display the maps of the sites \n Exit to quit")

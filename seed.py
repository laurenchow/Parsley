import model
import csv

# more_example_data = [{u'category_labels': [[u'Social', u'Food and Dining', u'Restaurants', u'American'], [u'Social', u'Food and Dining', u'Restaurants', u'Seafood'], [u'Landmarks']], u'meal_lunch': True, u'alcohol_beer_wine': True, u'rating': 4, u'reservations': True, u'alcohol_bar': True, u'options_organic': True, u'postcode': u'94121', u'parking': True, u'neighborhood': [u'Richmond District', u'Outer Richmond', u'Lincoln Park - Lobos', u'Northwest', u'Richmond', u'Northwest San Francisco', u'san francisco', u'Sutro Heights', u'Point Bonita'], u'groups_goodfor': True, u'parking_free': True, u'cuisine': [u'Bistro', u'Seafood', u'American', u'Californian', u'Mediterranean'], u'meal_dinner': True, u'alcohol': True, u'locality': u'San Francisco', u'parking_valet': True, u'payment_cashonly': False, u'category_ids': [348, 364, 107], u'attire': u'casual', u'latitude': 37.778512, u'email': u'ralph@cliffhouse.com', u'tel': u'(415) 386-3330', u'website': u'http://www.cliffhouse.com', u'fax': u'(415) 387-7837', u'options_healthy': True, u'meal_takeout': True, u'meal_breakfast': True, u'price': 4, u'meal_cater': True, u'hours': {u'monday': [[u'9:00', u'21:30']], u'tuesday': [[u'9:00', u'21:30']], u'friday': [[u'9:00', u'21:30']], u'wednesday': [[u'9:00', u'21:30']], u'thursday': [[u'9:00', u'21:30']], u'sunday': [[u'8:30', u'21:30']], u'saturday': [[u'9:00', u'21:30']]}, u'factual_id': u'89dc424d-b27a-4203-a5c7-ea3620067cfe', u'hours_display': u'Mon-Sat 9:00 AM-9:30 PM; Sun 8:30 AM-9:30 PM', u'room_private': True, u'kids_goodfor': True, u'parking_lot': True, u'parking_street': True, u'smoking': False, u'open_24hrs': False, u'name': u'Cliff House', u'country': u'us', u'region': u'CA', u'wifi': False, u'accessible_wheelchair': True, u'longitude': -122.513894, u'meal_deliver': False, u'address': u'1090 Point Lobos Ave', u'options_vegetarian': True}, {u'category_labels': [[u'Social', u'Entertainment', u'Movie Theatres'], [u'Social', u'Food and Dining', u'Restaurants']], u'meal_lunch': True, u'neighborhood': [u'Downtown / Union Square', u'South Of Market', u'South Beach', u'Financial District', u'Financial District South', u'Downtown San Francisco', u'san francisco', u'soma', u'Union Square', u'NOMA', u'SoMa (South of Market)', u'Central East'], u'rating': 4.5, u'reservations': True, u'address': u'701 Mission St', u'postcode': u'94103', u'parking': True, u'tel': u'(415) 978-2787', u'seating_outdoor': True, u'cuisine': [u'Tea', u'Sandwiches', u'International', u'Cafe'], u'meal_dinner': True, u'locality': u'San Francisco', u'payment_cashonly': False, u'category_ids': [332, 347], u'attire': u'casual', u'latitude': 37.785466, u'email': u'help@samovarlife.com', u'website': u'http://www.ybca.org/', u'fax': u'(415) 543-1755', u'meal_takeout': True, u'meal_breakfast': True, u'price': 2, u'meal_cater': True, u'hours': {u'monday': [[u'10:00', u'20:00']], u'tuesday': [[u'10:00', u'20:00']], u'friday': [[u'10:00', u'21:00']], u'wednesday': [[u'10:00', u'20:00']], u'thursday': [[u'10:00', u'21:00']], u'sunday': [[u'10:00', u'20:00']], u'saturday': [[u'10:00', u'21:00']]}, u'factual_id': u'fce56388-90c9-4003-af01-3d9ee1e6954f', u'hours_display': u'Mon-Wed 10:00 AM-8:00 PM; Thu-Sat 10:00 AM-9:00 PM; Sun 10:00 AM-8:00 PM', u'kids_goodfor': True, u'parking_lot': True, u'parking_street': True, u'open_24hrs': False, u'name': u'Yerba Buena Center for the Arts', u'country': u'us', u'region': u'CA', u'longitude': -122.402062, u'options_glutenfree': True}, {u'category_labels': [[u'Social', u'Bars'], [u'Social', u'Food and Dining', u'Restaurants', u'Burgers'], [u'Social', u'Entertainment', u'Night Clubs']], u'meal_lunch': True, u'alcohol_beer_wine': True, u'rating': 4.5, u'reservations': False, u'alcohol_bar': True, u'postcode': u'94103', u'parking': True, u'neighborhood': [u'Mission', u'Mission Dolores', u'Central', u'Mission Dolores (Hub', u'Mid-Market)', u'Central San Francisco', u'Mission District', u'The Hub', u'somamission', u'san francisco', u'the mission', u'Deco Ghetto', u'Duboce Triangle'], u'groups_goodfor': True, u'cuisine': [u'Burgers', u'Pub Food', u'American', u'Barbecue', u'Continental'], u'meal_dinner': True, u'alcohol': True, u'locality': u'San Francisco', u'payment_cashonly': True, u'category_ids': [312, 351, 334], u'attire': u'casual', u'latitude': 37.770022, u'email': u'info@zeitgeistsf.com', u'tel': u'(415) 255-7505', u'website': u'http://www.zeitgeistsf.com', u'options_healthy': True, u'meal_takeout': True, u'meal_breakfast': True, u'price': 2, u'hours': {u'monday': [[u'00:00', u'2:00'], [u'9:00', u'23:59']], u'tuesday': [[u'00:00', u'2:00'], [u'9:00', u'23:59']], u'friday': [[u'00:00', u'2:00'], [u'9:00', u'23:59']], u'wednesday': [[u'00:00', u'2:00'], [u'9:00', u'23:59']], u'thursday': [[u'00:00', u'2:00'], [u'9:00', u'23:59']], u'sunday': [[u'00:00', u'2:00'], [u'9:00', u'23:59']], u'saturday': [[u'00:00', u'2:00'], [u'9:00', u'23:59']]}, u'factual_id': u'019a576e-5590-4bee-b315-87e48c648382', u'hours_display': u'Open Daily 12:00 AM-2:00 AM, 9:00 AM-11:59 PM', u'smoking': False, u'parking_street': True, u'open_24hrs': False, u'name': u'Zeitgeist', u'country': u'us', u'region': u'CA', u'wifi': False, u'accessible_wheelchair': True, u'longitude': -122.422207, u'meal_deliver': False, u'seating_outdoor': True, u'address': u'199 Valencia St', u'options_vegetarian': True}, {u'category_labels': [[u'Social', u'Food and Dining', u'Restaurants', u'Burgers'], [u'Social', u'Food and Dining', u'Cafes, Coffee and Tea Houses'], [u'Social', u'Food and Dining', u'Bakeries']], u'tel': u'(415) 252-0800', u'alcohol_beer_wine': False, u'rating': 4, u'address': u'375 Valencia St', u'postcode': u'94103', u'parking': True, u'neighborhood': [u'Mission Dolores', u'Mission', u'Central', u'Mission Dolores (Hub', u'Mid-Market)', u'Mission District', u'san francisco', u'the mission'], u'seating_outdoor': True, u'cuisine': [u'Coffee', u'Cafe', u'Tea', u'cafe', u'coffee'], u'alcohol': False, u'locality': u'San Francisco', u'payment_cashonly': False, u'category_ids': [351, 342, 340], u'alcohol_byob': False, u'alcohol_bar': False, u'attire': u'casual', u'latitude': 37.767027, u'email': u'info@fourbarrelcoffee.com', u'website': u'http://www.fourbarrelcoffee.com', u'options_healthy': True, u'meal_takeout': True, u'price': 1, u'hours': {u'monday': [[u'7:00', u'20:00']], u'tuesday': [[u'7:00', u'20:00']], u'friday': [[u'7:00', u'20:00']], u'wednesday': [[u'7:00', u'20:00']], u'thursday': [[u'7:00', u'20:00']], u'sunday': [[u'7:00', u'20:00']], u'saturday': [[u'7:00', u'20:00']]}, u'factual_id': u'2fb18c5e-45cf-42a1-b7da-f13f74d92239', u'hours_display': u'Open Daily 7:00 AM-8:00 PM', u'kids_goodfor': True, u'parking_street': True, u'open_24hrs': False, u'name': u'Fourbarrel Coffee', u'country': u'us', u'region': u'CA', u'wifi': True, u'accessible_wheelchair': True, u'longitude': -122.421957, u'meal_deliver': False, u'options_vegetarian': True}, {u'category_labels': [[u'Social', u'Food and Dining', u'Restaurants', u'American'], [u'Social', u'Food and Dining', u'Restaurants', u'Burgers'], [u'Social', u'Food and Dining', u'Restaurants', u'Seafood']], u'meal_lunch': True, u'alcohol_beer_wine': True, u'rating': 4, u'reservations': True, u'alcohol_bar': True, u'postcode': u'94107', u'parking': True, u'neighborhood': [u'SOMA', u'South Beach', u'South Park', u'somamission', u'san francisco', u'Rincon Hill', u'South Of Market', u'Financial District South', u'Central East'], u'groups_goodfor': True, u'cuisine': [u'Cafe', u'Pub Food', u'American', u'Burgers', u'Pizza'], u'meal_dinner': True, u'alcohol': True, u'locality': u'San Francisco', u'payment_cashonly': False, u'category_ids': [348, 351, 364], u'attire': u'casual', u'latitude': 37.782415, u'email': u'contact@21st-amendment.com', u'tel': u'(415) 369-0900', u'website': u'http://www.21st-amendment.com', u'fax': u'(415) 369-0909', u'options_healthy': True, u'meal_takeout': True, u'meal_breakfast': True, u'price': 2, u'hours': {u'monday': [[u'11:30', u'23:59']], u'tuesday': [[u'11:30', u'23:59']], u'friday': [[u'11:30', u'23:59']], u'wednesday': [[u'11:30', u'23:59']], u'thursday': [[u'11:30', u'23:59']], u'sunday': [[u'00:00', u'1:00'], [u'10:00', u'23:59']], u'saturday': [[u'00:00', u'1:00'], [u'11:30', u'23:59']]}, u'factual_id': u'44304903-661d-49f1-adbb-c0a73eaf886c', u'hours_display': u'Mon-Fri 11:30 AM-11:59 PM; Sat 12:00 AM-1:00 AM, 11:30 AM-11:59 PM; Sun 12:00 AM-1:00 AM, 10:00 AM-11:59 PM', u'smoking': False, u'parking_street': True, u'open_24hrs': False, u'name': u'21st Amendment Brewery Cafe', u'country': u'us', u'region': u'CA', u'wifi': True, u'accessible_wheelchair': True, u'longitude': -122.392576, u'meal_deliver': True, u'seating_outdoor': True, u'address': u'563 2nd St', u'options_vegetarian': True}]
# true is 1 false is 0

# example_data = {'category_labels': [['Social', 'Food and Dining', 'Restaurants', 'American'], 
# ['Social', 'Food and Dining', 'Restaurants', 'Seafood'], ['Landmarks']], 
# 'meal_lunch': 1, 'alcohol_beer_wine': 1, 'rating': 4, 'reservations': 1, 
# 'alcohol_bar': 1, 'options_organic': 1, 'postcode': '94121', 'parking': 1, 
# 'neighborhood': ['Richmond District', 'Outer Richmond', 'Lincoln Park - Lobos', 'Northwest', 'Richmond', 'Northwest San Francisco', 'san francisco', 'Sutro Heights', 'Point Bonita'], 
# 'groups_goodfor': 1, 'parking_free': 1, 'cuisine': ['Bistro', 'Seafood', 'American', 'Californian', 'Mediterranean'], 
# 'meal_dinner': 1, 'alcohol': 1, 'locality': 'San Francisco', 'parking_valet': 1, 
# 'payment_cashonly': 0, 'category_ids': [348, 364, 107], 'attire': 'casual', 'latitude': 37.778512, 
# 'email': 'ralph@cliffhouse.com', 'tel': '(415) 386-3330', 'website': 'http://www.cliffhouse.com', 
# 'fax': '(415) 387-7837', 'options_healthy': 1, 'meal_takeout': 1, 'meal_breakfast': 1,
# 'price': 4, 'meal_cater': 1, 'hours': {'monday': [['9:00', '21:30']], 'tuesday': [['9:00', '21:30']], 'friday': [['9:00', '21:30']], 'wednesday': [['9:00', '21:30']], 'thursday': [['9:00', '21:30']], 'sunday': [['8:30', '21:30']], 'saturday': [['9:00', '21:30']]}, 
# 'factual_id': '89dc424d-b27a-4203-a5c7-ea3620067cfe', 'hours_display': 'Mon-Sat 9:00 AM-9:30 PM; Sun 8:30 AM-9:30 PM', 'room_private': 1, 
# 'kids_goodfor': 1, 'parking_lot': 1, 'parking_street': 1, 'smoking': 0, 'open_24hrs': 0, 
# 'name': 'Cliff House', 'country': 'us', 'region': 'CA', 'wifi': 0, 'accessible_wheelchair': 1, 'longitude': -122.513894, 
# 'meal_deliver': 0, 'address': '1090 Point Lobos Ave', 'options_vegetarian': 1}

example_data = {'category_labels': [['Social', 'Food and Dining', 'Restaurants', 'American'], 
['Social', 'Food and Dining', 'Restaurants', 'Seafood'], ['Landmarks']], 
'meal_lunch': True, 'alcohol_beer_wine': True, 'rating': 4, 'reservations': True, 
'alcohol_bar': True, 'options_organic': True, 'postcode': '94121', 'parking': True, 
'neighborhood': ['Richmond District', 'Outer Richmond', 'Lincoln Park - Lobos', 'Northwest', 'Richmond', 'Northwest San Francisco', 'san francisco', 'Sutro Heights', 'Point Bonita'], 
'groups_goodfor': True, 'parking_free': True, 'cuisine': ['Bistro', 'Seafood', 'American', 'Californian', 'Mediterranean'], 
'meal_dinner': True, 'alcohol': True, 'locality': 'San Francisco', 'parking_valet': True, 
'payment_cashonly': False, 'category_ids': [348, 364, 107], 'attire': 'casual', 'latitude': 37.778512, 
'email': 'ralph@cliffhouse.com', 'tel': '(415) 386-3330', 'website': 'http://www.cliffhouse.com', 
'fax': '(415) 387-7837', 'options_healthy': True, 'meal_takeout': True, 'meal_breakfast': True,
'price': 4, 'meal_cater': True, 'hours': {'monday': [['9:00', '21:30']], 'tuesday': [['9:00', '21:30']], 'friday': [['9:00', '21:30']], 'wednesday': [['9:00', '21:30']], 'thursday': [['9:00', '21:30']], 'sunday': [['8:30', '21:30']], 'saturday': [['9:00', '21:30']]}, 
'factual_id': '89dc424d-b27a-4203-a5c7-ea3620067cfe', 'hours_display': 'Mon-Sat 9:00 AM-9:30 PM; Sun 8:30 AM-9:30 PM', 'room_private': True, 
'kids_goodfor': True, 'parking_lot': True, 'parking_street': True, 'smoking': False, 'open_24hrs': False, 
'name': 'Cliff House', 'country': 'us', 'region': 'CA', 'wifi': False, 'accessible_wheelchair': True, 'longitude': -122.513894, 
'meal_deliver': False, 'address': '1090 Point Lobos Ave', 'options_vegetarian': True}


def load_users(session):
    with open('seed_data/u.user', 'rb') as csvfile:
        user_table = csv.reader(csvfile, delimiter='|')
        for row in user_table:
            new_user = model.User(id = row[0], age = row[1], gender = row[2], occupation = row[3], zip = row[4], email = row[5]) 
            session.add(new_user)




def load_restaurants(session):
  # with open('seed_data/example_data', 'rb') as csvfile:
  #   item_table= csv.reader(csvfile, delimiter='\t')
    
    # for entry in more_example_data:

      new_restaurant = model.Restaurant(name = example_data['name'],
      # address_extended = example_data['address_extended'],
      address = example_data['address'],
      # attire = example_data['attire'],
      # attire_prohibited = example_data['attire_prohibited'],
      # attire_required = example_data['attire_required'],
      # chain_id = example_data['chain_id'],
      # chain_name = example_data['chain_name'],
      country = example_data['country'],
      email = example_data['email'],
      factual_id = example_data['factual_id'],
      # fax = example_data['fax'],
      # founded = example_data['founded'],
      # hours = example_data['hours'],
      # hours_display = example_data['hours_d'],
      latitude =  example_data['latitude'],
      locality = example_data['locality'],
      longitude = example_data['longitude'],
      # owner = example_data['owner'],
      # po_box = example_data['po_box'],
      postcode = example_data['postcode'],
      price = example_data['price'],
      rating = example_data['rating'],
      region =  example_data['region'],
      tel = example_data['tel'],
      website = example_data['website'])

      session.add(new_restaurant)
 

def load_restaurant_features(session):
  # with open('seed_data/example_data', 'rb') as csvfile:
  #   item_table= csv.reader(csvfile, delimiter='\t')
    
  #   for row in feature_table:
      new_restaurant_features= model.Restaurant_Features(accessible_wheelchair = example_data['accessible_wheelchair'], 
      # alcohol_byob = example_data['alcohol_byob'],
      alcohol_bar = example_data['alcohol_bar'], 
      alcohol_beer_wine = example_data['alcohol_beer_wine'],
      alcohol= example_data['alcohol'],
      # groups_goodfor= example_data['groups_goodfor'],
      # kids_goodfor= example_data['kids_goodfor'],
      # kids_menu = example_data['kids_menu'],
      # meal_breakfast= example_data['meal_breakfast'],   
      # meal_cater= example_data['meal_cater'],
      # meal_deliver= example_data['meal_deliver'],
      # meal_dinner= example_data['meal_dinner'], 
      # meal_lunch = example_data['meal_lunch'],
      # meal_takeout= example_data['meal_takeout'],
      # open_24hrs= example_data['open_24hrs'],
      # options_glutenfree  = example_data['options_glutenfree'],
      # options_lowfat  = example_data['options_lowfat'],
      # options_organic = example_data['options_organic'],
      # options_healthy= example_data['options_healthy'],
      # options_vegan= example_data['options_vegan'],
      # options_vegetarian= example_data['options_vegetarian'],
      # parking = example_data['parking'],
      # parking_free = example_data['parking_free'],
      # parking_garage = example_data['parking_garage'],
      # parking_lot = example_data['parking_lot'],
      # parking_street= example_data['parking_street'],
      # parking_valet= example_data['parking_valet'], 
      # parking_validated = example_data['parking_validated'],
      # payment_cashonly = example_data['payment_cashonly'],
      reservations =  example_data['reservations'],
      # room_private= example_data['room_private'],
      # seating_outdoor= example_data['seating_outdoor'],
      # smoking= example_data['smoking'],
      wifi= example_data['wifi'])

      session.add(new_restaurant_features)

  
                  
        
def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(session)
    load_restaurants(session) 
    load_restaurant_features(session)
    session.commit()

if __name__ == "__main__":
    s = model.connect()
    main(s) 
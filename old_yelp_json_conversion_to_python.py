import json
import model

#work on this when you are ready for machine learning so you have a database with 
#enough data to make some interesting stuff

def add_restaurants(session):
  json_data=open("static/yelp_academic_dataset_business.json")

  # with json_data as myfile:
  for line in json_data:
    restaurant_data = json.loads(line)
    name = restaurant_data.get("name", None)
    business_id = restaurant_data.get("business_id", None)
    full_address = restaurant_data.get("full_address", None)
    city = restaurant_data.get("city", None)
    latitude = restaurant_data.get("latitude", None)
    longitude = restaurant_data.get("longitude", None)
    # neighborhoods = restaurant_data.get("neighborhoods", None)
    # if neighborhoods != []:

    stars = restaurant_data.get("longitude", None)
    state = restaurant_data.get("state", None)
    review_count = restaurant_data.get("review_count", None)
    is_still_open = restaurant_data.get("is_still_open", None)
    #these are likely to be lists and a problem unless unpacked -- will need to put in another table
    categories = restaurant_data.get("categories", None)
    if "Restaurants" in categories:
      restaurant = 1
        
        afghan = 
        african = 
        american_new
        american_trad 
        arabian
        argentine 
        armenian 
        asian_fusion
        bangladeshi
        barbeque
        basque
        belgian
        brasseries
        brazilian
        breakfast_brunch
        british
        buffet
        burgers
        burmese
        cafe
        cafeteria
        cajun_creole
        cambodian
        caribbean
        catalan
        cheesesteaks
        chicken_wings
        chinese
        comfort_food
        creperies
        cuban
        czech
        delis 
        diners
        ethiopian
        fast_food
        filipino
        fish_chips
        food_court
        food_stands
        french
        gastropubs
        german
        gluten_free
        greek
        halal
        hawaiian
        himalayan_nepa
        hot_dogs
        hot_pot
        hungarian
        iberian
        indian
        indonesian
        irish
        italian
        japanese
        koraen
        kosher
        laotian
        lat_am
        live_raw
        malaysian
        mediterranean
        mexican
        middle_eastern
        modern_euro
        mongolian
        pakistani
        persian
        peruvian
        pizza
        polish
        portuguese
        russian
        salad
        sandwiches
        scandinavian
        scottish
        seafood
        singaporean
        slovakian
        soul_food
        soup
        southern
        spanish
        steakhouses
        sushi_bars
        taiwanese
        tapas_bars
        tapas_small
        texmex
        thai
        turkish
        ukranian
        vegan 
        vegetarian 
        vietnamese 

    if "Food" in categories:
      food = 1
      # these are secondary categories for foods:
      #Bagels
      # Bakeries
      # Beer, Wine & Spirits
      # Breweries
      # Bubble Tea
      # Butcher
      # CSA
      # Coffee & Tea
      # Convenience Stores
      # Desserts
      # Do-It-Yourself Food
      # Donuts
      # Farmers Market
      # Food Delivery Services
      # Food Trucks
      # Gelato
      # Grocery
      # Ice Cream & Frozen Yogust
      # Internet Cafes
      # Juice Bars & Smoothies
      # Pretzels
      # Shaved Ice
      # Specialty Food
      # Street Vendors
      # Tea Rooms
      # Wineries
    if "Nightlife" in categories:
      nightlife = 1
      # secondary categories:
      #Adult Entertainment
      # Bars
      # Comedy Clubs
      # Country Dance Halls
      # Dance Clubs
      # Jazz& Blues
      # Karaoke
      # Music Venues
      # Piano Bars
      # Pool Halls
      # tertiary: 
        # Champagne Bars
        # Cocktail Bars
        # Dive Bars
        # Gay Bars
        # Hookah Bars
        # Lounges
        # Pubs
        # Sports Bars
      # Wine Bars
    if categories ==[]:
      print "Ugh."
    # timestamp = strftime

    new_business = model.Yelp_Business(name = name, business_id = business_id, 
    full_address = full_address, city = city, latitude = latitude, 
    longitude = longitude, stars = stars, review_count = review_count, 
    is_still_open = is_still_open, state = state)
  
    model.session.add(new_business)
    print "Here's what got added %r" % new_business

   
    
    "categories": ["Restaurants"], 
    "attributes": {"Take-out": true, "Good For": {"dessert": false, "latenight": false, "lunch": true, "dinner": false, "breakfast": false, "brunch": false}, 
    "Caters": false, 
    "Noise Level": "average", 
    "Takes Reservations": false, 
    "Delivery": false, 
    "Ambience": {"romantic": false, "intimate": false, "touristy": false, "hipster": false, "divey": false, "classy": false, "trendy": false, "upscale": false, "casual": false}, 
    "Parking": {"garage": false, "street": false, "validated": false, "lot": true, "valet": false}, 
    "Has TV": true, 
    "Outdoor Seating": false, 
    "Attire": "casual", 
    "Alcohol": "none", 
    "Waiter Service": true, 
    "Accepts Credit Cards": true, 
    "Good for Kids": true, 
    "Good For Groups": true, 
    "Price Range": 1}, 

    "type": "business"}
  model.session.commit()    
  json_data.close() 

      # business_neighborhood = python_data['neighborhoods'] add this later, not in example data
      # print "Here's what is in hoods %r" % python_data['neighborhoods']
      # if business_neighborhood != []:
      #   print "This works so far %r" % business_neighborhood[1]
      # else: 
      #   print "This is empty, see? %r" % business_neighborhood
    

def add_reviews(session):
  json_data=open("static/yelp_academic_dataset_reviews_small.json")

  for line in json_data:
    review_data = json.loads(line)
    stars = review_data.get("stars", None)
    business_id = review_data.get("business_id", None)
    user_id = review_data.get("user_id", None) 
    date = review_data.get("date", None)
    votes_funny = review_data.get("votes[funny]", None)
    votes_useful = review_data.get("votes[useful] ", None)
    votes_cool = review_data.get("votes[cool]", None)
    text = review_data.get("text", None)
   

{"votes": {"funny": 0, "useful": 0, "cool": 0}, "user_id": "p4ySEi8PEli0auZGBsy6gA", "review_id": "9uHZyOu5CTCDl1L6cfvOCA", "stars": 4, "date": "2009-05-03", "text": "Good truck stop dining at the right price. We love coming here on the weekends when we don't feel like cooking.", "type": "review", "business_id": "JwUE5GmEO-sH1FuwJgKBlQ"}

   

    #these are likely to be lists and a problem unless unpacked -- will need to put in another table
    # categories =  Column(String(64), nullable=True) 
    # neighborhoods = Column(String(128), nullable=True) 
    # timestamp = strftime

    new_review = model.Yelp_Review(stars = stars, business_id = business_id, 
    text = text, date = date, votes_funny = votes_funny, votes_useful = votes_useful,
    votes_cool = votes_cool, user_id = user_id)
  
    model.session.add(new_review)
    print "Here's what got added %r" % new_review.id

  model.session.commit()    
  json_data.close() 

def add_users(session):
  json_data=open("static/yelp_academic_dataset_user.json")

  for line in json_data:
    user_data = json.loads(line)
    user_id = user_data.get("user_id", None)
    name = user_data.get("name", None)
    review_count = user_data.get("review_count", 0)
    review_count = int(review_count)
    average_stars = user_data.get("average_stars", 0.0)
    average_stars = float(average_stars)
    votes = user_data.get("votes", 0)
    votes_funny = votes.get("funny", 0)
    votes_funny = int(votes_funny)
    votes_useful = votes.get("useful", 0)
    votes_useful = int(votes_useful)
    votes_cool = votes.get("cool", 0)
    votes_cool = int(votes_cool)
    # friends = user_data.get("friends", None)
    friends = "friends"
    elite = "elite"
    yelping_since = user_data.get("yelping_since", None)
    compliments = user_data.get("compliments", 0)
    compliment_type = user_data.get("compliment_type", 0)
    compliment_type = int(compliment_type)
    compliments = 0
    compliment_type = 0
    fans = user_data.get("fans", 0)
    fans = int(fans)

     

    new_user= model.Yelp_User(user_id = user_id, name = name, 
      review_count = review_count, average_stars = average_stars, 
      votes_funny = votes_funny, votes_useful = votes_useful, 
      votes_cool = votes_cool, 
      friends = friends, elite = elite, 
      yelping_since = yelping_since, compliments = compliments, 
      compliment_type = compliment_type, fans = fans)
  
    model.session.add(new_user)
    print "Here's what got added %r" % new_user.user_id

  model.session.commit()    
  json_data.close() 



def main(session):
  # add_restaurants(session)
  # add_reviews(session)
  add_users(session)

if __name__ == "__main__":
    s = model.connect()
    main(s) 

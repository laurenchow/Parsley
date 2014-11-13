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
    stars = restaurant_data.get("longitude", None)
    review_count = restaurant_data.get("review_count", None)
    is_still_open = restaurant_data.get("is_still_open", None)
    #these are likely to be lists and a problem unless unpacked -- will need to put in another table
    # categories =  Column(String(64), nullable=True) 
    # neighborhoods = Column(String(128), nullable=True) 
    # timestamp = strftime

    new_business = model.Yelp_Business(name = name, business_id = business_id, 
    full_address = full_address, city = city, latitude = latitude, 
    longitude = longitude, stars = stars, review_count = review_count, 
    is_still_open = is_still_open)
  
    model.session.add(new_business)
    print "Here's what got added %r" % new_business

  model.session.commit()    
  json_data.close() 

      # business_neighborhood = python_data['neighborhoods'] add this later, not in example data
      # print "Here's what is in hoods %r" % python_data['neighborhoods']
      # if business_neighborhood != []:
      #   print "This works so far %r" % business_neighborhood[1]
      # else: 
      #   print "This is empty, see? %r" % business_neighborhood
    

def add_reviews(session):
  json_data=open("static/yelp_academic_dataset_review.json")

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
    
    #these are likely to be lists and a problem unless unpacked -- will need to put in another table
    # categories =  Column(String(64), nullable=True) 
    # neighborhoods = Column(String(128), nullable=True) 
    # timestamp = strftime

    new_review = model.Yelp_Review(stars = stars, business_id = business_id, 
    text = text, date = date, votes_funny = votes_funny, votes_useful = votes_useful,
    votes_cool = votes_cool, user_id = user_id)
  
    model.session.add(new_review)
    print "Here's what got added %r" % new_review

  model.session.commit()    
  json_data.close() 

def add_users(session):
  json_data=open("static/yelp_academic_dataset_users_small.json")

  for line in json_data:
    user_data = json.loads(line)
    user_id = user_data.get("user_id", None)
    name = user_data.get("name", None)
    review_count = user_data.get("review_count", None)
    average_stars = user_data.get("average_stars", None)
    votes_funny = user_data.get("votes_funny", None)
    votes_useful = user_data.get("votes_useful", None)
    votes_cool = user_data.get("votes_cool", None)
    friends = user_data.get("friends", None)
    elite = user_data.get("elite", None)
    yelping_since = user_data.get("yelping_since", None)
    compliments = user_data.get("compliments", None)
    compliment_type = user_data.get("compliment_type", None)
    fans = user_data.get("fans", None)

    new_user= model.Yelp_User(user_id = user_id, name = name, 
      review_count = review_count, average_stars = average_stars, 
      votes_funny = votes_funny, votes_useful = votes_useful, 
      votes_cool = votes_cool, friends = friends, elite = elite, 
      yelping_since = yelping_since, compliments = compliments, 
      compliment_type = compliment_type, fans = fans)
  
    model.session.add(new_user)
    print "Here's what got added %r" % new_user.user_id

  model.session.commit()    
  json_data.close() 



def main(session):
  # add_restaurants(session)
  add_reviews(session)
  # add_users(session)

if __name__ == "__main__":
    s = model.connect()
    main(s) 

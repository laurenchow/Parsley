import json
import model



#work on this when you are ready for machine learning so you have a database with 
#enough data to make some interesting stuff

def add_restaurants(session):
  json_data=open("static/yelp_academic_dataset_business_small.json")

  with json_data as myfile:
    for line in json_data:
      db_friendly_data = json.loads(line)
      business_id = db_friendly_data['business_id']
      business_name = db_friendly_data['name']
      business_address = db_friendly_data['full_address']
      business_city = db_friendly_data['city']
      business_state = db_friendly_data['state']
      business_lat = db_friendly_data['latitude']
      business_long = db_friendly_data['longitude']
      # business_neighborhood = python_data['neighborhoods'] add this later, not in example data
      # print "Here's what is in hoods %r" % python_data['neighborhoods']
      # if business_neighborhood != []:
      #   print "This works so far %r" % business_neighborhood[1]
      # else: 
      #   print "This is empty, see? %r" % business_neighborhood

      new_restaurant = model.Restaurant(business_id = business_id, 
        name = business_name, address = business_address, 
        city = business_city, state = business_state, 
        latitude = business_lat, longitude = business_long)
      
      session.add(new_restaurant)
    
    print new_restaurant

    json_data.close()

# def load_reviews(session):
#       review_data=open("yelp_review_small.json")
   
#       # with review_data as myotherfile:
#       for line in review_data:
#         review_data = json.loads(line)
#         review_stars = review_data['stars']
#         review_biz_id = review_data['business_id']
#         review_text = review_data['text']

#         new_review = model.Review(business_id = review_biz_id, 
#           stars = review_stars, text = review_text)

#         session.add(new_review)
#         print new_review

      # review_data.close()
            # delete by hand or add in 
            # check and see if there's an ID in the database for the data:
            # if so, don't do anything, if not, add a row 
            # if id == "is null":
            
            
        
            # print ' '.join(row)
def main(session):
  add_restaurants(session)

if __name__ == "__main__":
    s = model.connect()
    main(s) 

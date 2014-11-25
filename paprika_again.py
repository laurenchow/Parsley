from flask import Flask, render_template, session, flash, redirect, request, g
from passlib.hash import pbkdf2_sha256
from factual import Factual
import model
import os
import jinja2
import numpy as np
import math 
# from flask.ext.login import LoginManager
# from flask.ext.openid import OpenID
# from config import basedir


KEY = os.environ.get('FACTUAL_KEY')
SECRET= os.environ.get('FACTUAL_SECRET')

app = Flask(__name__) 

#TODO: TURN INTO ENVIRONMENT VARIABLE
app.secret_key = ')V\xaf\xdb\x9e\xf7k\xccm\x1f\xec\x13\x7fc\xc5\xfe\xb0\x1dc\xf9\xcfz\x92\xe8'
app.jinja_env.undefined = jinja2.StrictUndefined


# use g in a before_request function to check and see if a user is logged in -- if they are logged in you can save it in g    
@app.before_request
def load_user_id():
    g.user_id = session.get('user_id')
    # just use flask logins

@app.route('/', methods = ['GET'])
def index():
    return render_template("index.html")
    
@app.route('/restaurants', methods = ['GET'])
def restos():
    return render_template("restaurants.html")

@app.route('/restaurants', methods = ['POST'])
def other_restos():
    restaurant1 = request.form.get('restaurant_1')
    restaurant2 = request.form.get('restaurant_2')
    restaurant3 = request.form.get('restaurant_3')      
    user_geo = request.form.get('user_geo') 

    restaurant1_data = parse_restaurant_input(restaurant1)
    restaurant2_data = parse_restaurant_input(restaurant2)
    restaurant3_data = parse_restaurant_input(restaurant3)

    print "This could be useful %r %r %r" % (restaurant1_data, restaurant2_data, restaurant3_data) 

    #TODO: Make it so that if it isn't in factual, a box prompts up asking you for another one

    restaurant_data = ping_factual([restaurant1, restaurant2, restaurant3], user_geo)
    restaurant_ids = check_db_for_restos(restaurant_data)
    add_restaurants_to_user_preferences(restaurant_ids)

    session['user_restaurant_ids'] = restaurant_ids
    session['user_geo'] = user_geo
    return suggest_new_resto(restaurant_data)
    # return redirect("/new_restaurant", restaurant_data = restaurant_data)
        
# use jquery AJAX here to add on same page
# show some things only when logged in

def parse_restaurant_input(restaurant_text):

    # restaurant1 = request.form['restaurant_1']
    data = {}

    #TODO: make sure everything is entered in here and that it adheres to GMaps
    #TODO: figure out how to link away for something when giving feedback

    restaurant_split = restaurant_text.split(',')
    
    if restaurant_split[0]:
        data['name'] = restaurant_split[0]
    if restaurant_split[2]:
        data['city'] =restaurant_split[2]
    if restaurant_split[3]:
        data['state'] = restaurant_split[3]
    if restaurant_split[2] and restaurant_split[3]:    
        data['geo'] = data['city']+data['state']

    return data


def ping_factual(restaurants, user_geo):

    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')

    restaurant_data = [] 

    #TODO: validate user enters three restaurants
    for restaurant in restaurants:
        #TODO: when you ping factual check DB there
        q = table.search(restaurant).limit(1)
        print "Here's what's stored in Factual for %r" %restaurant
        print q.data()
        print q.get_url()

        restaurant_data.append(q)

   
    return restaurant_data
    

#passing it a list of retaurants dictionaries from factual
#TODO: make it plural 
def check_db_for_restos(restaurant_data):
    """ Checks database for restaurants
    """
    restaurant_ids = []

    if type(restaurant_data) == list:
        for entry in range(len(restaurant_data)):
            print "Here's the number getting printed %r" % entry
            print "Here's what came in from Factual %r" % restaurant_data[entry]
       
            #searching the database seems to need to be case-sensitive for now, make it case insensitive
            restaurant_deets = restaurant_data[entry].data()
            print "Here are some deets %r" % restaurant_deets
            
            #TODO: Make sure three entries are valid
            if restaurant_deets:
                for item in restaurant_deets:
                    db_result = model.session.query(model.Restaurant).filter_by(factual_id = item['factual_id']).first() 

                    if db_result:
                        print "Here's what is stored in DB right now for name ID and address %r %r %r" % (db_result.name, db_result.id, db_result.address)
                        db_result.set_from_factual(item)
                        restaurant_ids.append(db_result.id)

                        model.session.add(db_result)

                        
                        db_result_features = model.session.query(model.Restaurant_Features).filter_by(factual_id = item['factual_id']).first()     
                        db_result_features.set_from_factual(item)
                        
                        model.session.add(db_result_features)

                        db_result_categories = model.session.query(model.Restaurant_Category).filter_by(factual_id = item['factual_id']).first()  
                        db_result_categories.restaurant_id = db_result_categories.id                  
                        db_result_categories.set_from_factual(item)

                        model.session.add(db_result_categories)
                        #TODO: figure out if this is fragile because it breaks if it doesn't happen the first time (like if you delete your table)
                        model.session.commit()

                    else:
                        print "***NOT IN DATABASE YET***"
                        new_restaurant = model.Restaurant()
                        new_restaurant.set_from_factual(item)
                        #use get to check for keys, otherwise make it none
                       
                        model.session.add(new_restaurant)

                        new_restaurant_features = model.Restaurant_Features()
                        new_restaurant_features.restaurant = new_restaurant
                        new_restaurant_features.set_from_factual(item)

                        model.session.add(new_restaurant_features)

                        new_restaurant_categories = model.Restaurant_Category()  
                        new_restaurant_categories.restaurant_id = new_restaurant.id                  
                        new_restaurant_categories.set_from_factual(item)
                        model.session.add(new_restaurant_categories)
                        model.session.commit()

                        restaurant_ids.append(new_restaurant.id)
    #TODO: figure out how to handle this when not a list
    else: 
        restaurant_deets = restaurant_data.data()
        print "Here are some deets %r" % restaurant_deets
        
        #TODO: Make sure three entries are valid
        if restaurant_deets:
        #check to see if restaurant details are in the DB for this restaurant
        #if not add it, if it is check to see that it's still the same
            for item in restaurant_deets:
                db_result = model.session.query(model.Restaurant).filter_by(factual_id = item['factual_id']).first() 

                if db_result:
                    print "Here's what is stored in DB right now for name ID and address %r %r %r" % (db_result.name, db_result.id, db_result.address)
                    db_result.set_from_factual(item)
                    restaurant_ids.append(db_result.id)
                    model.session.add(db_result)

        
                    db_result_features = model.session.query(model.Restaurant_Features).filter_by(factual_id = item['factual_id']).first() 
                    db_result_features.set_from_factual(item)
                    model.session.add(db_result_features)
                    
                    #adds categories if resto exists in DB
                    db_result_categories = model.session.query(model.Restaurant_Category).filter_by(factual_id = item['factual_id']).first()
                    db_result_categories.set_from_factual(item)
                    model.session.add(db_result_categories)
                    model.session.commit()



                else:
                    print "***NOT IN DATABASE YET***"
                    new_restaurant = model.Restaurant()
                    new_restaurant.set_from_factual(item)
                    #use get to check for keys, otherwise make it none
                   
                    model.session.add(new_restaurant)

                    new_restaurant_features = model.Restaurant_Features()
                    new_restaurant_features.restaurant = new_restaurant
                    new_restaurant_features.set_from_factual(item)

                    model.session.add(new_restaurant_features)
                    

                    new_restaurant_categories = model.Restaurant_Category()  
                    # new_restaurant_categories.restaurant_id = new_restaurant.id
                    new_restaurant_categories.restaurant = new_restaurant                  
                    new_restaurant_categories.set_from_factual(item)
                    model.session.add(new_restaurant_categories)
                    model.session.commit()

                    restaurant_ids.append(new_restaurant.id)

                
    return restaurant_ids

@app.route('/user_restaurant_preferences', methods = ['GET', 'POST'])
def add_restaurants_to_user_preferences(restaurant_ids):
    user_restaurant_preference = model.User_Restaurant_Rating(user_id = session['user_id'])
   
    #TODO: Fix this so it doesn't add multiple entries of same restaurant
    #this only works when a user initially types in restaurants, you need to figure out a way to handle upvote/downvote
    for entry in range(len(restaurant_ids)):
  
        db_result = model.session.query(model.User_Restaurant_Rating).filter_by(restaurant_id = restaurant_ids[entry], user_id = session['user_id']).first()
           
        if not db_result:
            user_restaurant_preference.restaurant_id = restaurant_ids[entry]
            user_restaurant_preference.rating = "1.0"
            model.session.merge(user_restaurant_preference)

    model.session.commit()

   

@app.route('/suggest_restaurant', methods = ['GET', 'POST'])
def suggest_new_resto(restaurant_data):
    """ This processes the user's input regarding favorite restaurants as well 
        as what their preferences are, then queries to determine suitable matches.
    """ 
    if session.get('user_restaurant_ids'):
        rest_ids = session.get('user_restaurant_ids')

    user_input_rest_data = get_user_inputs(rest_ids)
    print user_input_rest_data
    parsed_restaurants = get_factual_results()
    return "hello"
    
    # restaurants_to_suggest = process_factual_results(new_restaurants)
    # suggest_new_restaurant()
    # return restaurants_to_suggest


    #TODO: do not suggest restaurants that have already been typed in, check for that
    #TODO: make it so this page only shows if you're logged in 
   
def get_user_inputs(rest_ids):

    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
    user_geo = session['user_geo']

    user_input_rest_data = []
  
    for rest_id in rest_ids:
        resto_data = model.session.query(model.Restaurant).get(rest_id)
        user_input_rest_data.append(resto_data)


    # #TODO: have something in Javascript so you have to type in restaurants or else

    # current_user_id = session['user_id']  
    # user_preferences = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()

    return user_input_rest_data

def get_restaurant_model_similarities():
def get_rest_cat_similarities():
    
    # import pdb; pdb.set_trace()
    #TODO: CLEAR RESTAURANT ID SESSION
    #TODO: figure out if you can make evaluating similarities a function once it works
    restaurant_similarity = {'rating': [], 'price': []}
    restaurant_categories_similarity = {'cuisine': [], 'category_labels': []}
    #TODO: make this work


    for entry in range(len(restaurant_data)):
       
        restaurant_model = restaurant_data[entry]
        restaurant_categories = restaurant_model.restaurant_categories

        for feature in restaurant_similarity.keys():
          
            #does this work if you change to set?
            restaurant_model_value = getattr(restaurant_model, feature)

            if restaurant_model_value:
                restaurant_similarity[feature].append(restaurant_model_value)
         
        for feature in restaurant_categories_similarity.keys():  
            restaurant_categories_value = getattr(restaurant_categories, feature, None)
            if restaurant_categories_value is not None:
                restaurant_categories_similarity[feature].append(restaurant_categories_value)

                #A count of how often each variable happened in each restaurant {'rating': [4.5, 3.5, 3.5], 'price': [2, 1, 2]}
                #this doesn't work because it just adds to key and doesn't do a counter
                #for rating, you need to average it
                #for price, you need to average it
      

# def get_factual_results():
#     pass
# def process_factual_results(new_restaurants):
#     pass
# def suggest_new_restaurant():
#     pass

    sorted_restaurant_similarity = sorted(restaurant_similarity.items(), key = lambda (k,v): v)
    sorted_restaurant_similarity.reverse()
    sorted_restaurant_similarity_keys = [x[0] for x in sorted_restaurant_similarity]

    # print "!@*(!@#!*@#)!@#----- %r" % sorted_restaurant_similarity_keys
    #these are all the boolean restaurant features, process differently than 
    #cuisine and categories
    restaurant_features_similarity = {'alcohol': 0,
        'groups_goodfor':  0, 'kids_goodfor': 0,
        'kids_menu': 0, 'meal_breakfast':  0,
        'meal_dinner':  0, 'meal_deliver':  0,
        'options_healthy': 0, 
        'options_glutenfree': 0, 
        'options_lowfat':0, 
        'options_vegan': 0, 
        'options_vegetarian': 0, 
        'options_organic': 0, 'parking': 0, 
        'reservations':  0,
        'wifi' : 0}
    

    for entry in range(len(restaurant_data)):
        restaurant_model = restaurant_data[entry]
        restaurant_features = restaurant_model.restaurant_features

        for feature in restaurant_features_similarity.keys():
            restaurant_feature_value = getattr(restaurant_features, feature)
            if restaurant_feature_value:
                restaurant_features_similarity[feature] += 1


    sorted_restaurant_features_similarity = sorted(restaurant_features_similarity.items(), key = lambda (k,v): v)
    sorted_restaurant_features_similarity.reverse()
    sorted_restaurant_features_similarity_keys = [x[0] for x in sorted_restaurant_features_similarity]

    #TODO: figure out why this error is happening when you type in certain restaurants
    # AttributeError: 'NoneType' object has no attribute 'cuisine'

    #take the categories list and cuisine list, split them by each type of cuisine
    restaurant_cuisines_split_but_not_unpacked={}
    restaurant_categories_split_but_not_unpacked={}
    distinct_restaurant_cuisines={} 
    distinct_restaurant_categories={} 

    for key, value in restaurant_categories_similarity.iteritems():
        for entry in value:
            if key == 'cuisine':
                distinct_cuisines_list = entry.split(',')
                restaurant_cuisines_split_but_not_unpacked[entry]=distinct_cuisines_list

            if key == 'category_labels': 
                distinct_categories_list = entry.split(',')
                restaurant_categories_split_but_not_unpacked[entry]=distinct_categories_list
                

    for key, value in restaurant_cuisines_split_but_not_unpacked.iteritems():
        for entry in value:
            if entry != '':
                cuisine_count= distinct_restaurant_cuisines.get(entry, 0)+1
                distinct_restaurant_cuisines[entry]=cuisine_count
       

    
    sorted_distinct_restaurant_cuisines=sorted(distinct_restaurant_cuisines.items(), key = lambda (k,v): v)
    sorted_distinct_restaurant_cuisines.reverse()
    sorted_distinct_restaurant_cuisines_keys = [x[0] for x in sorted_distinct_restaurant_cuisines]


    for key, value in restaurant_categories_split_but_not_unpacked.iteritems():
        for entry in value:
            if entry != '':
                category_count= distinct_restaurant_categories.get(entry, 0)+1
                distinct_restaurant_categories[entry]=category_count
  
    
    sorted_distinct_restaurant_categories=sorted(distinct_restaurant_categories.items(), key = lambda (k,v): v)
    sorted_distinct_restaurant_categories.reverse()
    sorted_distinct_restaurant_categories_keys = [x[0] for x in sorted_distinct_restaurant_categories]


    
    #turn it into dictionaries where each item in list is counted and stored as value
    #search for the most-common cuisines and most-common categories from Factual
    #dot product that with the restaurants you return    
    #TODO: could you make it so it queries for all things that are 3 out of 3?
    new_restaurant_suggestion_from_features = table.filters({sorted_restaurant_features_similarity_keys[0]: "1" ,
     sorted_restaurant_features_similarity_keys[1]: "1", sorted_restaurant_features_similarity_keys[2]:"1", 
     "postcode": user_geo}).limit(5)


    # this sometimes throws a weird error due to throttle limits? so make something that makes this ok otherwise
    new_restaurant_suggestion_from_cuisines = table.filters({'cuisine': {"$in": [sorted_distinct_restaurant_cuisines_keys[0],
    sorted_distinct_restaurant_cuisines_keys[1], sorted_distinct_restaurant_cuisines_keys[2]]}, "postcode": user_geo}).limit(5)

    # #TODO: what if this returns nothing? how to subtract a key?
    new_restaurant_suggestion_from_categories = table.filters({'category_labels': {"$includes_any": [sorted_distinct_restaurant_categories_keys[0],
        sorted_distinct_restaurant_categories_keys[1], sorted_distinct_restaurant_categories_keys[2]]}, "postcode": user_geo}).limit(5)

    # print "Here are the new restaurants from features %r" % new_restaurant_suggestion_from_features
    # print "Here are the new restaurants from cuisines %r" % new_restaurant_suggestion_from_cuisines
   
    #TODO: is this the most sensible way to handle errors?    
    if new_restaurant_suggestion_from_features == []:
        return render_template("sorry.html")
    #TODO: if it returns nothing, reload the page to ask for new restaurants? 
    #TODO: return to new page so users know they moved URLs when they get new restaurants
    # list_new_restaurant_suggestion = new_restaurant_suggestion_from_features
    db_result_new_restaurants_from_features = check_db_for_restos(new_restaurant_suggestion_from_features)
    db_result_new_restaurants_from_cuisines = check_db_for_restos(new_restaurant_suggestion_from_cuisines)
    db_result_new_restaurants_from_categories = check_db_for_restos(new_restaurant_suggestion_from_categories)
    db_results_for_cuisines_and_features_combined = set(db_result_new_restaurants_from_features).union(set(db_result_new_restaurants_from_cuisines))
    all_db_results_for_new_restaurants = set(db_results_for_cuisines_and_features_combined).union(set(db_result_new_restaurants_from_categories))
    

    #turn the Factual objects into lists, then go over each list
    

    #TODO: create user_ideal_restaurant from three restaurant inputs along with user input
    user_ideal_restaurant = model.session.query(model.Restaurant).get(1)
    user_ideal_restaurant_features = user_ideal_restaurant.restaurant_features.get_all_data()
    user_ideal_restaurant_cuisines = user_ideal_restaurant.restaurant_categories.cuisine.split(',')
    user_ideal_restaurant_cat_labels = user_ideal_restaurant.restaurant_categories.category_labels.split(',')


    user_ideal_distinct_restaurant_cuisines ={}
    user_ideal_distinct_restaurant_cat_labels ={}

    for entry in user_ideal_restaurant_cuisines:
        if entry != '':
            user_cuisine_count = user_ideal_distinct_restaurant_cuisines.get(entry, 0)+1
            user_ideal_distinct_restaurant_cuisines[entry]=user_cuisine_count

    for entry in user_ideal_restaurant_cat_labels: 
        if entry !='':
            user_cat_label_count = user_ideal_distinct_restaurant_cat_labels.get(entry,0)+1
            user_ideal_distinct_restaurant_cat_labels[entry]=user_cat_label_count

    cosine_similarity_results = {}
    cuisine_cosine_similarity_results = {}
    category_cosine_similarity_results = {}

    all_distinct_restaurant_cuisines = {}
    all_distinct_restaurant_category_labels = {}

    for restaurant in all_db_results_for_new_restaurants:
        db_entry_for_restaurant= model.session.query(model.Restaurant).get(restaurant)
        db_entry_data_for_restaurant_features = db_entry_for_restaurant.restaurant_features.get_all_data()
        db_entry_data_for_restaurants_cuisine_list = db_entry_for_restaurant.restaurant_categories.cuisine
        db_entry_data_for_restaurant_category_list = db_entry_for_restaurant.restaurant_categories.category_labels
        

        #this only covers features
        total_cos_sim_value = 0 
        for item in db_entry_data_for_restaurant_features:
            cos_sim_result = cosine_similarity(db_entry_data_for_restaurant_features[item], user_ideal_restaurant_features[item])
            if cos_sim_result > 0:
                total_cos_sim_value = total_cos_sim_value + cos_sim_result
            cosine_similarity_results[db_entry_for_restaurant.name] = total_cos_sim_value

        #need to cover cuisine as well 

        #cosine similarity between restaurants returned and user ideal restaurants
        #add this cosine similarity with the features one to determine best restaurants
        #this may not work because these contain different items)
        #use all_distinct_restaurant_cuisines here because it's also a dict

        for entry in range(len(db_entry_data_for_restaurant_category_list)):
            db_entry_data_for_restaurants_cuisine_list.strip(" ")
            split_cat_list = db_entry_data_for_restaurant_category_list.split(',')
            for entry in split_cat_list:
                if entry != '':
                    cat_count = distinct_restaurant_cuisines.get(entry, 0)+1
                    all_distinct_restaurant_category_labels[entry]=cat_count



        for entry in range(len(db_entry_data_for_restaurants_cuisine_list)):
            db_entry_data_for_restaurants_cuisine_list.strip(" ")
            split_cuis_list = db_entry_data_for_restaurants_cuisine_list.split(',')
            for entry in split_cuis_list:
                if entry != '':
                    cuisine_count = distinct_restaurant_cuisines.get(entry, 0)+1
                    all_distinct_restaurant_cuisines[entry]=cuisine_count
        
        cuisine_total_cos_sim_value =0
        for key, value in all_distinct_restaurant_cuisines.iteritems():
                cuisine_cos_sim_result = cosine_similarity(all_distinct_restaurant_cuisines.get(key, 0), user_ideal_distinct_restaurant_cuisines.get(key,0))
                print key, cuisine_cos_sim_result
                if cuisine_cos_sim_result > 0:
                    cuisine_total_cos_sim_value = cuisine_total_cos_sim_value + cuisine_cos_sim_result
                cuisine_cosine_similarity_results[db_entry_for_restaurant.name] = cuisine_total_cos_sim_value

        #need to cover categories to know which one to search for

        #TODO: check and see if this should be 0
        category_label_total_cos_sim_value=0
        for key, value in all_distinct_restaurant_category_labels.iteritems():
                cat_cos_sim_result = cosine_similarity(all_distinct_restaurant_category_labels.get(key, 0),user_ideal_distinct_restaurant_cat_labels.get(key,0))
                if cat_cos_sim_result > 0:
                    category_label_total_cos_sim_value= category_label_total_cos_sim_value+cat_cos_sim_result
                category_cosine_similarity_results[db_entry_for_restaurant.name] = category_label_total_cos_sim_value

  

    sorted_all_distinct_restaurant_cuisines =  sorted(all_distinct_restaurant_cuisines.items(), key = lambda (k,v): v)
    sorted_all_distinct_restaurant_cuisines.reverse()
    sorted_all_distinct_restaurant_cuisines_keys = [x[0] for x in sorted_all_distinct_restaurant_cuisines]

    sorted_cuisine_cosine_similarity_results = sorted(cuisine_cosine_similarity_results.items(), key = lambda (k,v): v)
    sorted_cuisine_cosine_similarity_results.reverse()
    sorted_cuisine_cosine_similarity_results_keys =  [x[0] for x in sorted_all_distinct_restaurant_cuisines]


    #TODO: add results from category, features and cuisine cosine similarities
    #TODO: then suggest those restaurants
    """
        {u'Boogaloos': 1.0, u'Beretta': 1.0, u'Taqueria Cancun': 1.0, u'La Taqueria': 1.0, u'El Farolito': 1.0, u'Foreign Cinema': 1.0, u'Luna Park': 0, u'Flour + Water': 2.0, u'Limon': 1.0, u'Humphry Slocombe': 2.0, u'Slow Club': 0, u'Philz Coffee': 2.0, u'Bi-Rite Creamery': 2.0, u'Tartine Bakery': 1.0}
    (Pdb) category_cosine_similarity_results
    {u'Boogaloos': 5.0, u'Beretta': 5.0, u'Taqueria Cancun': 5.0, u'La Taqueria': 5.0, u'El Farolito': 5.0, u'Foreign Cinema': 5.0, u'Luna Park': 3.0, u'Flour + Water': 5.0, u'Limon': 5.0, u'Humphry Slocombe': 5.0, u'Slow Club': 4.0, u'Philz Coffee': 5.0, u'Bi-Rite Creamery': 5.0, u'Tartine Bakery': 5.0}
    (Pdb) cosine_similarity_results
    {u'Boogaloos': 7.0, u'Beretta': 8.0, u'Taqueria Cancun': 7.0, u'La Taqueria': 7.0, u'El Farolito': 6.0, u'Foreign Cinema': 7.0, u'Luna Park': 8.0, u'Flour + Water': 0, u'Limon': 8.0, u'Humphry Slocombe': 3.0, u'Slow Club': 7.0, u'Philz Coffee': 1.0, u'Bi-Rite Creamery': 8.0, u'Tartine Bakery': 7.0}
    (Pdb)  * Detected change in 'paprika_again.py', reloading
    """

    #this gives you what the user input prioritizes in terms of cuisine
    #compares restaurants from factual results with this

    #this is cosine similarity for features, doesn't include cuisines
    sorted_cosine_similarity_results = sorted(cosine_similarity_results.items(), key = lambda (k,v): v)
    sorted_cosine_similarity_results.reverse()
    sorted_cosine_similarity_results_keys = [x[0] for x in sorted_cosine_similarity_results]

    new_restaurant_suggestion_from_all = table.filters({'name': {"$in": [sorted_cosine_similarity_results_keys[0],
    sorted_cosine_similarity_results_keys[1], sorted_cosine_similarity_results_keys[2], sorted_cosine_similarity_results_keys[3], 
    sorted_cosine_similarity_results_keys[4], sorted_cosine_similarity_results_keys[5]]}, "postcode": user_geo}).limit(5)
    
    print new_restaurant_suggestion_from_all

    # compare each restaurant in list to ideal restaurant for a user

    return render_template("new_restaurant.html", new_restaurant_suggestion = new_restaurant_suggestion_from_cuisines, 
        sorted_restaurant_features_similarity_keys = sorted_restaurant_features_similarity_keys)



def cosine_similarity(v1, v2):
    """ This takes list of restaurants features returned from Factual and compares them to user's 
    ideal restaurant to see how similar they are.
    """

    cosine_similarity_result = np.dot(v1, v2) / (np.sqrt(np.dot(v1, v1)) * np.sqrt(np.dot(v2, v2)))
    
    # print "Here's what is printing for cosine_sim_result %r" % cosine_similarity_result
    return cosine_similarity_result
   
    

@app.route('/favorites', methods = ['GET'])
def user_favorites():
    current_user_id = session['user_id']
    single_user = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id).all()
    # default_user = model.session.query(model.User_Restaurant_Rating)
    # ValueError: View function did not return a response happened when no favorites
    # TODO: figure out why user is undefined

    if single_user:
        return render_template("favorites.html", user = single_user)
    else:
         return render_template("favorites.html")
    #TODO: FIX THIS SO IT STORES USER ALWAYS
@app.route('/user', methods = ['GET'])
def user_profile():
    current_user_id = session['user_id']
    single_user = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id).all()
    default_user =model.session.query(model.User_Restaurant_Rating).filter_by(user_id = 1).all()
    if single_user:
        return render_template("favorites.html", user = single_user)
    else:
        return render_template("user.html", user = default_user)
    #TODO make map, make it so you can save map

@app.route('/contact', methods = ['GET'])
def contact_us():
    return render_template("contact.html")

@app.route('/about', methods = ['GET'])
def about_us():
    return render_template("about.html")

#TODO: make this evaluate whether it's retuning nthing because restaurant list is bad
# or if you need to search different parameters
@app.route('/sorry', methods = ['GET'])
def more_restaurant_data_needed():
    return render_template("sorry.html")

@app.route('/signup', methods = ['GET', 'POST'])
def user_signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        return signup_user()
        #but you also want to reload the page with their data if they do


def signup_user():
    user_email = request.form['email']
    user_password = request.form['password']
    user_first_name = request.form['first_name']
    user_last_name = request.form['last_name']
    print "This is what user_password is stored as %r" % type(user_password)

    already_registered = model.session.query(model.User).filter_by(email = user_email).first()

    if already_registered:
        flash("Looks like you already have an account. Want to try signing in?")

    secure_password = pbkdf2_sha256.encrypt(user_password, rounds=200000, salt_size=16)
    print "this is the secure hashed password %r" % secure_password
    #put something in here about making good passwords with uppercase and flash suggestion
    new_user = model.User(email = user_email, password = secure_password, 
        first_name = user_first_name, last_name = user_last_name)

    model.session.add(new_user)
    model.session.commit() 
    
    current_user = model.session.query(model.User).filter_by(email = user_email).first()
    current_user_preferences = model.User_Preference(user_id=current_user.id)

    model.session.add(current_user_preferences)
    model.session.commit() 

    session['user_id'] = current_user.id
    session['user_email'] = current_user.email
        
    print "Here's what in the session at the end of signup %r" % session

    return redirect("/welcome")






@app.route('/welcome', methods = ['GET', 'POST'])
def new_user_welcome():
    print "Here's what in the session in welcome %r" % session
    current_user_id = session['user_id']  

    if request.method == "GET":
        return render_template("welcome.html")
    else:
        return submit_user_details(current_user_id)

# # fix this so you don't see it unless logged in

def submit_user_details(current_user_id):
      
    new_user_info = model.session.query(model.User).filter_by(id = current_user_id).first()

    kwargs = {'age': request.form['age'], 'gender': request.form['gender'],
    'zip': request.form['zip'], 'occupation': request.form['job'], 'id': current_user_id}

    new_user_info = model.User(**kwargs)

    model.session.merge(new_user_info)
    model.session.commit()

    return redirect("/user_preferences")
    



@app.route('/user_preferences', methods = ['GET'])
def user_preferences():
    return render_template("user_preferences.html")
    

@app.route('/user_preferences', methods = ['POST'])
def submit_user_preferences(): 
    current_user_id = session['user_id']  
    print "This is where you'll show what the user says they prefer"  
    print "This is who is logged in right now %r" % current_user_id
    update_existing_user_prefs = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()

    # print "This exists!!! %r" % new_user_prefs_info
    if update_existing_user_prefs:
    # if current_user_id:
        kwargs = {'accessible_wheelchair': request.form['accessible_wheelchair'],
        'kids_goodfor': request.form['kids_goodfor'],
        'options_healthy': request.form['options_healthy'], 
        'options_organic': request.form['options_organic'], 
        'parking': request.form['parking'], 
        'wifi' : request.form['wifi'], 'user_id': current_user_id}

        update_existing_user_prefs = model.User_Preference(**kwargs)
        model.session.merge(update_existing_user_prefs)
        model.session.commit()
    
        return redirect("/")
    # else:
    #     new_user_prefs = model.User_Preference()
    #     kwargs = {'accessible_wheelchair': request.form['accessible_wheelchair'],
    #     'kids_goodfor': request.form['kids_goodfor'],
    #     'options_healthy': request.form['options_healthy'], 
    #     'options_organic': request.form['options_organic'], 
    #     'parking': request.form['parking'], 
    #     'wifi' : request.form['wifi'], 'user_id': current_user_id}

    #     new_user_prefs = model.User_Preference(**kwargs)
    #     model.session.merge(new_user_prefs)
    #     model.session.commit()


    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def show_login():
    if request.method == "GET":
        return render_template("login.html")
    else: 
        return login_user()

def login_user():
    user_email = request.form['email']

    # does a user with this email exist?
    current_user = model.session.query(model.User).filter_by(email = user_email).first()

        # if so, get their password (which is stored in hash form)
    if current_user:
        input_password = request.form['password']
        print "This is what user_password is stored as %r" % type(input_password)
        
        if pbkdf2_sha256.verify(input_password, current_user.password):
            session['user_email'] = current_user.email    
            print session
            return redirect("/")    
            
        else:
            flash("Invalid username or password", "error")
            return redirect("/signup") 
    else:
        flash("Invalid username or password", "error")
        return redirect("/signup") 
    

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect("/")


@app.route('/logout')
def logout_user():
    session.clear()
    print "This is what session looks like now %r" % session
    return redirect("/login")
  



if __name__ == "__main__":
    app.debug = True
    app.run()

from flask import Flask, render_template, session, flash, redirect, request, g, jsonify
from passlib.hash import pbkdf2_sha256
from factual import Factual
import model
import os
import jinja2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


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
    """This is the main function for suggesting a new restaurant. It contains
    functions that 
    (1) take in user input for restaurants using Google Maps JS autocomplete
    (2) parse restaurant inputs to determine name, city
    (3) make API call to Factual to find information on those restaurants
    (4) determine the most common categories, features and cuisines of those restaurants
    (5) make API call to Factual to find similar restaurants using parameters defined in (4)
    (6) ranks results from (5) using cosine similarity, which measures how each restaurant
    in (5) compares to a user's established preferences
    (7) returns the highest-ranked restaurants to surface to user for user feedback

    """
    restaurant1 = request.form.get('restaurant_1')
    restaurant2 = request.form.get('restaurant_2')
    restaurant3 = request.form.get('restaurant_3')      
    user_geo = request.form.get('user_geo') 

    restaurant_data = ping_factual([restaurant1, restaurant2, restaurant3], user_geo)
    print "\n\n\n\n\n\n\n2"
    restaurant_ids = check_db_for_restos(restaurant_data)
    session['user_restaurant_ids'] = restaurant_ids
    session['user_geo'] = user_geo
    print "\n\n\n\n\n\n\n3"
    add_restaurants_to_user_preferences(restaurant_ids)
    print "\n\n\n\n\n\n\n4"
   
    return suggest_new_resto(restaurant_data)
        
# use jquery AJAX here to add on same page
# show some things only when logged in

def parse_restaurant_input(restaurant_text):
 
    data = {}

    #TODO: make sure everything is entered in here and that it adheres to GMaps
    #TODO: figure out how to link away for something when giving feedback

    restaurant_split = restaurant_text.split(',')
    #check to make sure that there are commas
    #check that the length is greater than r eq 4 if not use the full string
    if restaurant_split[0]:
        data['name'] = restaurant_split[0]
    if restaurant_split[-3]:
        data['city'] =restaurant_split[2]
    if restaurant_split[-2]:
        data['state'] = restaurant_split[3]
    if restaurant_split[-3] and restaurant_split[-2]:    
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
        # print "Here's what's stored in Factual for %r" %restaurant
        print q.data()
        print q.get_url()

        restaurant_data.append(q)

   
    return restaurant_data


def check_db_for_restos(restaurant_data):
    """ 
    Checks database for restaurants to see if they exist as entries yet. 
    If not, adds restaurants into database.
    """
    restaurant_ids = []

    if type(restaurant_data) == list:
        for entry in range(len(restaurant_data)): 
       
            #searching the database seems to need to be case-sensitive for now, make it case insensitive
            restaurant_deets = restaurant_data[entry].data() 
            #TODO: Make sure three entries are valid
            if restaurant_deets:
                for item in restaurant_deets:
                    db_result = model.session.query(model.Restaurant).filter_by(factual_id = item['factual_id']).first() 

                    if db_result:
                        restaurant_ids.append(db_result.id)
                
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

    #this handles in event restaurant is not passed in in list form
    if restaurant_deets:
        #check to see if restaurant details are in the DB for this restaurant
        #if not add it, if it is check to see that it's still the same
            for item in restaurant_deets:
                db_result = model.session.query(model.Restaurant).filter_by(factual_id = item['factual_id']).first() 

                if db_result:
                    restaurant_ids.append(db_result.id)

                else:
                    new_restaurant = model.Restaurant()
                    new_restaurant.set_from_factual(item)
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
    """
    This function is passed a restaurant id (or a list of restaurant ids).
    It checks to see if a user's restaurant preference already exists in a user's entry in the User_Restaurant_Rating table.
    If not, it adds to the DB.
    """
    user_restaurant_preference = model.User_Restaurant_Rating(user_id = session['user_id'])

    for entry in range(len(restaurant_ids)):
        db_result = model.session.query(model.User_Restaurant_Rating).filter_by(restaurant_id = restaurant_ids[entry], 
            user_id = session['user_id']).first()
           
        if not db_result:
            user_restaurant_preference.restaurant_id = restaurant_ids[entry]
            user_restaurant_preference.rating = "1.0"
            model.session.merge(user_restaurant_preference)

    model.session.commit()

@app.route('/user_feedback', methods = ['POST'])
def user_feedback_on_restaurants():
    """
    This function receives user feedback on suggested restaurants, then checks to see 
    if this already exists in the database. If it does not, it adds it to the DB.
    """
    #TODO: change to .get
    feedback_factual_id = request.form.get('factual_id')
    feedback_restaurant_rating = request.form.get('user_feedback')
    feedback_restaurant_rating = float(feedback_restaurant_rating)
    feedback_button_id = request.form.get('button_id')
    
    restaurant = model.session.query(model.Restaurant).filter_by(factual_id = feedback_factual_id).first()
    user_preference = model.session.query(model.User_Restaurant_Rating).filter_by(restaurant_id = restaurant.id, 
        user_id = session['user_id']).first()
    
    if user_preference:
        user_preference.rating = feedback_restaurant_rating
        model.session.add(user_preference)
    #if/else write a function to try/except and get an integrity error if it already exists
    else:
        user_preference = model.User_Restaurant_Rating()
        user_preference.restaurant_id = restaurant.id
        # factual_id = feedback_factual_id).first()
        user_preference.rating = feedback_restaurant_rating
        user_preference.user_id = session['user_id']
        model.session.add(user_preference)

    model.session.commit()
    return jsonify( { 'feedback_button_id': feedback_button_id} )



@app.route('/suggest_restaurant', methods = ['GET', 'POST'])
def suggest_new_resto(restaurant_data):
    """ This processes the user's input regarding favorite restaurants as well 
        as what their preferences are, then queries to determine suitable matches.

        It returns a list of restaurants from Factual along with a list of the 
        user's top-ranked features (if cuisine is selected, weights cuisine as well.)
    """ 

   

    if session.get('user_restaurant_ids'):
        rest_ids = session.get('user_restaurant_ids')

    print "\n\n\n\n\n\na"
    user_input_rest_data = get_user_inputs(rest_ids)
    print "\n\n\n\n\n\nb"
    sorted_restaurant_features_counter_keys = get_rest_features_similarities(user_input_rest_data)
    print "\n\n\n\n\n\nc"
    db_result_new_restaurants_from_features = get_rest_features_results(sorted_restaurant_features_counter_keys)
    print "\n\n\n\n\n\nd"
     # import pdb; pdb.set_trace()
    translated_sorted_rest_feat_sim_keys = convert_restaurant_features_to_normal_words(sorted_restaurant_features_counter_keys)
    new_restaurant_suggestion = get_suggestions(db_result_new_restaurants_from_features)

    return render_template("new_restaurant.html", new_restaurant_suggestion = new_restaurant_suggestion, 
        translated_sorted_rest_feat_sim_keys = translated_sorted_rest_feat_sim_keys )


def get_suggestions(db_result_new_restaurants_from_features):

    """
    This function:
    (1) Queries the database for a user's established preferences. 
    (2) Determines the cosine similarity between restaurants returned from Factual (adding together results from categories, 
    features and cuisines) and the 'ideal restaurant' for this user.
    (3) Returns best restaurants. 
    """
    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
    user_geo =  session['user_geo'] 

     #turn the Factual objects into lists, then go over each list
    
    #TODO: create user_ideal_restaurant from three restaurant inputs along with user input
   
    #this will give you a row for the user that contains all their weighted preferences

    #TODO: replace placeholder of ideal restaurant with user preferences
    user_ideal_restaurant = model.session.query(model.Restaurant).get(2)
    user_ideal_profile =  model.session.query(model.User_Preference).filter_by(user_id= session['user_id'])
    # import pdb; pdb.set_trace()
    user_ideal_restaurant_features = user_ideal_restaurant.restaurant_features.get_all_data() 
    cosine_similarity_results = {}

    for restaurant in db_result_new_restaurants_from_features:
        db_entry_for_restaurant= model.session.query(model.Restaurant).get(restaurant)
        db_entry_data_for_restaurant_features = db_entry_for_restaurant.restaurant_features.get_all_data() 
        
 
        total_cos_sim_value = 0 
        for item in db_entry_data_for_restaurant_features:
            cos_sim_result = cosine_similarity(db_entry_data_for_restaurant_features[item], user_ideal_restaurant_features[item])
            if cos_sim_result > 0:
                total_cos_sim_value = total_cos_sim_value + cos_sim_result
            cosine_similarity_results[db_entry_for_restaurant.name] = total_cos_sim_value 

        # #TODO: fix this
        #TODO: remove the last element in list for category_labels because it is breadcrumbs so only the last one
        # for entry in range(len(db_entry_data_for_restaurant_category_list)):


    #this gives you what the user input prioritizes in terms of cuisine
    #compares restaurants from factual results with this

    #this is cosine similarity for features, doesn't include cuisines
    sorted_cosine_similarity_results = sorted(cosine_similarity_results.items(), key = lambda (k,v): v)
    sorted_cosine_similarity_results.reverse()
    sorted_cosine_similarity_results_keys = [x[0] for x in sorted_cosine_similarity_results]

    #TODO: write a function to pass in here in case length is variable so it doesn't break
    new_restaurant_suggestion_from_all = table.filters({'name': {"$in": [sorted_cosine_similarity_results_keys[0],
    sorted_cosine_similarity_results_keys[1], sorted_cosine_similarity_results_keys[2], sorted_cosine_similarity_results_keys[3], 
    sorted_cosine_similarity_results_keys[4], ]}, "postcode": user_geo}).limit(5)
    
    return new_restaurant_suggestion_from_all

def get_user_inputs(rest_ids):
    """
    This function takes the restaurant ids from the three restaurants that the user inputs and creates a list 
    containing all DB data for restaurants.
    """
    # factual = Factual(KEY, SECRET)
    # table = factual.table('restaurants')
    # user_geo = session['user_geo']

    user_input_rest_data = []
  
    for rest_id in rest_ids:
        resto_data = model.session.query(model.Restaurant).get(rest_id)
        user_input_rest_data.append(resto_data)

    return user_input_rest_data

def get_rest_features_similarities(user_input_rest_data): 
    """
    This creates dictionary counting instances of each restaurant feature in the data
    that the user input, returns most relevant (highest frequency) restaurant features.
    """

    # factual = Factual(KEY, SECRET)
    # table = factual.table('restaurants')
    # user_geo =  session['user_geo']     

    restaurant_features_counter = {'alcohol': 0,
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
    

    for entry in range(len(user_input_rest_data)):
        restaurant_model = user_input_rest_data[entry]
        restaurant_features = restaurant_model.restaurant_features

        for feature in restaurant_features_counter.keys():
            restaurant_feature_value = getattr(restaurant_features, feature)
            if restaurant_feature_value:
                restaurant_features_counter[feature] += 1


    sorted_restaurant_features_counter = sorted(restaurant_features_counter.items(), key = lambda (k,v): v)
    sorted_restaurant_features_counter.reverse()
    sorted_restaurant_features_counter_keys = [x[0] for x in sorted_restaurant_features_counter]

    # import pdb; pdb.set_trace()

    return sorted_restaurant_features_counter_keys

def convert_restaurant_features_to_normal_words(translated_sorted_rest_feat_sim_keys):
    """
    This function takes the list of most common features from the DB and translates
    to English (e.g., alcohol_bar becomes bars, groups_goodfor becomes good for groups, etc.)
    so that sentence reads 'You like places that: ...'
    """ 

    translated_restaurant_features = { 'accessible_wheelchair': "are accessible",
    'alcohol_byob': "let you bring your own booze", 'alcohol_bar': "have a full bar", 
    'alcohol_beer_wine': "have beer and wine", 'alcohol': "serve alcohol",
    'groups_goodfor': "are good for groups", 'kids_goodfor': "are good for kids",
    'kids_menu': "have a kids menu", 'meal_breakfast': "serve breakfast",  
    'meal_cater': "have catering available", 'meal_deliver': "have delivery options",
    'meal_dinner': "serve dinner", 'meal_lunch': "serve lunch", 'meal_takeout': "have takeout options available",
    'open_24hrs': "are open 24 hours", 'options_glutenfree': "have gluten-free options",
    'options_lowfat': "have low-fat options", 'options_organic': "have organic options",
    'options_healthy': "have healthy options", 'options_vegan': "have vegan options",
    'options_vegetarian': "have vegetarian options", 'parking': "have parking",
    'parking_free': "have free parking", 'parking_garage': "have garages for parking",
    'parking_lot': "have parking lots", 'parking_street': "have street parking",
    'parking_valet': "have valet", 'parking_validated': "have validated parking",
    'payment_cashonly': "are cash only", 'reservations': "allow reservations", 
    'room_private': "have private rooms", 'seating_outdoor': "have outdoor seating",
    'smoking': "allow smoking", 'wifi': "have wifi"}

    for entry in range(len(translated_sorted_rest_feat_sim_keys)):
        phrase_to_change =  translated_sorted_rest_feat_sim_keys[entry]
        if phrase_to_change in translated_restaurant_features.keys():
             translated_sorted_rest_feat_sim_keys[entry] = translated_restaurant_features[phrase_to_change]

    return translated_sorted_rest_feat_sim_keys

def get_rest_features_results(sorted_restaurant_features_counter_keys):
    """
    This function takes the ranked restaurant features, searches 
    Factual for matching restaurants and returns restaurants from Factual that 
    match these features.
    """
    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
    user_geo =  session['user_geo']  

    #TODO: figure out why this error is happening when you type in certain restaurants
    # AttributeError: 'NoneType' object has no attribute 'cuisine'

    #TODO: could you make it so it queries for all things that are 3 out of 3?
    new_restaurant_suggestion_from_features = table.filters({sorted_restaurant_features_counter_keys[0]: "1" ,
     sorted_restaurant_features_counter_keys[1]: "1", sorted_restaurant_features_counter_keys[2]:"1", 
     "postcode": user_geo}).limit(5)


    #TODO: is this the most sensible way to handle errors?    
    if new_restaurant_suggestion_from_features == []:
        return render_template("sorry.html")
    print "\n\n\n\n\n\nXX1"   
    
    #TODO: fix looping here in check_db_for_restos.
    #you could loop over the entry instead and pass DB a list of factual IDs
    #to check all at once instead of checking each factual ID

    db_result_new_restaurants_from_features = check_db_for_restos(new_restaurant_suggestion_from_features)

    # import pdb; pdb.set_trace()

    print "\n\n\n\n\n\nXX2"


    return db_result_new_restaurants_from_features

def cosine_similarity(v1, v2):
    """ This takes list of restaurants features returned from Factual and compares them to user's 
    ideal restaurant to see how similar they are.
    It returns an integer value.
    """
    # rest_ids = session['user_restaurant_ids']
    # D = session.model.query
    # x = v.fit_transform(D) 

    # print x

    # x = v.fit_transform(D)
    # # y = v.fit_transform(a)
    # # y.todense()
    # x.todense()
    # cs = cosine_similarity(x[0:1], x)

    cosine_similarity_result = np.dot(v1, v2) / (np.sqrt(np.dot(v1, v1)) * np.sqrt(np.dot(v2, v2)))
    
    return cosine_similarity_result
   
# @app.route('/get_restos', methods = ['GET'])
# def new_restaurants():

#     factual = Factual(KEY, SECRET)
#     table = factual.table('restaurants')
#     user_geo =  session['user_geo']  
#     # import pdb; pdb.set_trace()
#     new_restaurants = table.filters({"postcode": 94102}).offset(75).limit(25)
#     check_db_for_restos(new_restaurants)

#     return "Success"


@app.route('/favorites', methods = ['GET'])
def user_favorites():
    """
    This function queries DB to determine what user favorites are.
    If user has filled out user preferences form or submitted any information on preferred restaurants,
    it will return all the restaurants a user has rated and display those on the page.
    If a user has not completed any, it will send the user to a page to submit more information.
    """
    current_user_id = session['user_id']
    single_user = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id).all()
    # default_user = model.session.query(model.User_Restaurant_Rating)
    # ValueError: View function did not return a response happened when no favorites
    # TODO: figure out why user is undefined

    if single_user:
        return render_template("favorites.html", user = single_user)
    else:
         return render_template("sorry.html")

@app.route('/user', methods = ['GET'])
def user_profile():
    """
    This function may not be necessary.
    """
    current_user_id = session['user_id']
    single_user = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id).all()
    default_user =model.session.query(model.User_Restaurant_Rating).filter_by(user_id = 1).all()
    if single_user:
        return render_template("favorites.html", user = single_user)
    else:
        return render_template("user.html", user = default_user)
    #TODO make map, make it so you can save map

@app.route('/browse', methods = ['GET'])
def browse_new_rests():
    """ 
    This function allows the user to browse new restaurants based on user preferences
    and requires no new input from the user.
    """

    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
    user_geo =  session['user_geo']  
    current_user_id = session['user_id']

    single_user = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id, rating = 1.0).all()
    
    single_user_features = {}
    for item in single_user:
        single_user_features = single_user.restaurant_features.get_all_data()

    # import pdb; pdb.set_trace()
    default_user =model.session.query(model.User_Restaurant_Rating).filter_by(user_id = 1).all()


    new_restaurant_suggestion_from_all = table.filters({'name': {"$in": [sorted_cosine_similarity_results_keys[0],
    sorted_cosine_similarity_results_keys[1], sorted_cosine_similarity_results_keys[2], sorted_cosine_similarity_results_keys[3], 
    sorted_cosine_similarity_results_keys[4], ]}, "postcode": user_geo}).limit(5)
    
    return render_template("new_restaurant.html", new_restaurant_suggestion = new_restaurant_suggestion, 
        translated_sorted_rest_feat_sim_keys = translated_sorted_rest_feat_sim_keys )


@app.route('/contact', methods = ['GET'])
def contact_us():
    """
    This function returns an HTML template containing contact information and how to contact developer.
    """

    return render_template("contact.html")

@app.route('/about', methods = ['GET'])
def about_us():
    """
    This function returns an HTML template containing license information and how to contact developer.
    """
    return render_template("about.html")

#TODO: make this evaluate whether it's retuning nthing because restaurant list is bad
# or if you need to search different parameters
@app.route('/sorry', methods = ['GET'])
def more_restaurant_data_needed():
    """
    This function returns an HTML template containing a request for the user to submit more information.
    It redirects them to either 
    (a) the /restaurants page to submit preferred restaurant information or
    (b) the /user_preferences page to submit user preferences 
    """
    return render_template("sorry.html")

@app.route('/signup', methods = ['GET', 'POST'])
def user_signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        return signup_user()
        #but you also want to reload the page with their data if they do


def signup_user():
    """
    This function requests information from the signup form, then returns the
    user to the welcome page via redirect after storing user_id and user_email in session.

    """
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
    """
    This function requests demographic information from the signup form, then returns the
    user to the user preferences form via a redirect. 
    """
    current_user_id = session['user_id']  

    new_user_info = model.session.query(model.User).filter_by(id = current_user_id).first()

    kwargs = {'age': request.form['age'], 'gender': request.form['gender'],
    'zip': request.form['zip'], 'occupation': request.form['job'], 'id': current_user_id}

    new_user_info = model.User(**kwargs)

    model.session.merge(new_user_info)
    model.session.commit()

    return redirect("/user_preferences")

    

#TODO: this has a weird bug smetimes, make sure it doesn't happen
@app.route('/user_preferences', methods = ['GET', 'POST'])
def user_preferences():
    """
    Determines if user has submitted preferences. If post method, 
    submits user pref data to the update_user_prefs function.
    """

    if request.method == "GET":
        return render_template("user_preferences.html")
    else:
        return update_user_prefs()

def update_user_prefs():
    """
    Looks up existing user preferences and loads the restaurants a user has reviewed.
    For each restaurant a user has reviewed, increments the feature in user preferences
    to show that the user strongly values that feature.
    """
    current_user_id = session['user_id']  
    print "This is who is logged in right now %r" % current_user_id
    existing_user_prefs = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()
    

    #you'll want to check if the restaurant has already been entered into the user
    if existing_user_prefs:
        user_fave_rests = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id).all()
        if user_fave_rests:
            user_prefs_to_store = {}
            user_prefs = existing_user_prefs.get_all_data()

            for key, value in user_prefs.iteritems():
                user_prefs_to_store[key] = getattr(existing_user_prefs, key,value)


            for entry in user_fave_rests:
                rest_features = entry.restaurant.restaurant_features.get_all_data()
                for key, value in rest_features.iteritems():
                    feature_count = rest_features.get(key, 0) +1
                    user_prefs_to_store[key] = feature_count
                    #should be 20 keys
                    # user_prefs_to_store[key] = getattr(rest_features,key,value)
                    #create a new key in dictionary to add this value in
                    #make this a counter where the key is the feature, the value is the number of times it's happened
                    #if key already exists, add feature value to it
                    #add all keys (which are db columns) in to session and commit
                    #should set all user preferences to zero then try as negative 1
                    
            kwargs = user_prefs_to_store

            
            new_user_prefs = model.User_Preference(user_id = current_user_id, **kwargs)
            model.session.add(new_user_prefs)
           
            # updated_user_prefs = model.session.query(model.User_Preference).filter_by(user_id = existing_user_prefs.id).first()
            # updated_user_prefs = model.session.User_Preference(user_id = existing_user_prefs.id,  **kwargs)

            # model.session.commit()
        

#             model.session.add(updated_user_prefs, user_id = current_user_id)

#             model.session.add(updated_user_prefs, user_id = current_user_id)
#             import pdb; pdb.set_trace()
#         
        else:
        
            kwargs = {'accessible_wheelchair': request.form.get('accessible_wheelchair'),
            'kids_goodfor': request.form.get('kids_goodfor'),
            'options_healthy': request.form.get('options_healthy'), 
            'options_organic': request.form.get('options_organic'), 
            'parking': request.form.get('parking'), 
            'wifi' : request.form.get('wifi'), 
            'user_id': current_user_id}

            initial_user_prefs = model.User_Preference(**kwargs)

            model.session.add(initial_user_prefs, user_id = current_user_id)
        
        model.session.commit()
                      
    else:
        pass
        # return redirect("/sorry")

    return render_template("user_preferences.html")
    

# @app.route('/user_preferences', methods = ['GET', 'POST'])
# # def submit_user_preferences(restaurant_data): 
# def submit_user_preferences(): 
#     """
#     This function stores user preferences for all restaurants rated.
    
#     If user preferences do not exist (e.g., at signup), creates instance of User_Preference 
#     class and stores preferences.
    
#     If user preferences do already exist, this function reviews all the restaurants 
#     a user has favorited and stores in a dictionary of values indicating how strongly a user prefers 
#     a certain restaurant feature, category or cuisine.
#     """

#     current_user_id = session['user_id']  
#     print "This is who is logged in right now %r" % current_user_id
#     existing_user_prefs = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()
 
#     if existing_user_prefs:
#         user_fave_rests = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id).first()
#         if user_fave_rests:
#             pass

#             model.session.add(updated_user_prefs, user_id = current_user_id)
#             import pdb; pdb.set_trace()
#         else:
#             pass
#             redirect("/sorry")
#     else:
    
#         kwargs = {'accessible_wheelchair': request.form.get('accessible_wheelchair'),
#         'kids_goodfor': request.form.get('kids_goodfor'),
#         'options_healthy': request.form.get('options_healthy'), 
#         'options_organic': request.form.get('options_organic'), 
#         'parking': request.form.get('parking'), 
#         'wifi' : request.form.get('wifi'), 
#         'user_id': current_user_id}

#         initial_user_prefs = model.User_Preference(**kwargs)

#         model.session.add(initial_user_prefs, user_id = current_user_id)
    
#     model.session.commit()
    
    
#     return redirect("/")


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
    

@app.route('/logout')
def logout_user():
    session.clear()
    print "This is what session looks like now %r" % session
    return redirect("/login")
  



if __name__ == "__main__":
    app.debug = True
    app.run()

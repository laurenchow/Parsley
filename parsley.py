#TODO: update requirements.txt
from flask import Flask, render_template, session, flash, redirect, request, g, jsonify
from passlib.hash import pbkdf2_sha256
from factual import Factual
import model, collections, os, jinja2, helper
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KEY = os.environ.get('FACTUAL_KEY')
SECRET= os.environ.get('FACTUAL_SECRET') 

app = Flask(__name__) 
app.secret_key = helper.app.secret_key
app.jinja_env.undefined = jinja2.StrictUndefined

# use g in a before_request function to check and see if a user is logged in -- if they are logged in you can save it in g    
@app.before_request
def load_user_id():
    g.user_id = session.get('user_id') 

@app.route('/', methods = ['GET'])
def index():
    """
    This function returns the app's homepage.
    """
    return render_template("index.html")
    
@app.route('/restaurants', methods = ['GET'])
def restos():
    """
    This function returns the app's restaurant submission template.
    """
    return render_template("restaurants.html")

@app.route('/restaurants', methods = ['POST'])
def other_restos():
    """
    This function: 
    (1) takes in user input for restaurants using Google Maps JS autocomplete. 
        If user input is incorrectly formatted, returns user to restaurants page
        to reenter.
    (2) checks DB to see if these restaurants are already entered. If not, makes
        a call to the Factual API to get information on restaurant and its features
        and inserts a new entry into restaurants and restaurant_features.
    (3) Updates user_restaurant_rating table to indicate that user likes these 
        restaurants.
    (4) calls function to suggest new restaurants 
    """
    current_user_id = session['user_id']
    restaurant1 = request.form.get('restaurant_1')
    restaurant2 = request.form.get('restaurant_2')
    restaurant3 = request.form.get('restaurant_3')      
    user_geo_input = request.form.get('user_geo') 
    feedback_cuisine_id = request.form.get('cuisines_similar') 

    if len(user_geo_input) !=5:
        user_info= model.session.query(model.User).filter_by(id = current_user_id).first()
        user_geo = user_info.zipcode
    else: 
        user_geo = request.form.get('user_geo') 
        #TODO: check that this is a valid zipcode
  
     
    if restaurant1 and restaurant2 and restaurant3:
        restaurant_ids = check_db_for_restos([restaurant1, restaurant2, restaurant3], user_geo)
     
        session['user_restaurant_ids'] = restaurant_ids
        session['user_geo'] = user_geo 
 

        if type(restaurant_ids) == list:
            add_restaurants_to_user_preferences(restaurant_ids)
            return suggest_new_resto(feedback_cuisine_id)
        else:
            flash("We don't have enough information on those restaurants. Please try some other restaurants.", "error")
            return render_template("restaurants.html")

    else:
        flash("Please re-enter using format from autocomplete.", "error")

        return render_template("restaurants.html")
        
def parse_restaurant_input(restaurant_text):
    """
    This function takes in three restaurants inputs formatted using Google Maps JS
    autocomplete (e.g., "Shake Shack, Madison Ave, New York, NY"), parses 
    restaurant name, city and state and returns this information in a dictionary.

    If information submitted in incorrect format, asks user to re-enter.
    """

    data = {}

    restaurant_split = restaurant_text.split(',')

    if restaurant_split and len(restaurant_split) >=3:
            #TODO: should this be 3 or 4
            if restaurant_split[0]:
                data['name'] = restaurant_split[0]
            if restaurant_split[-3]:
                data['city'] =restaurant_split[2]
            if restaurant_split[-2]:
                data['state'] = restaurant_split[3]
            if restaurant_split[-3] and restaurant_split[-2]:    
                data['geo'] = data['city']+data['state']
            return data
    else:
        flash("Please re-enter using format from autocomplete.", "error")
        return render_template("restaurants.html")
        
def check_db_for_restos(restaurant_data, user_geo):
    """ 
    Checks database for restaurants to see if they exist as entries yet. 
    If not, adds restaurants into database.
    """

    restaurant_ids = []

    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
 

    for restaurant in restaurant_data: 
        parsed_data = parse_restaurant_input(restaurant)
        db_entry = model.session.query(model.Restaurant).filter_by(name= parsed_data['name']).first() 
        

        if db_entry:
             restaurant_deets = db_entry.restaurant_features.get_all_data()
             if restaurant_deets:
                restaurant_ids.append(db_entry.id)
 
        else:
            new_resto = table.filters({'name':{'$bw':parsed_data['name']}})
            new_resto_data = new_resto.data() 
       
            if new_resto_data:
                new_restaurant = model.Restaurant()

                for item in new_resto_data: 
                    new_restaurant.set_from_factual(item)
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
    
    if restaurant_ids == []:
        flash("We need a bit more information, please try some other restaurants.")
        return redirect("/restaurants")
    else: 
        return restaurant_ids

#TODO: get this to work when you click on it from restaurants suggestion page
# @app.route('/refresh_restaurants', methods = ['GET', 'POST'])
# def show_different_restos(restaurant_ids):
#     pass

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
    else:
        user_preference = model.User_Restaurant_Rating()
        user_preference.restaurant_id = restaurant.id 
        user_preference.rating = feedback_restaurant_rating
        user_preference.user_id = session['user_id']
        model.session.add(user_preference)

    model.session.commit()
    return jsonify( { 'feedback_button_id': feedback_button_id} )

@app.route('/suggest_restaurant', methods = ['GET', 'POST'])
def suggest_new_resto(feedback_cuisine_id):
    """ This processes the user's input regarding favorite restaurants as well 
        as what their preferences are, then queries to determine suitable matches.

        It returns a list of restaurants from Factual along with a list of the 
        user's top-ranked features (if cuisine is selected, weights cuisine as well.)
    """ 

    if session.get('user_restaurant_ids'):
        rest_ids = session.get('user_restaurant_ids')
    
    user_input_rest_data = get_user_inputs(rest_ids)
    cuisine_type = filter_by_cuisine(user_input_rest_data, feedback_cuisine_id)
    
    sorted_restaurant_features_counter_keys = get_rest_features_similarities(user_input_rest_data) 
    db_result_new_restaurants_from_features = get_rest_features_results(sorted_restaurant_features_counter_keys, user_input_rest_data, cuisine_type)
    sk_cos_sim = sk_cosine_similarity(rest_ids, db_result_new_restaurants_from_features) 
    translated_sorted_rest_feat_sim_keys = convert_restaurant_features_to_normal_words(sorted_restaurant_features_counter_keys)

    new_restaurant_suggestion = check_resto_suggestions(sk_cos_sim) 

    # import pdb; pdb.set_trace()
        
    return render_template("new_restaurant.html", new_restaurant_suggestion = new_restaurant_suggestion, 
        translated_sorted_rest_feat_sim_keys = translated_sorted_rest_feat_sim_keys )

def filter_by_cuisine(user_input_rest_data, feedback_cuisine_id):
    """
    This function takes the user input and determines whether or not to filter restaurant recommendations by cuisine.
    If filtering by cuisine, returns list of cuisines to search for.
    """

    if feedback_cuisine_id == 'similar_cuisines':
        cuisine_type = "similar"

    else:
        cuisine_type = "all"

    return cuisine_type


def check_resto_suggestions(restaurants):
# def check_resto_suggestions(restaurants, cuisine_type): 
# def get_resto_suggestions(sk_cos_sim):
    """
    This function:
    (1) Takes the list of restaurant ids returned from a function 
    (2) Loops over list to remove any restaurants the user has already rated
    (3) Returns the edited list of dictionaries of database objects containing all restaurants, ordered by preference,
    to print on new_restaurants.html page.
    """

    new_restaurant_suggestion = []


    for rest_id in restaurants:
        already_rated = model.session.query(model.User_Restaurant_Rating).filter_by(restaurant_id = rest_id).first()
        if not already_rated:
            rest_data = model.session.query(model.Restaurant).get(rest_id)
            new_restaurant_suggestion.append(rest_data)

    return new_restaurant_suggestion

def get_user_inputs(rest_ids):
    """
    This function takes the restaurant ids from the three restaurants that the user inputs and creates a list 
    containing all DB data for those three restaurants.
    """
   
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

    restaurant_features_counter = {'alcohol': 0, 'groups_goodfor': 0, 'kids_goodfor': 0,
        'kids_menu': 0, 'meal_breakfast': 0, 'meal_dinner': 0, 'meal_deliver': 0, 
        'options_healthy': 0, 'options_glutenfree': 0, 'options_lowfat': 0, 
        'options_vegan': 0, 'options_vegetarian': 0, 'options_organic': 0, 'parking': 0, 
        'reservations':  0, 'wifi' : 0}
    
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

#TODO: pass cuisine and category to this function to evaluate whether or not to show all cuisines or all categories
def get_rest_features_results(sorted_restaurant_features_counter_keys, user_input_rest_data, cuisine_type):
# def get_rest_features_results(sorted_restaurant_features_counter_keys):
    """
    This function takes the ranked restaurant features, searches 
    for matching restaurants and returns restaurants that 
    match these features in the user's desired zipcode.

    If function determines there are insufficient number (less than 25) restaurants
    to suggest in desired user zipcode, will ping Factual for entries in that area.

    If a user opted to filter by cuisine, this function also filters by the top cuisines
    returned by earlier function filter_by_cuisine() by splitting on commas, creating
    a dictionary of incidences of that cuisine in all three restaurants with the cuisine as key
    then converting those key, value pairs to tuples and sorting for the most frequently listed
    cuisines.

    This function returns a list of restaurant ids.

    """

    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
    user_geo =  session['user_geo']  
 
    db_zip_density = model.session.query(model.Restaurant).filter_by(postcode = user_geo).all()
    db_restaurant_list = []
 
    if len(db_zip_density) >= 25:

        kwargs= {sorted_restaurant_features_counter_keys[0]: "1", sorted_restaurant_features_counter_keys[1]: "1", 
            sorted_restaurant_features_counter_keys[2]: "1"}

        # if cuisine_type == 'similar':
        if cuisine_type == 'all':
            rest_cuisines = {}
            for entry in range(len(user_input_rest_data)):
                each_restaurant = model.session.query(model.Restaurant_Category).filter_by(restaurant_id = user_input_rest_data[entry].id).first()
                
                if each_restaurant != None:
                    if each_restaurant.cuisine != None:
                        each_restaurant_cuisine = each_restaurant.cuisine
                        list_of_each_restaurant_cuisine = each_restaurant_cuisine.split(',')
                        for item in list_of_each_restaurant_cuisine:
                            if item!='':
                                cuisine_count = rest_cuisines.get(item, 0) + 1
                                rest_cuisines[item] = cuisine_count

            sorted_rest_cuisines = sorted(rest_cuisines.items(), key = lambda (k,v): v)
            sorted_rest_cuisines.reverse()
            sorted_rest_cuisines_keys = [x[0] for x in sorted_rest_cuisines]
           
            new_restaurant_suggestion_filtered_by_cuisine= model.session.query(model.Restaurant).filter_by(postcode = user_geo).outerjoin(model.Restaurant_Features).filter_by(**kwargs).outerjoin(model.Restaurant_Category).filter(model.Restaurant_Category.cuisine.like("%" + sorted_rest_cuisines_keys[0] + sorted_rest_cuisines_keys[1]+ "%")).group_by(model.Restaurant.id).limit(20).all()

            #writing a for loop here to try all the variables
            if len(new_restaurant_suggestion_filtered_by_cuisine) <= 3 :
                new_restaurant_suggestion_filtered_by_cuisine = model.session.query(model.Restaurant).filter_by(postcode = user_geo).outerjoin(model.Restaurant_Features).filter_by(**kwargs).outerjoin(model.Restaurant_Category).filter(model.Restaurant_Category.cuisine.like("%" + sorted_rest_cuisines_keys[0] + "%")).group_by(model.Restaurant.id).limit(25).all()
            
            # if new_restaurant_suggestion_filtered_by_cuisine == []:
                # new_restaurant_suggestion_filtered_by_cuisine = model.session.query(model.Restaurant).filter_by(postcode = user_geo).outerjoin(model.Restaurant_Features).filter_by(**kwargs).outerjoin(model.Restaurant_Category).filter(model.Restaurant_Category.cuisine.like("%" + sorted_rest_cuisines_keys[0] + "%")).group_by(model.Restaurant.id).limit(25).all()
            
            if new_restaurant_suggestion_filtered_by_cuisine == []:
                new_restaurant_suggestion_filtered_by_cuisine = model.session.query(model.Restaurant).filter_by(postcode = user_geo).outerjoin(model.Restaurant_Features).filter_by(**kwargs).outerjoin(model.Restaurant_Category).filter(model.Restaurant_Category.cuisine.like("%" + sorted_rest_cuisines_keys[1] + "%")).group_by(model.Restaurant.id).limit(25).all()

            for item in new_restaurant_suggestion_filtered_by_cuisine:
                  db_restaurant_list.append(item.id)
        else:
            new_restaurant_suggestion_from_features = model.session.query(model.Restaurant).filter_by(postcode = user_geo).outerjoin(model.Restaurant_Features).filter_by(**kwargs).group_by(model.Restaurant.id).limit(25).all()

            for item in new_restaurant_suggestion_from_features:
                db_restaurant_list.append(item.id)

        db_result_new_restaurants_from_features = db_restaurant_list
        #return the sorted features 

    else:
        # import pdb; pdb.set_trace()
        new_restaurant_suggestion_from_features = table.filters({"postcode": user_geo}).limit(50)
        # factual_restaurant_suggestion_from_features = table.filters({sorted_restaurant_features_counter_keys[0]: "1" ,
        # sorted_restaurant_features_counter_keys[1]: "1", sorted_restaurant_features_counter_keys[2]:"1", 
        # "postcode": user_geo}).limit(5)
          
        if new_restaurant_suggestion_from_features == []:
            return render_template("sorry.html") 
        # import pdb; pdb.set_trace()
        else: 
            db_result_new_restaurants_from_features = check_db_for_restos(new_restaurant_suggestion_from_features, user_geo)

    return db_result_new_restaurants_from_features

def sk_cosine_similarity(restaurant_ids, db_result_new_restaurants_from_features):
    """ 
    This function takes list of restaurant ids (from the new restaurants returned)
    and compares them to user's preferences to see how similar the restaurants are to
    a user's ideal restaurant using cosine similarity.

    It returns the list of restaurant ids ranked by cosine similarity values.
    """

    current_user_id = session['user_id']

    rest_ids = db_result_new_restaurants_from_features
    user_prefs = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()

    restaurant_features = {}
     
    restaurants_to_suggest = model.session.query(model.Restaurant).filter(model.Restaurant.id.in_(rest_ids)).all()

    for entry in range(len(restaurants_to_suggest)):
        rest_features_from_db = model.session.query(model.Restaurant_Features).filter_by(id = restaurants_to_suggest[entry].id).first()
        restaurant_features[restaurants_to_suggest[entry].name] = rest_features_from_db.get_all_data()

    restaurant_features[user_prefs.user_id] = user_prefs.get_all_data() 

    dv = DictVectorizer(sparse=True)
    x = dv.fit_transform(restaurant_features.values())
    x.todense()
 
    cs = cosine_similarity(x[0:1], x)

    cs = cs.tolist()
    
    rest_name_plus_cos_sim_value = collections.OrderedDict()

    for item in range(len(restaurants_to_suggest)):
        resto_id = restaurants_to_suggest[item].id
        rest_name_plus_cos_sim_value[resto_id] = cs[0][item+1]

    sorted_sk_cos_sim_results = sorted(rest_name_plus_cos_sim_value.items(), key = lambda (k,v): v)
    sorted_sk_cos_sim_results.reverse()
    sorted_sk_cos_sim_results_keys = [z[0] for z in sorted_sk_cos_sim_results]
     
    return sorted_sk_cos_sim_results_keys
        
         
@app.route('/get_restos', methods = ['GET'])
def new_restaurants():
    """
    This function gets restaurants for a certain zipcode and is not visible to the user.
    """
    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
    user_geo =  session['user_geo']   
    new_restaurants = table.filters({"postcode": 20006}).limit(50)
    check_db_for_restos(new_restaurants, user_geo)

    return "Success"

@app.route('/favorites', methods = ['GET'])
def user_favorites():
    """
    This function queries DB to determine what user favorites are.
    If user has filled out user preferences form or submitted any information on preferred restaurants,
    it will return all the restaurants a user has rated and display those on the page.
    If a user has not completed any, it will send the user to a page to submit more information.
    """
    current_user_id = session['user_id']
    single_user = model.session.query(model.User_Restaurant_Rating).filter_by(user_id = current_user_id).group_by(model.User_Restaurant_Rating.restaurant_id).all()  

    if single_user:
        return render_template("favorites.html", user = single_user)
    else:
         return render_template("sorry.html")
 
@app.route('/browse', methods = ['GET'])
def browse_new_rests():
    """ 
    This function allows the user to browse new restaurants based on user preferences
    and requires no new input from the user.
    """

    current_user_id = session['user_id']
    # if session['cuisine_type']:
    #     cuisine_type = session['cuisine_type']
    # else:
    #     cuisine_type = "all"

    current_user = model.session.query(model.User).filter_by(id = current_user_id).first()
    user_geo = current_user.zip

    user_preferences = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()

    if user_preferences:
        user_prefs_as_dict = {}
        user_prefs = user_preferences.get_all_data()

        for key, value in user_prefs.iteritems():
            user_prefs_as_dict[key] = getattr(user_prefs, key,value)

        for key, value in user_prefs.iteritems():
            user_prefs_as_dict[key] = int(user_prefs_as_dict[key])

        sorted_user_pref_results = sorted(user_prefs_as_dict.items(), key = lambda (k,v): v)
        sorted_user_pref_results.reverse()
        sorted_user_pref_results_keys = [x[0] for x in sorted_user_pref_results]

        kwargs = {sorted_user_pref_results_keys[0]: 1, sorted_user_pref_results_keys[1]: 1}
           
        restaurants = model.session.query(model.Restaurant).filter_by(postcode = user_geo).outerjoin(model.Restaurant_Features).filter_by(**kwargs).limit(25)

        rest_list = []

        for item in restaurants:
            rest_list.append(item.id)

        new_restaurant_suggestion = check_resto_suggestions(rest_list) 

        # import pdb; pdb.set_trace()

        translated_sorted_rests_from_user_prefs_keys = convert_restaurant_features_to_normal_words(sorted_user_pref_results_keys)

        return render_template("browse.html", new_restaurant_suggestion = new_restaurant_suggestion, 
                translated_sorted_rest_feat_sim_keys = translated_sorted_rests_from_user_prefs_keys)
        
    else:
        return render_template("sorry.html")

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
    """
    This function returns signup template. Once information is submitted, calls
    function to sign up user.
    """
    if request.method == "GET":
        return render_template("signup.html")
    else:
        return signup_user()

def signup_user():
    """
    This function requests information from the signup form, then returns the
    user to the welcome page via redirect after storing user_id and user_email in session.
    """
    user_email = request.form['email']
    user_password = request.form['password']
    user_first_name = request.form['first_name']
    user_last_name = request.form['last_name'] 

    already_registered = model.session.query(model.User).filter_by(email = user_email).first()

    if already_registered:
        flash("Looks like you already have an account. Want to try signing in?")

    secure_password = pbkdf2_sha256.encrypt(user_password, rounds=200000, salt_size=16) 

    new_user = model.User(email = user_email, password = secure_password, 
        first_name = user_first_name, last_name = user_last_name)

    model.session.add(new_user)
    model.session.commit() 
    
    current_user = model.session.query(model.User).filter_by(email = user_email).first()
    current_user_profile = model.User_Profile(user_id=current_user.id)

    model.session.add(current_user_profile)
    model.session.commit() 

    session['user_id'] = current_user.id
    session['user_email'] = current_user.email
        
    return redirect("/welcome")

@app.route('/welcome', methods = ['GET', 'POST'])
def new_user_welcome(): 
    """
    This function welcomes a new user upon signup and requests details for 
    initial user profile.
    """

    current_user_id = session['user_id']  

    if request.method == "GET":
        return render_template("welcome.html")
    else:
        return submit_user_details(current_user_id)

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

    return redirect("/user_profiles")

@app.route('/my_profile', methods = ['GET'])
def view_profile():
    current_user_id = session['user_id']
    single_user = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).group_by(model.User_Preference).all()  

    if single_user:
        return render_template("my_profile.html", user = single_user)

    else:
         return render_template("sorry.html")

@app.route('/user_profiles', methods = ['GET', 'POST'])
def user_profiles():
    """
    Determines if user has submitted preferences. If post method, 
    submits user pref data to the update_user_prefs function.
    """
    
    if request.method == "GET":
        return render_template("user_preferences.html")
    else:
        return update_user_profile()

def update_user_profile():
    """
    This function sets initial user preferences, which are stored in user_profiles table. 
    Users can select to update baseline preferences, otherwise they will stay set to initial 
    values.
    """

    current_user_id = session['user_id']  

    
    existing_user_prefs = model.session.query(model.User_Profile).filter_by(user_id = current_user_id).first()

    if existing_user_prefs:

        kwargs = {'accessible_wheelchair': request.form.get('accessible_wheelchair'),
        'kids_goodfor': request.form.get('kids_goodfor'),
        'options_healthy': request.form.get('options_healthy'), 
        'options_organic': request.form.get('options_organic'), 
        'parking': request.form.get('parking'), 'wifi' : request.form.get('wifi'), 
        'alcohol_byob': 0, 'alcohol_bar': 0, 'alcohol_beer_wine': 0, 'alcohol': 0,
        'groups_goodfor': 0, 'kids_goodfor':0, 'kids_menu': 0, 'meal_breakfast': 0,
        'meal_cater': 0, 'meal_deliver':  0, 'meal_dinner': 0, 'meal_lunch': 0, 
        'open_24hrs': 0, 'options_glutenfree': 0, 'options_lowfat': 0, 'options_vegan': 0, 
        'options_vegetarian': 0, 'parking': 0, 'parking_free': 0, 'parking_garage': 0, 
        'parking_lot': 0, 'parking_street': 0, 'parking_valet': 0, 'parking_validated': 0, 
        'payment_cashonly': 0, 'room_private': 0, 'reservations':  0, 'seating_outdoor': 0, 
        'smoking': 0, 'user_id': current_user_id}
 
        new_user_prof = model.User_Profile(id = existing_user_prefs.id, **kwargs)
        new_user_prefs = model.User_Preference(id = existing_user_prefs.id, **kwargs) 

        model.session.merge(new_user_prefs)
        model.session.merge(new_user_prof)

    else:
        kwargs = {'accessible_wheelchair': request.form.get('accessible_wheelchair'),
        'kids_goodfor': request.form.get('kids_goodfor'),
        'options_healthy': request.form.get('options_healthy'), 
        'options_organic': request.form.get('options_organic'), 
        'parking': request.form.get('parking'), 'wifi' : request.form.get('wifi'), 
        'alcohol_byob': 0, 'alcohol_bar': 0, 'alcohol_beer_wine': 0, 'alcohol': 0,
        'groups_goodfor': 0, 'kids_goodfor':0, 'kids_menu': 0, 'meal_breakfast': 0,
        'meal_cater': 0, 'meal_deliver':  0, 'meal_dinner': 0, 'meal_lunch': 0, 
        'open_24hrs': 0, 'options_glutenfree': 0, 'options_lowfat': 0, 'options_vegan': 0, 
        'options_vegetarian': 0, 'parking': 0, 'parking_free': 0, 'parking_garage': 0, 
        'parking_lot': 0, 'parking_street': 0, 'parking_valet': 0, 'parking_validated': 0, 
        'payment_cashonly': 0, 'room_private': 0, 'reservations':  0, 'seating_outdoor': 0, 
        'smoking': 0, 'user_id': current_user_id}


        initial_user_prof = model.User_Profile(**kwargs)
        initial_user_prefs = model.User_Preference(id = existing_user_prefs.id, **kwargs)
        model.session.add(initial_user_prof)
        model.session.add(initial_user_prefs)
    
    model.session.commit() 

    return redirect("/")
 
@app.route('/user_preferences', methods = ['GET', 'POST'])
def user_preferences():
    """
    Determines if user has submitted preferences. If post method, 
    submits user pref data to the update_user_prefs function.
    """

    # current_user_id = session['user_id']   

    if request.method == "GET":
        return render_template("user_preferences.html")
    else:
        return update_user_prefs()

def update_user_prefs():
    """
    Looks up existing user preferences and loads the restaurants a user has reviewed.
    For each restaurant a user has reviewed, increments the feature in relevant
    row in user_preferences to show that the user strongly values that feature.
    """

    current_user_id = session['user_id']   
    existing_user_prefs = model.session.query(model.User_Profile).filter_by(user_id = current_user_id).first()
    
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
                    try:
                        existing_feature_count = int(user_prefs_to_store[key])
                    except:
                        user_prefs_to_store[key] = None
 
                    if user_prefs_to_store[key] == None:
                        user_prefs_to_store[key] = 0
                    if rest_features[key] > 0:
                        user_prefs_to_store[key] = existing_feature_count + 1
                             
            kwargs = user_prefs_to_store
            new_user_prefs = model.User_Preference(id = existing_user_prefs.id, user_id = current_user_id, **kwargs)
            model.session.merge(new_user_prefs)

    else:
        update_user_profile()

    model.session.commit() 

    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def show_login():
    if request.method == "GET":
        return render_template("login.html")
    else: 
        return login_user()

def login_user():
    """
    This function allows registered users to log in and checks their password against
    the hashed, salted entry using pbkdf2_sha256 encryption.
    """
    user_email = request.form['email'] 
    current_user = model.session.query(model.User).filter_by(email = user_email).first()
    
    if current_user:
        input_password = request.form['password']
        
        if pbkdf2_sha256.verify(input_password, current_user.password):
            session['user_email'] = current_user.email    
            session['user_id'] = current_user.id

            return redirect("/")    
    
        else:
            flash("Invalid username or password", "error")
            return redirect("/login") 
    else:
        flash("Invalid username or password", "error")
        return redirect("/login")   


@app.route('/logout')
def logout_user():
    """
    This function clears the user session.
    """
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.debug = True
    app.run()

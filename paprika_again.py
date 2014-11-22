from flask import Flask, render_template, session, flash, redirect, request, g
from passlib.hash import pbkdf2_sha256
from factual import Factual
import model
import os
import jinja2

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

    print "Here's some new data %r" % restaurant1_data

    print "Here's some new data for restaurant 2 %r" % restaurant2_data


    print "Here's some new data for 3 %r" % restaurant3_data
    #TODO: Make it so that if it isn't in factual, a box prompts up asking you for another one

    restaurant_data = ping_factual([restaurant1, restaurant2, restaurant3], user_geo)
    restaurant_ids = check_db_for_restos(restaurant_data)

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
            #check to see if restaurant details are in the DB for this restaurant
            #if not add it, if it is check to see that it's still the same
                for item in restaurant_deets:
                    db_result = model.session.query(model.Restaurant).filter_by(factual_id = item['factual_id']).first() 

                    if db_result:
                        print "Here's what is stored in DB right now for name ID and address %r %r %r" % (db_result.name, db_result.id, db_result.address)
                        db_result.set_from_factual(item)
                        restaurant_ids.append(db_result.id)

                        model.session.add(db_result)

                        # restaurant_update = model.Restaurant(name= name, 
                        #     locality = locality, country = country, postcode = postcode, 
                        #     region = region, address = address, tel = tel, longitude = longitude, 
                        #     latitude = latitude, price = price, rating = rating, 
                        #     address_extended = address_extended, attire_prohibited = attire_prohibited, 
                        #     attire_required = attire_required, chain_id = chain_id, chain_name = chain_name,
                        #     email = email, fax = fax, founded = founded, owner = owner, 
                        #     po_box = po_box, website = website)
                        
                        
                        db_result_features = model.session.query(model.Restaurant_Features).filter_by(factual_id = item['factual_id']).first() 
                        
                        db_result_features.set_from_factual(item)
                        
                        model.session.add(db_result_features)
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
                        model.session.commit()

                        restaurant_ids.append(new_restaurant.id)
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

                    # restaurant_update = model.Restaurant(name= name, 
                    #     locality = locality, country = country, postcode = postcode, 
                    #     region = region, address = address, tel = tel, longitude = longitude, 
                    #     latitude = latitude, price = price, rating = rating, 
                    #     address_extended = address_extended, attire_prohibited = attire_prohibited, 
                    #     attire_required = attire_required, chain_id = chain_id, chain_name = chain_name,
                    #     email = email, fax = fax, founded = founded, owner = owner, 
                    #     po_box = po_box, website = website)
                    
                    
                    db_result_features = model.session.query(model.Restaurant_Features).filter_by(factual_id = item['factual_id']).first() 
                    
                    db_result_features.set_from_factual(item)
                    
                    model.session.add(db_result_features)
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
                    model.session.commit()

                    restaurant_ids.append(new_restaurant.id)

    return restaurant_ids




@app.route('/suggest_restaurant', methods = ['GET', 'POST'])
def suggest_new_resto(restaurant_data):
    """ This processes the user's input regarding favorite restaurants as well 
        as what their preferences are, then queries to determine suitable matches.
    """ 

    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')
    user_geo = session['user_geo']

    restaurant_data = []
    if session.get('user_restaurant_ids'):
        rest_ids = session.get('user_restaurant_ids')
        for rest_id in rest_ids:
            resto_data = model.session.query(model.Restaurant).get(rest_id)
            restaurant_data.append(resto_data)

    #TODO: have something in Javascript so you have to type in restaurants or else
    for restaurant in restaurant_data:
        kwargs = restaurant.restaurant_features.get_all_data()
        print "Here's what is in kwargs %r" % kwargs

    current_user_id = session['user_id']  
    user_preferences = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()


    #TODO: CLEAR RESTAURANT ID SESSION
    #TODO: add category to this and cuisine
    #TODO: figure out if you can make evaluating similarities a function once it works
    

    # restaurant_similarity = {'cuisine': [], 'category_labels': [], 'category_ids': []}
    # #you still need to get the rating and price but those are in restaurant not categories
  

    # for entry in range(len(restaurant_data)):
    #     # import pdb; pdb.set_trace()
    #     restaurant_model = restaurant_data[entry]
    #     restaurant_categories = restaurant_model.restaurant_categories

    #     for feature in restaurant_similarity.keys():
    #         restaurant_value = getattr(restaurant_categories, feature)
    #         if restaurant_value:
    #             restaurant_similarity[feature].append(restaurant_value)


    # print "Here's what's stored in restaurant_similarity"
    # print "A count of how often each variable happened in each restaurant %r" % restaurant_similarity


    # sorted_restaurant_similarity = sorted(restaurant_similarity.items(), key = lambda (k,v): v)
    # sorted_restaurant_similarity.reverse()
    # # you could do that on javascript side

    # sorted_restaurant_similarity_keys = [x[0] for x in sorted_restaurant_similarity]

    # print "Here are the keys of three most important things outside of features %r" % sorted_restaurant_similarity_keys

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
        # import pdb; pdb.set_trace()
        restaurant_model = restaurant_data[entry]
        restaurant_features = restaurant_model.restaurant_features
        #are these two lines accomplisting anyhting?

        for feature in restaurant_features_similarity.keys():
            restaurant_feature_value = getattr(restaurant_features, feature)
            if restaurant_feature_value:
                restaurant_features_similarity[feature] += 1


    print "Here's what's stored in restaurant_features_similarity"
    print "A count of how often each variable happened in each restaurant %r" % restaurant_features_similarity

    sorted_restaurant_features_similarity = sorted(restaurant_features_similarity.items(), key = lambda (k,v): v)
    sorted_restaurant_features_similarity.reverse()
    # you could do that on javascript side

    sorted_restaurant_features_similarity_keys = [x[0] for x in sorted_restaurant_features_similarity]

    print "Here are the keys of three most important features %r" % sorted_restaurant_features_similarity_keys
        #loop over three restaurants and increase counter in 
    
    #TODO: could you make it so it queries for all things that are 3 out of 3?

    new_restaurant_suggestion = table.filters({sorted_restaurant_features_similarity_keys[0]: "1" ,
     sorted_restaurant_features_similarity_keys[1]: "1", sorted_restaurant_features_similarity_keys[2]:"1", "postcode": user_geo}).limit(5)
    
    #TODO: is this the most sensible way to handle errors?    
    if new_restaurant_suggestion == []:
        return render_template("sorry.html")
    #if it returns nothing, reload the page?

    # should also ask cuisine
    # look at category as well  are these all dinner? lunch?
    # should ask preference on region
    # look at neighborhoods also if they're all in common 


    # put in a bunch of if statements here in case none of those parameters are met
    # assign binary values to each user preference because you have to for queries
    # compare user preferences to these three restaurants
    # search factual for similar restaurants
    # suggest a new restaurant
    # you'll want to ask if they like this restaurant also
    #TODO: redo search if no results, figure out how to deal with


    print "" "-----------IS this new_restaurant_suggestion working?--------"
    print new_restaurant_suggestion.data()
    # add all these suggestions to DB

    # TODO: figure out function to add to DB because this is rewriting everything
    list_new_restaurant_suggestion = new_restaurant_suggestion

    print "" "-----------IS this list working?-------- %r" % list_new_restaurant_suggestion

    check_db_for_restos(list_new_restaurant_suggestion)

    return render_template("new_restaurant.html", new_restaurant_suggestion = new_restaurant_suggestion, 
        sorted_restaurant_features_similarity_keys = sorted_restaurant_features_similarity_keys)



@app.route('/user', methods = ['GET'])
def user_profile():
    return render_template("user.html")


@app.route('/favorites', methods = ['GET'])
def user_favorites():
    return render_template("favorites.html")
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
    print "This is what user_password is stored as %r" % type(user_password)

    already_registered = model.session.query(model.User).filter_by(email = user_email).first()

    if already_registered:
        flash("Looks like you already have an account. Want to try signing in?")

    secure_password = pbkdf2_sha256.encrypt(user_password, rounds=200000, salt_size=16)
    print "this is the secure hashed password %r" % secure_password
    #put something in here about making good passwords with uppercase and flash suggestion
    new_user = model.User(email = user_email, password = secure_password)

    model.session.add(new_user)
    model.session.commit() 
    
    current_user = model.session.query(model.User).filter_by(email = user_email).first()

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
    



@app.route('/user_preferences', methods = ['GET', 'POST'])
def user_preferences():
    if request.method == "GET":
        return render_template("user_preferences.html")
    else:
        return submit_user_preferences()

def submit_user_preferences(): 
    current_user_id = session['user_id']  
    print "This is where you'll show what the user says they prefer"  
    print "This is who is logged in right now %r" % current_user_id
    # new_user_prefs_info = model.session.query(model.User_Preference).filter_by(user_id = current_user_id).first()

    # print "This exists!!! %r" % new_user_prefs_info
    # if new_user_prefs_info:
    if current_user_id:
        kwargs = {'accessible_wheelchair': request.form['accessible_wheelchair'],
        'kids_goodfor': request.form['kids_goodfor'],
        'options_healthy': request.form['options_healthy'], 
        'options_organic': request.form['options_organic'], 
        'parking': request.form['parking'], 
        'wifi' : request.form['wifi'], 'user_id': current_user_id}

        new_user_prefs = model.User_Preference(**kwargs)
        model.session.merge(new_user_prefs)
        model.session.commit()
        
        return redirect("/")

    #this is just the full list for kwargs when you want to use it
    # if new_user_prefs_info:
    #     kwargs = {'accessible_wheelchair': request.form['accessible_wheelchair'],
    #     'alcohol_byob': request.form['alcohol_byob'], 'alcohol_bar':request.form['alcohol_bar'],
    #     'alcohol_beer_wine': request.form['alcohol_beer_wine'], 'alcohol': request.form['alcohol'],
    #     'groups_goodfor':  request.form['groups_goodfor'], 'kids_goodfor': request.form['kids_goodfor'],
    #     'kids_menu': request.form['kids_menu'], 'meal_breakfast':  request.form['meal_breakfast'],
    #     'meal_dinner':  request.form['meal_dinner'], 'meal_deliver':  request.form['meal_deliver'],
    #     'options_healthy': request.form['options_healthy'] , 
    #     'options_glutenfree': request.form['options_glutenfree'], 
    #     'options_lowfat': request.form['options_lowfat'], 
    #     'options_vegan': request.form['options_vegan'], 
    #     'options_vegetarian':  request.form['options_vegetarian'], 
    #     'options_organic': request.form['options_organic'], 'parking': request.form['parking'], 
    #     'reservations':  request.form['reservations'],
    #     'wifi' : request.form['wifi']}

      
        
  
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

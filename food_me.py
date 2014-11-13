from flask import Flask, render_template, session, flash, redirect, request, g
from passlib.hash import pbkdf2_sha256
from factual import Factual
import model
import os
import jinja2

KEY = os.environ.get('FACTUAL_KEY')
SECRET= os.environ.get('FACTUAL_SECRET')

app = Flask(__name__) 
app.secret_key = ')V\xaf\xdb\x9e\xf7k\xccm\x1f\xec\x13\x7fc\xc5\xfe\xb0\x1dc\xf9\xcfz\x92\xe8'
app.jinja_env.undefined = jinja2.StrictUndefined


# use g in a before_request function to check and see if a user is logged in -- if they are logged in you can save it in g    
@app.before_request
def load_user_id():
    g.user_id = session.get('user_id')

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template("index.html")
    
@app.route('/restaurants', methods = ['GET', 'POST'])
def restos():
    if request.method == "GET":
        return render_template("restaurants.html")
    else:
        submit_resto_list()
        return render_template("new_restaurant.html")
        
# use jquery AJAX here to add on same page
# show some things only when logged in

def submit_resto_list():

    restaurant1 = request.form['restaurant_1']
    restaurant2 = request.form['restaurant_2']
    restaurant3 = request.form['restaurant_3']      
    user_geo = request.form['user_geo'] 

    return ping_factual(restaurant1, restaurant2, restaurant3, user_geo)
    #figure out how to remove everything after restaurant name
    #look up clustering using categoriacl information


def ping_factual(restaurant1, restaurant2, restaurant3, user_geo):

    factual = Factual(KEY, SECRET)
    table = factual.table('restaurants')

    restaurant_data = [] 

    #add in user_geo here
    q1 = table.search("'restaurant1' 'user_geo'").limit(1)
    print "Here's what's stored in Factual for %r" %restaurant1
    print q1.data()
    print q1.get_url()
    restaurant_data.append(q1)

    q2 = table.search(restaurant2).limit(1)
    print "Here's what's stored in Factual for %r" %restaurant2
    print q2.data()
    print q2.get_url()
    restaurant_data.append(q2)
    
    q3 = table.search(restaurant3).limit(1)
    print "Here's what's stored in Factual for %r" %restaurant3
    print q3.data()
    print q3.get_url()
    restaurant_data.append(q3)

    print "Here's the restaurant inputs as a list %r" % restaurant_data
    
    return check_db_for_restos(restaurant_data)

    

def check_db_for_restos(restaurant_data):
    for entry in range(len(restaurant_data)):
        print "Here's what came in from Factual %r" % restaurant_data[entry]
      
        #searching the database seems to need to be case-sensitive for now, make it case insensitive
        restaurant_deets = restaurant_data[entry].data()
        print "Here are some deets %r" % restaurant_deets
        if restaurant_deets == []:
            print "****This is empty, you'll want a new restaurant here****"
            pass
        else:
        #check to see if restaurant details are in the DB for this restaurant
        #if not add it, if it is check to see that it's still the same
        
            for item in restaurant_deets:
                db_result = model.session.query(model.Restaurant).filter_by(factual_id = item['factual_id']).first() 

                if db_result:
                    print "Here's what is stored in DB right now for name ID and address %r %r %r" % (db_result.name, db_result.id, db_result.address)
                    db_result.name = item.get("name", None)
                    db_result.locality = item.get("locality", None)
                    db_result.country = item.get("country", None)
                    db_result.postcode = item.get("postcode", None)
                    db_result.region = item.get("region", None)
                    db_result.address = item.get("address", None)
                    db_result.longitude = item.get("longitude", None)
                    db_result.price = item.get("price", None)
                    db_result.rating = item.get("rating", None)
                    db_result.latitude = item.get("latitude", None)
                    db_result.tel = item.get("tel" , None)
                    db_result.address_extended = item.get("address_extended" , None)
                    db_result.attire_prohibited= item.get("attire_prohibited" , None)
                    db_result.attire_required= item.get("attire_required" , None)
                    db_result.chain_id= item.get("chain_id" , None)
                    db_result.chain_name= item.get("chain_name" , None)
                    db_result.email= item.get("email" , None)
                    db_result.fax= item.get("fax" , None)
                    db_result.founded= item.get("founded" , None)
                    db_result.owner= item.get("owner" , None)
                    db_result.website = item.get("website", None)
                    db_result.po_box= item.get("po_box", None)


                    model.session.add(db_result)
                    model.session.commit()

                    # restaurant_update = model.Restaurant(name= name, 
                    #     locality = locality, country = country, postcode = postcode, 
                    #     region = region, address = address, tel = tel, longitude = longitude, 
                    #     latitude = latitude, price = price, rating = rating, 
                    #     address_extended = address_extended, attire_prohibited = attire_prohibited, 
                    #     attire_required = attire_required, chain_id = chain_id, chain_name = chain_name,
                    #     email = email, fax = fax, founded = founded, owner = owner, 
                    #     po_box = po_box, website = website)
                    
                    
                    db_result_features = model.session.query(model.Restaurant_Features).filter_by(factual_id = item['factual_id']).first() 
                    db_result_features.accessible_wheelchair= item.get("accessible_wheelchair", None)
                    db_result_features.alcohol_byob =item.get("alcohol_byob", None)
                    db_result_features.alcohol_bar = item.get("alcohol_bar", None)
                    db_result_features.alcohol_beer_wine = item.get("alcohol_beer_wine", None)
                    db_result_features.alcohol = item.get("alcohol", None)
                    db_result_features.groups_goodfor=  item.get("groups_goodfor", None)
                    db_result_features.kids_goodfor=  item.get("kids", None)
                    db_result_features.kids_menu =  item.get("kids_menu", None)
                    db_result_features. meal_breakfast=  item.get("meal_breakfast", None)
                    db_result_features.meal_cater=  item.get("meal_cater", None)
                    db_result_features.meal_deliver=  item.get("meal_deliver", None)
                    db_result_features.meal_dinner= item.get("meal_dinner", None)
                    db_result_features.meal_lunch =  item.get("meal_lunch", None)
                    db_result_features.meal_takeout=  item.get("meal_takeout", None)
                    db_result_features.open_24hrs=  item.get("open_24hrs", None)
                    db_result_features.options_glutenfree  =  item.get("options_glutenfree", None)
                    db_result_features.options_lowfat  =  item.get("options_lowfat", None)
                    db_result_features.options_organic =  item.get("options_organic", None)
                    db_result_features.options_healthy=  item.get("options_healthy", None)
                    db_result_features.options_vegan=  item.get("options_vegan", None)
                    db_result_features.options_vegetarian=  item.get("options_vegetarian", None)
                    db_result_features.parking = item.get("parking", None)
                    db_result_features.parking_free =  item.get("parking_free", None)
                    db_result_features.parking_garage =  item.get("parking_garage", None)
                    db_result_features.parking_lot=  item.get("parking_lot", None)
                    db_result_features.parking_street=  item.get("parking_street", None)
                    db_result_features.parking_valet=  item.get("parking_valet", None)
                    db_result_features.parking_validated = item.get("parking_validated", None)
                    db_result_features.payment_cashonly=  item.get("payment_cashonly", None)
                    db_result_features.reservations = item.get("rese", None)
                    db_result_features.room_private= item.get("room_private", None)
                    db_result_features.seating_outdoor=  item.get("seating_outdoor", None)
                    db_result_features.smoking=  item.get("smoking", None)
                    db_result_features.wifi= item.get("wi", None)

                    
                    model.session.add(db_result_features)
                    model.session.commit()

                else:
                    print "***NOT IN DATABASE YET***"
                    #use get to check for keys, otherwise make it none
                    name = item.get("name", None)
                    factual_id = item.get("factual_id", None)
                    locality = item.get("locality", None)
                    country = item.get("country", None)
                    postcode = item.get("postcode", None)
                    region = item.get("region", None)
                    address = item.get("address", None)
                    longitude = item.get("longitude", None)
                    price = item.get("price", None)
                    rating = item.get("rating", None)
                    latitude = item.get("latitude", None)
                    tel = item.get("tel" , None)
                    address_extended = item.get("address_extended" , None)
                    attire_prohibited= item.get("attire_prohibited" , None)
                    attire_required= item.get("attire_required" , None)
                    chain_id= item.get("chain_id", None)
                    chain_name= item.get("chain_name", None)
                    email= item.get("email" , None)
                    fax= item.get("fax" , None)
                    founded= item.get("founded" , None)
                    owner= item.get("owner" , None)
                    website = item.get("website", None)
                    po_box= item.get("po_box", None)


                   
                    new_restaurant = model.Restaurant(name= name, factual_id= factual_id, 
                        locality = locality, country = country, postcode = postcode, 
                        region = region, address = address, tel = tel, longitude = longitude, 
                        latitude = latitude, price = price, rating = rating, 
                        address_extended = address_extended, attire_prohibited = attire_prohibited, 
                        attire_required = attire_required, chain_id = chain_id, chain_name = chain_name,
                        email = email, fax = fax, founded = founded, owner = owner, 
                        po_box = po_box, website = website)
                    model.session.add(new_restaurant)
                    model.session.commit()

                    
                    accessible_wheelchair= item.get("accessible_wheelchair", None)
                    alcohol_byob =item.get("alcohol_byob", None)
                    alcohol_bar = item.get("alcohol_bar", None)
                    alcohol_beer_wine = item.get("alcohol_beer_wine", None)
                    alcohol = item.get("alcohol", None)
                    groups_goodfor=  item.get("groups_goodfor", None)
                    kids_goodfor=  item.get("kids", None)
                    kids_menu =  item.get("kids_menu", None)
                    meal_breakfast=  item.get("meal_breakfast", None)
                    meal_cater=  item.get("meal_cater", None)
                    meal_deliver=  item.get("meal_deliver", None)
                    meal_dinner= item.get("meal_dinner", None)
                    meal_lunch =  item.get("meal_lunch", None)
                    meal_takeout=  item.get("meal_takeout", None)
                    open_24hrs=  item.get("open_24hrs", None)
                    options_glutenfree  =  item.get("options_glutenfree", None)
                    options_lowfat  =  item.get("options_lowfat", None)
                    options_organic =  item.get("options_organic", None)
                    options_healthy=  item.get("options_healthy", None)
                    options_vegan=  item.get("options_vegan", None)
                    options_vegetarian=  item.get("options_vegetarian", None)
                    parking = item.get("parking", None)
                    parking_free =  item.get("parking_free", None)
                    parking_garage =  item.get("parking_garage", None)
                    parking_lot=  item.get("parking_lot", None)
                    parking_street=  item.get("parking_street", None)
                    parking_valet=  item.get("parking_valet", None)
                    parking_validated = item.get("parking_validated", None)
                    payment_cashonly=  item.get("payment_cashonly", None)
                    reservations = item.get("rese", None)
                    room_private= item.get("room_private", None)
                    seating_outdoor=  item.get("seating_outdoor", None)
                    smoking=  item.get("smoking", None)
                    wifi= item.get("wi", None)
                    reservations = item.get("reservations", None)


                    new_restaurant_features = model.Restaurant_Features(accessible_wheelchair = accessible_wheelchair,
                        alcohol_bar = alcohol_bar, alcohol_beer_wine = alcohol_beer_wine, alcohol_byob = alcohol_byob,
                        alcohol = alcohol, groups_goodfor = groups_goodfor, kids_goodfor = kids_goodfor,
                        kids_menu = kids_menu, meal_breakfast = meal_breakfast, meal_cater = meal_cater,
                        meal_deliver = meal_deliver, meal_dinner = meal_dinner, meal_lunch = meal_lunch,
                        meal_takeout = meal_takeout, open_24hrs = open_24hrs, options_glutenfree = options_glutenfree,
                        options_lowfat = options_lowfat, options_organic = options_organic, options_healthy = options_healthy,
                        options_vegan = options_vegan, options_vegetarian = options_vegetarian, parking = parking, 
                        parking_free = parking_free, parking_garage = parking_garage, parking_lot = parking_lot,
                        parking_street = parking_street, parking_valet = parking_valet, parking_validated = parking_validated,
                        payment_cashonly = payment_cashonly, reservations = reservations, room_private = room_private,
                        seating_outdoor = seating_outdoor, smoking = smoking, wifi = wifi, factual_id = factual_id)
                    
                    model.session.add(new_restaurant_features)
                    model.session.commit()

    return redirect("/")  
#     return suggest_new_resto(restaurant_data)

# def suggest_new_resto(restaurant_data):

#     # factual = Factual(KEY, SECRET)
#     # table = factual.table('restaurants')

#     # if restaurant_data[0].data() != []:
#     #     # new_q1 = table.search("'restaurant_data[0].name").limit(1)
#     #     #figure out how many times each parameter is present in the three entries
#     #     print "*** YOU GOT THE QUERY TO WORK AND SOMETHING EXISTS IN HERE"
#     # else:
#     #     print "*******You need to type in a different restaurant****"
         
#     #you'll want to ask if they like this restaurant also
#     return render_template("new_restaurant.html")

@app.route('/signup', methods = ['GET', 'POST'])
def user_signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        return signup_user()


def signup_user():
    #make this offer to let you signup with Facebook
    #how to make this all popup with JS?
    if session:
        print "User is already signed in"
        flash("Looks like you're already signed in! Did you want to sign in as someone else?", "error")
        return render_template("login.html")
    else:
        user_email = request.form['email']
        user_password = request.form['password']
        print "This is what user_password is stored as %r" % type(user_password)
        # if len(user_password) <= 4:
        #     flash("You need a longer password.")
        #     return redirect("/signup")
        # elif user_password.isalpha() == True:
        #     flash("You need a more secure password.")
        #     return redirect("/signup")
        # else:
        secure_password = pbkdf2_sha256.encrypt(user_password, rounds=200000, salt_size=16)
        print "this is the secure hashed password %r" % secure_password
        #put something in here about making good passwords with uppercase and flash suggestion
        new_user = model.User(email = user_email, password = secure_password)

        model.session.add(new_user)
        model.session.commit() 

        current_user = model.session.query(model.User).filter_by(email = user_email).first()
        session['user_id'] = current_user.id
        session['user_email'] = current_user.email
            
        print session
        return redirect("/welcome")

@app.route('/welcome', methods = ['GET', 'POST'])
def new_user_welcome():
    if request.method == "GET":
        return render_template("welcome.html")
    else:
        return submit_user_details()

def submit_user_details():
    current_user_id = session['user_id']

    print "Here's the current user id %r" % session['user_id']

    new_user_info = model.session.query(model.User).filter_by(id = current_user_id).first()

    print "I don't know what's broken"
    print "Here's what is stored in new_user_info ID %r" % new_user_info.id 
    new_user_age = request.form['age']

    print "I still don't know what's broken"
    new_user_gender = request.form['gender']

    print "I STILL don't know what's broken"
    new_user_zip = request.form['zip']

    print "I still STILL STILL don't know what's broken"

    new_user_info = model.User(id = current_user_id, age = new_user_age, 
        gender = new_user_gender, zip = new_user_zip)

    model.session.merge(new_user_info)
    model.session.commit()

    print "Here's the current user age %r" % new_user_info.age 

    print "This is where you'll show what the user says they prefer"    
    return redirect("/")

@app.route('/user_prefs', methods = ['GET'])
def user_prefs():
    print "This is where you'll show what the user says they prefer"    
    return render_template("slider.html")

@app.route('/login', methods=['GET', 'POST'])
def show_login():
    if request.method == "GET":
        return render_template("login.html")
    else: 
        return login_user()

def login_user():
    user_email = request.form['email']

    if session:
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

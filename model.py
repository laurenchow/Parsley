from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


ENGINE = None
Session = None

engine = create_engine("sqlite:///paprika_spice.db", echo=False)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))

Base = declarative_base()
Base.query = session.query_property()


ENGINE= None
Session= None
Base = declarative_base()

class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True)
    age = Column(String(64), nullable=True)
    gender = Column(String(64), nullable=True)
    occupation =  Column(String(64), nullable=True)
    zip = Column(String(64), nullable=True)
    email = Column(String(64), nullable=True)
    password = Column(String(256), nullable=True)
    timestamp = Column(Integer, nullable=True)

    # make a quick form to get additional user demo info for machine learning

    age = Column(Integer, nullable=True)
    zipcode =  Column(String(15), nullable= True) 


#     # Flask-Login integration
#     def is_authenticated(self):
#         return True

#     def is_active(self):
#         return True

#     def is_anonymous(self):
#         return False

#     def get_id(self):
#         return self.id

#     # Required for administrative interface
#     def __unicode__(self):
#         return self.username

# class LoginForm(form.Form):
#     login = fields.TextField(validators=[validators.required()])
#     password = fields.PasswordField(validators=[validators.required()])

#     def validate_login(self, field):
#         user = self.get_user()

#         if user is None:
#             raise validators.ValidationError('Invalid user')

#         # we're comparing the plaintext pw with the the hash from the db
#         if not check_password_hash(user.password, self.password.data):
#         # to compare plain text passwords use
#         # if user.password != self.password.data:
#             raise validators.ValidationError('Invalid password')

#     def get_user(self):
#         return db.session.query(User).filter_by(login=self.login.data).first()


# class RegistrationForm(form.Form):
#     login = fields.TextField(validators=[validators.required()])
#     email = fields.TextField()
#     password = fields.PasswordField(validators=[validators.required()])

#     def validate_login(self, field):
#         if db.session.query(User).filter_by(login=self.login.data).count() > 0:
#             raise validators.ValidationError('Duplicate username')    # rest = models.Restaurant()
#     # rest.name = "Bob's"

    # factual_to_rest():
    #     for key (fact_resp):
    #         if key == ""
    #         switch statement

class Restaurant(Base):
    __tablename__="restaurants"

    id = Column(Integer, primary_key=True) #autoincrement
    name = Column(String(64), nullable=True)
    address = Column(String(64), nullable=True) 
    address_extended =  Column(String(128), nullable=True) 
    attire = Column(String(64), nullable=True) 
    attire = Column(String(64), nullable=True) 
    attire_prohibited = Column(String(64), nullable=True) 
    attire_required = Column(String(64), nullable=True) 
    chain_id = Column(String(64), nullable=True) 
    chain_name = Column(String(64), nullable=True) 
    country = Column(String(64), nullable=True) 
    email = Column(String(64), nullable=True) 
    factual_id = Column(String(128), nullable=True) 
    fax = Column(Integer, nullable=True)
    founded = Column(String(64), nullable=True)
    hours = Column(String(64), nullable=True) 
    hours_display = Column(String(64), nullable=True) 
    latitude =  Column(Float(Precision=64), nullable=True)
    locality = Column(String(64), nullable=True) 
    longitude = Column(Float(Precision=64), nullable=True)
    owner  = Column(String(64), nullable=True)
    po_box = Column(Integer, nullable=True)
    postcode = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    rating = Column(Float(Precision=64), nullable=True)
    region =  Column(String(64), nullable=True)  
    tel = Column(String(64), nullable=True)  
    website = Column(String(64), nullable=True)  
    timestamp = Column(Integer, nullable=True)
    #look at notes for list of strings to deal with

    #super magical function that lets you pass in whatever is inside dictionary 
    #from Factual and updates it as current instance in restaurant
    def set_from_factual(self, data):
        for key, value in data.iteritems():
            if key not in ['hours', 'hours_display']:
                setattr(self, key, value)


class Restaurant_Features(Base):
    __tablename__="restaurant_features"   
    #name and factual_id to join 
    id = Column (Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id')) #because each should be unique
    factual_id = Column(String(128), nullable=True) 
    #these are all booleans
    accessible_wheelchair= Column(Boolean, unique=False, default=False)
    alcohol_byob = Column(Boolean, unique=False, default=False)
    alcohol_bar = Column(Boolean, unique=False, default=False)
    alcohol_beer_wine = Column(Boolean, unique=False, default=False)
    alcohol = Column(Boolean, unique=False, default=False)
    groups_goodfor=  Column(Boolean, unique=False, default=False)
    kids_goodfor=  Column(Boolean, unique=False, default=False)
    kids_menu =  Column(Boolean, unique=False, default=False)
    meal_breakfast=  Column(Boolean, unique=False, default=False)
    meal_cater=  Column(Boolean, unique=False, default=False)
    meal_deliver=  Column(Boolean, unique=False, default=False)
    meal_dinner=  Column(Boolean, unique=False, default=False)
    meal_lunch =  Column(Boolean, unique=False, default=False)
    meal_takeout=  Column(Boolean, unique=False, default=False)
    open_24hrs=  Column(Boolean, unique=False, default=False)
    options_glutenfree  =  Column(Boolean, unique=False, default=False)
    options_lowfat  =  Column(Boolean, unique=False, default=False)
    options_organic =  Column(Boolean, unique=False, default=False)
    options_healthy=  Column(Boolean, unique=False, default=False)
    options_vegan=  Column(Boolean, unique=False, default=False)
    options_vegetarian=  Column(Boolean, unique=False, default=False)
    parking = Column(Boolean, unique=False, default=False)
    parking_free =  Column(Boolean, unique=False, default=False)
    parking_garage =  Column(Boolean, unique=False, default=False)
    parking_lot=  Column(Boolean, unique=False, default=False)
    parking_street=  Column(Boolean, unique=False, default=False)
    parking_valet=  Column(Boolean, unique=False, default=False)
    parking_validated =  Column(Boolean, unique=False, default=False)
    payment_cashonly=  Column(Boolean, unique=False, default=False)
    reservations =   Column(Boolean, unique=False, default=False)
    room_private=  Column(Boolean, unique=False, default=False)
    seating_outdoor=  Column(Boolean, unique=False, default=False)
    smoking=  Column(Boolean, unique=False, default=False)
    wifi= Column(Boolean, unique=False, default=False)
    reservations = Column(Boolean, unique=False, default=False)
    timestamp = Column(Integer, nullable=True)

  

    restaurant = relationship("Restaurant", backref=backref("restaurant_features", order_by=restaurant_id, uselist=False))

    #the point of this table is to start storing values to figure out how often a user wants these 

    def set_from_factual(self, data):
        for key, value in data.iteritems():
            setattr(self, key, value)

    def get_data(self):
        kwargs = {'organic_rating': self.options_organic,
                'health_rating': self.options_healthy,
                'access_rating':  self.accessible_wheelchair,
                'wifi_rating': self.wifi,
                'parking_rating': self.parking}

        return kwargs

    def get_all_data(self):
        
        kwargs = {'accessible_wheelchair': self.accessible_wheelchair,
        'alcohol_byob': self.alcohol_byob, 'alcohol_bar': self.alcohol_bar,
        'alcohol_beer_wine': self.alcohol_beer_wine, 'alcohol': self.alcohol,
        'groups_goodfor':  self.groups_goodfor, 'kids_goodfor': self.kids_goodfor,
        'kids_menu': self.kids_menu, 'meal_breakfast':  self.meal_breakfast,
        'meal_dinner':  self.meal_dinner, 'meal_deliver':  self.meal_deliver,
        'options_healthy': self.options_healthy, 
        'options_glutenfree': self.options_glutenfree, 
        'options_lowfat': self.options_lowfat, 
        'options_vegan': self.options_vegan, 
        'options_vegetarian': self.options_vegetarian, 
        'options_organic': self.options_organic, 'parking': self.parking, 
        'reservations':  self.reservations,
        'wifi' : self.wifi}

        return kwargs

class Restaurant_Category(Base):
    __tablename__="restaurant_categories"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    factual_id = Column(String(128), nullable=True) 
    cuisine = Column(String(3000), nullable=True, default=None)
    category_labels = Column(String(3000), default=None)
    category_ids = Column(String(3000), default=None)

    restaurant = relationship("Restaurant", backref=backref("restaurant_categories", order_by=restaurant_id, uselist=False))

    def set_from_factual(self, data):

        for key, value in data.iteritems():
            print "Here's what is inside %r" % key
            print "Here's the value %r" % value 

        for key, value in data.iteritems():
            if key == 'factual_id':
                setattr(self, key, value)

            elif key == 'cuisine':
                cuisine_as_string = ""
                for item in range(len(value)):
                    cuisine_as_string+=str(value[item])+" "
                setattr(self, key, cuisine_as_string)

            elif key == 'category_labels':
                cat_label_as_string =""
                for item in range(len(value)):
                    categories = value[item]
                    for entry in categories:
                        cat_label_as_string+=str(entry)+" "
                setattr(self, key, cat_label_as_string)

            elif key == 'category_ids':
                cat_id_as_string = ""
                for item in range(len(value)):
                    cat_id_as_string+=str(value[item])+" "
                setattr(self, key, cat_id_as_string)



    #the point of this table is to start storing values 
    # afghan = Column(Boolean, unique=False, default=False)
    # african = Column(Boolean, unique=False, default=False)
    # american = Column(Boolean, unique=False, default=False)
    # argentine = Column(Boolean, unique=False, default=False)
    # armenian = Column(Boolean, unique=False, default=False)
    # asian_fusion= Column(Boolean, unique=False, default=False)
    # bangladeshi= Column(Boolean, unique=False, default=False)
    # barbeque= Column(Boolean, unique=False, default=False)
    # bakery = Column(Boolean, unique=False, default=False)
    # belgian= Column(Boolean, unique=False, default=False)
    # bistro= Column(Boolean, unique=False, default=False)
    # brazilian= Column(Boolean, unique=False, default=False)
    # buffet = Column(Boolean, unique=False, default=False)
    # british= Column(Boolean, unique=False, default=False)
    # burgers= Column(Boolean, unique=False, default=False)
    # burmese= Column(Boolean, unique=False, default=False)
    # cafe= Column(Boolean, unique=False, default=False)
    # cajun = Column(Boolean, unique=False, default=False)
    # californian= Column(Boolean, unique=False, default=False)
    # cambodian= Column(Boolean, unique=False, default=False)
    # caribbean= Column(Boolean, unique=False, default=False)
    # calzones= Column(Boolean, unique=False, default=False)
    # cheesesteaks= Column(Boolean, unique=False, default=False)
    # chicken= Column(Boolean, unique=False, default=False)
    # chilean = Column(Boolean, unique=False, default=False)
    # chinese= Column(Boolean, unique=False, default=False)
    # coffee = Column(Boolean, unique=False, default=False)
    # contemporary = Column(Boolean, unique=False, default=False)
    # continental = Column(Boolean, unique=False, default=False)
    # crepes= Column(Boolean, unique=False, default=False)
    # cuban= Column(Boolean, unique=False, default=False)
    # czech= Column(Boolean, unique=False, default=False)
    # delis = Column(Boolean, unique=False, default=False)
    # diners= Column(Boolean, unique=False, default=False)
    # dim_sum = Column(Boolean, unique=False, default=False)
    # donuts = Column(Boolean, unique=False, default=False)
    # dutch = Column(Boolean, unique=False, default=False)
    # eastern_euro = Column(Boolean, unique=False, default=False)
    # eclectic = Column(Boolean, unique=False, default=False)
    # ethiopian= Column(Boolean, unique=False, default=False)
    # fast_food= Column(Boolean, unique=False, default=False)
    # filipino= Column(Boolean, unique=False, default=False)
    # fish_chips= Column(Boolean, unique=False, default=False)
    # fondue = Column(Boolean, unique=False, default=False)
    # food_court= Column(Boolean, unique=False, default=False)
    # food_stands= Column(Boolean, unique=False, default=False)
    # french= Column(Boolean, unique=False, default=False)
    # frozen_yogurt = Column(Boolean, unique=False, default=False)
    # fusion = Column(Boolean, unique=False, default=False)
    # gastropubs= Column(Boolean, unique=False, default=False)
    # german= Column(Boolean, unique=False, default=False)
    # gluten_free= Column(Boolean, unique=False, default=False)
    # grill = Column(Boolean, unique=False, default=False)
    # greek= Column(Boolean, unique=False, default=False)
    # halal= Column(Boolean, unique=False, default=False)
    # hawaiian= Column(Boolean, unique=False, default=False)
    # himalayan_nepa= Column(Boolean, unique=False, default=False)
    # hot_dogs= Column(Boolean, unique=False, default=False)
    # hungarian= Column(Boolean, unique=False, default=False)
    # indian= Column(Boolean, unique=False, default=False)
    # indonesian= Column(Boolean, unique=False, default=False)
    # irish= Column(Boolean, unique=False, default=False)
    # italian= Column(Boolean, unique=False, default=False)
    # japanese= Column(Boolean, unique=False, default=False)
    # jamaican = Column(Boolean, unique=False, default=False)
    # juices = Column(Boolean, unique=False, default=False)
    # korean= Column(Boolean, unique=False, default=False)
    # kosher= Column(Boolean, unique=False, default=False)
    # lat_am= Column(Boolean, unique=False, default=False)
    # malaysian= Column(Boolean, unique=False, default=False)
    # mediterranean= Column(Boolean, unique=False, default=False)
    # mexican= Column(Boolean, unique=False, default=False)
    # middle_eastern= Column(Boolean, unique=False, default=False)
    # mongolian= Column(Boolean, unique=False, default=False)
    # organic = Column(Boolean, unique=False, default=False)
    # oysters = Column(Boolean, unique=False, default=False)
    # pacific_rim = Column(Boolean, unique=False, default=False)
    # pakistani= Column(Boolean, unique=False, default=False)
    # pan_asian = Column(Boolean, unique=False, default=False)
    # persian= Column(Boolean, unique=False, default=False)
    # peruvian= Column(Boolean, unique=False, default=False)
    # pizza= Column(Boolean, unique=False, default=False)
    # polish= Column(Boolean, unique=False, default=False)
    # portuguese= Column(Boolean, unique=False, default=False)
    # pub = Column(Boolean, unique=False, default=False)
    # russian= Column(Boolean, unique=False, default=False)
    # salad= Column(Boolean, unique=False, default=False)
    # smoothies = Column(Boolean, unique=False, default=False)
    # sandwiches= Column(Boolean, unique=False, default=False)
    # scandinavian= Column(Boolean, unique=False, default=False)
    # scottish= Column(Boolean, unique=False, default=False)
    # seafood= Column(Boolean, unique=False, default=False)
    # singaporean= Column(Boolean, unique=False, default=False)
    # slovakian= Column(Boolean, unique=False, default=False)
    # soul_food= Column(Boolean, unique=False, default=False)
    # soup= Column(Boolean, unique=False, default=False)
    # southern= Column(Boolean, unique=False, default=False)
    # spanish= Column(Boolean, unique=False, default=False)
    # steakhouses= Column(Boolean, unique=False, default=False)
    # sushi_bars= Column(Boolean, unique=False, default=False)
    # taiwanese= Column(Boolean, unique=False, default=False)
    # tapas_bars= Column(Boolean, unique=False, default=False)
    # tapas_small= Column(Boolean, unique=False, default=False)
    # tea = Column(Boolean, unique=False, default=False)
    # texmex= Column(Boolean, unique=False, default=False)
    # thai= Column(Boolean, unique=False, default=False)
    # turkish= Column(Boolean, unique=False, default=False)
    # ukranian= Column(Boolean, unique=False, default=False)
    # vegan = Column(Boolean, unique=False, default=False)
    # vegetarian = Column(Boolean, unique=False, default=False)
    # vietnamese = Column(Boolean, unique=False, default=False)
    # wings = Column(Boolean, unique=False, default=False)
    # wraps = Column(Boolean, unique=False, default=False)

class Restaurant_Neighborhood(Base):
    __tablename__="restaurant_neighborhoods"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    neighborhood = Column(String(128), nullable=True)
    
    
class User_Preference(Base):
    __tablename__="user_preferences"

    id = Column (Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id')) #because each should be unique
    accessible_wheelchair= Column(String(64), nullable=True)
    alcohol_byob = Column(String(64), nullable=True)
    alcohol_bar = Column(String(64), nullable=True)
    alcohol_beer_wine = Column(String(64), nullable=True)
    alcohol= Column(String(64), nullable=True) 
    groups_goodfor= Column(String(64), nullable=True) 
    kids_goodfor= Column(String(64), nullable=True) 
    kids_menu = Column(String(64), nullable=True) 
    meal_breakfast= Column(String(64), nullable=True)    
    meal_cater= Column(String(64), nullable=True) 
    meal_deliver= Column(String(64), nullable=True) 
    meal_dinner= Column(String(64), nullable=True) 
    meal_lunch = Column(String(64), nullable=True)
    meal_takeout= Column(String(64), nullable=True)
    open_24hrs= Column(String(64), nullable=True)
    options_glutenfree  = Column(String(64), nullable=True)
    options_lowfat  = Column(String(64), nullable=True)
    options_organic = Column(String(64), nullable=True)
    options_healthy= Column(String(64), nullable=True) 
    options_vegan= Column(String(64), nullable=True) 
    options_vegetarian= Column(String(64), nullable=True)
    parking = Column(String(64), nullable=True)
    parking_free = Column(String(64), nullable=True)
    parking_garage = Column(String(64), nullable=True)
    parking_lot= Column(String(64), nullable=True) 
    parking_street= Column(String(64), nullable=True)
    parking_valet= Column(String(64), nullable=True) 
    parking_validated = Column(String(64), nullable=True) 
    payment_cashonly= Column(String(64), nullable=True)
    reservations =  Column(String(64), nullable=True)
    room_private= Column(String(64), nullable=True) 
    seating_outdoor= Column(String(64), nullable=True) 
    smoking= Column(String(64), nullable=True) 
    wifi= Column(String(64), nullable=True)
    reservations = Column(String(64), nullable=True)
    timestamp = Column(Integer, nullable=True)

    user = relationship("User", backref=backref("user_preferences", order_by=user_id))

class User_Restaurant_Rating(Base):
    __tablename__="user_restaurant_ratings"
    # this table will basically say users like the first three restaurants they type in
    #it will also store feedback on suggested restaurants for each user
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id')) 
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    rating = Column(Float(Precision=64), nullable=True)

    user = relationship("User", backref=backref("user_restaurant_ratings", order_by=user_id))
    restaurant = relationship("Restaurant", backref=backref("user_restaurant_ratings", order_by=restaurant_id))
    # user_preference = relationship("User_Preference", backref=backref("user_restaurant_ratings", order_by=user_id))

    

def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("sqlite:///paprika_spice.db", echo=True)
    Session = sessionmaker(bind=ENGINE)

    return Session()
 

def main():
    Base.metadata.create_all(ENGINE)

if __name__ == "__main__":
    session = connect() 
    main()

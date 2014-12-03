Parsley
=======
####Summary
Parsley is a personalized restaurant recommendation engine that solves the age-old question – where should I go to eat? It addresses a gap in today’s recommendation engines landscape, using cosine similarities as a quick, simple way to understand a user's preferences and make tailored recommendations.

Parsley searches more than 1.1 million US restaurants (with more than 40 restaurant-specific attributes for each) to surface relevant suggestions to users based on restaurants, bars and cafes that they already love – then allows users an easy way to store, access and visualize their favorite restaurants. 
####How it works






Users provide feedback on suggestions as Parsley learns their preferences, using sci-kit learn's cosine similarity algorithm to find restaurants with feature vectors that closely match a user’s preferences for a requested zipcode and cuisine.

####Details
- [Stack](#stack)
- [Features](#how-it-works)
- [Features](#features)
- [Screenshots](#screenshots) 
  - [Landing Page](#landing-page)
  - [Log in Page](#login-page)
  - [Restaurant search page](#search)
  - [Results](#results)
  - [Favorites](#favorites)
  - [Browse](#browse)
- [Acknowledgements](#acknowledgements)

####Stack
•	Python 2.7 <br>
•	Factual API <br>
•	Flask 0.9<br>
•	Flask-SQLAlchemy 0.16<br>
•	Google Maps JS embed API  <br>
•	Jinja2 2.6<br>
•	Mapbox JS API (Leaflet JS) <br>
•	OAuth<br>
•	Passlib <br>
•	Scikit-learn (requires numpy and scipy)<br>
•	Werkzeug 0.8.3<br>
•	Wsgiref 0.1.2<br>
•	WTForms 1.0.2<br>

####How it works
•	Parsley uses a cosine similarity algorithm to determine restaurants that closely align with a user’s preferences along more than 40 different restaurant feature parameters, leveraging Factual’s API to access more than 1.1 million restaurants in the US. 

####Features 
1.	Secure user log in functionality (pbkdf2_sha256 encryption) <br>
2.	Search and autocomplete functionality (Google Maps JS Autocomplete)<br>
3.	Matching/recommendation algorithm (using scikit-learn) <br>
4.	Filter by zip code and cuisine <br>
5.	Save and view user favorites (LeafletJS/Mapbox JS API)<br>
 
####Screenshots

###<strong>Landing page</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/splash.png)<br><br>
###<strong>Login page</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/login.png)<br><br>
Users sign up and log in using secure pbkdf2_sha256 encryption (assuming https connection). After signup, users complete a quick preferences survey that inserts a row into the user_preferences SQLite table, which has a one-to-one relationship with the user table.  
###<strong>Restaurant search</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/restaurants_page.png)<br><br>
Restaurant suggestions: A user can enter three restaurants that he or she likes, along with the zip code that they would like to search, and receive tailored recommendations, with the option to filter by either cuisine or category (bar, coffee shop, etc.).
<br>
<strong>Google autocomplete: </strong>
When a user starts to type in restaurants, Google Maps’ Javascript API autocompletes the text entry to ensure submission format is standardized to be restaurant, address, city, state, country.
If a user clicks submit with incorrectly formatted information, they’ll see an error page and be returned to the form to re-enter information.
<br>
<strong>Check DB – or ping Factual API: </strong>
Upon clicking “submit”, a call to the server is made to check whether these restaurants exist in the Parsley database yet. If not, Parsley makes an API call to Factual (after parsing the entry to determine name, city, etc.) to search for restaurants by that name in that city. If restaurants are found, Parsley then takes the JSON object from Factual and inserts appropriate information into the restaurant, restaurant_features and user_restaurant_rating table. 
<br>

###<strong>Results </strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/all_cuisines.png)<br>
<strong> Suggest new restaurants: </strong>
Given that information, Parsley now loops over all restaurants a user has ever rated positively, along with a user’s initial preferences, to create a comprehensive dictionary of weighted user preferences. 
1.	Parsley then identifies the top 3 features that are important to a user – and queries the restaurant table for restaurants that contain these features in the zip code that the user specified and creates a dictionary of all entries.
2.	Using scikit learning’s DictVectorizer, both the user preferences and restaurant results dictionary are converted to vectors.
3.	Using scikit learning’s cosine similarity algorithm, Parsley then ranks all restaurants with those top features in that zip code by which restaurants most closely match a user’s preferences. 
<br>
###<strong>Favorites</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/favorites.png)<br><br>
Parsley returns ranked restaurants to the user on a feedback page, which contains restaurant contact information and the ability to upvote/downvote restaurants.
<be>

###<strong>Browse</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/browse.png)<br><br>
An alternative path for the user to quickly view suggested restaurants using their default zipcode established at signup. Users can modify their initial set of preferences and demographic information at any time by clicking on the My Profile tab.
<br>

####Acknowledgements
Image credit:<br>
• Leaf by Evan MacDonald and emoticons (Happy, Sad)  by Paul F. from The Noun Project from <a href = "https://www.http://thenounproject.com/"> The Noun Project</a><br>
• Background images from <a href = "https://unsplash.com/grid"> Unsplash
 


 

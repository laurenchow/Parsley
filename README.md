Parsley
=======
####Summary
Parsley is a personalized restaurant recommendation engine that solves the age-old question – where should I go to eat? It addresses a gap in today’s recommendation engines landscape, using cosine similarities as a quick, simple way to understand a user's preferences and make tailored recommendations.

Parsley searches more than 1.1 million US restaurants (with more than 40 restaurant-specific attributes for each) to surface relevant suggestions to users based on restaurants, bars and cafes that they already love – then allows users an easy way to store, access and visualize their favorite restaurants. 

Users provide feedback on suggestions as Parsley learns their preferences, using sci-kit learn's cosine similarity algorithm to find restaurants with feature vectors that closely match a user’s preferences for a requested zipcode and cuisine.

####Details
- [Features](#features)
- [Screenshots](#screenshots) 
- [Stack](#stack)
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

####Features 
1.	Secure user log in functionality (pbkdf2_sha256 encryption) <br>
2.	Search and autocomplete functionality (Google Maps JS Autocomplete)<br>
3.	Matching/recommendation algorithm (using scikit-learn) <br>
4.	Filter by zip code and cuisine <br>
5.	Save and view user favorites (LeafletJS/Mapbox JS API)<br>
 
####Screenshots

<strong>Login</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/login.png)<br><br>
<strong>Restaurant search</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/restaurants_page.png)<br><br>
<strong>Restaurant results: filtered by zip</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/all_cuisines.png)<br>
<strong>Favorites</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/favorites.png)<br><br>
 

####Acknowledgements
Image credit:<br>
Leaf by Evan MacDonald and emoticons (Happy, Sad)  by Paul F. from The Noun Project from <a href = "https://www.http://thenounproject.com/"> The Noun Project</a><br>
Background images from <a href = "https://unsplash.com/grid"> Unsplash
 


 

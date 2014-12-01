parsley
=======

Parsley is a personalized restaurant recommendation engine that solves the age-old question – where should I go to eat? It addresses a gap in today’s recommendation engines landscape, using cosine similarities as a quick, simple way to understand a user's preferences and make tailored recommendations.

Parsley surfaces relevant suggestions to users based on restaurants, bars and cafes that they already love – and allows users an easy way to access and visualize their favorite restaurants. 

It does this by searching more than 1.1 million US restaurants (with more than 40 restaurant-specific attributes for each) to surface relevant suggestions to users based on restaurants, bars and cafes that they already love. 

Users provide feedback on suggestions as Parsley learns their preferences, using sci-kit learning to find restaurants that closely match a user’s preferences for a requested zipcode and cuisine.

<h2><strong>Features</strong><br></h2>
1.	Secure user log in functionality (pbkdf2_sha256 encryption) <br>
2.	Search and autocomplete functionality (Google Maps JS Autocomplete)<br>
3.	Matching/recommendation algorithm (cosine similarity)<br>
4.	Filter by zip code  <br>
5.	Save and view user favorites (LeafletJS/Mapbox API)<br>
 
<h2><strong> User Experience </strong><br></h2>

<strong>Login</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/login.png)<br><br>
<strong>Restaurant search</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/restaurants_page.png)<br><br>
<strong>Restaurant results: filtered by zip</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/all_cuisines.png)<br>
<strong>Favorites</strong><br><br>
![alt tag] (https://github.com/laurenchow/parsley/blob/master/screenshots/favorites.png)<br><br>

<h2><strong> Requirements (included in requirements.txt): </strong><br></h2>

•	Python 2.7 <br>
•	Flask 0.9<br>
•	Flask-SQLAlchemy 0.16<br>
•	Jinja2 2.6<br>
•	OAuth<br>
•	Passlib <br>
•	Scikit-learn (requires numpy and scipy)<br>
•	Werkzeug 0.8.3<br>
•	Wsgiref 0.1.2<br>
•	WTForms 1.0.2<br>

<strong>APIs (require access keys):</strong><br>
•	Factual <br>
•	Google Maps autocomplete <br>
•	Leaflet JS/Mapbox <br>
 


 

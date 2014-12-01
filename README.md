parsley
=======

Parsley is a personalized restaurant recommendation engine that solves the age-old question – where should I go to eat? – and addresses a gap in today’s recommendation engines landscape by providing an intuitive, simple way to understand user preferences.

Parsley surfaces relevant suggestions to users based on restaurants, bars and cafes that they already love – and allows users an easy way to access and visualize their favorite restaurants. 

It does this by searching more than 1.1 million US restaurants (with more than 40 restaurant-specific attributes for each) to surface relevant suggestions to users based on restaurants, bars and cafes that they already love. 

Users provide feedback on suggestions as Parsley learns their preferences, using cosine similarity to find restaurants that closely match a user’s preferences for a requested zipcode.

<strong>Features</strong><br>
1.	Secure user log in functionality (pbkdf2_sha256 encryption) <br>
2.	Search and autocomplete functionality (Google Maps JS Autocomplete)<br>
3.	Matching/recommendation algorithm (cosine similarity)<br>
4.	Filter by zip code  <br>
5.	Save and view user favorites (LeafletJS/Mapbox API)<br>
 

<strong> Requirements (included in requirements.txt): </strong><br>

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
 


 

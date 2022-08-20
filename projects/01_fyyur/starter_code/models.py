from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import collections
collections.Callable = collections.abc.Callable


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500) , nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String,nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False,nullable=False)
    seeking_description = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<Venue name={self.name}, city={self.city}, state={self.state}, address={self.address}, past_shows_count={self.past_shows_count}, upcoming_shows_count={self.upcoming_shows_count}>'

    def __init__(self, name, city, state, address, phone, facebook_link, genres, website, seeking_talent, seeking_description):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.facebook_link = facebook_link
        self.genres = genres
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f'<Artist name={self.name}, city={self.city}, state={self.state}, genres={self.genres}, past_shows_count={self.past_shows_count}, upcoming_shows_count={self.upcoming_shows_count}>'

    def __init__(self, name, genres, city, state, phone, facebook_link):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.facebook_link = facebook_link

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', backref='shows', lazy=True)
    artist = db.relationship('Artist', backref='shows', lazy=True)

    def __repr__(self):
        return f'<Show start_time={self.start_time}, venue={self.venue}, artist={self.artist}>'

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time
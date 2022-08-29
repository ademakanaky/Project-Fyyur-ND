from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, and_, UniqueConstraint, distinct
import dateutil.parser
from datetime import datetime

db = SQLAlchemy()

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
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String,nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False,nullable=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    UniqueConstraint('name', 'city', 'state', 'address', name='unique_name_city_state_address')

    def __init__(self, name, city, state, address, phone, image_link, facebook_link, genres, website, seeking_talent, seeking_description):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.facebook_link = facebook_link
        self.image_link = image_link
        self.genres = genres
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

    @property
    def past_shows(self):
        past_shows = list(
            filter(lambda show: show.start_time < datetime.now(), self.shows))
        return [
            {
                'venue_id': show.venue.id,
                'artist_id': show.artist.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } for show in past_shows]

    @property
    def upcoming_shows(self):
        upcoming_shows = list(
            filter(lambda show: show.start_time > datetime.now(), self.shows))
        return [
            {
                'venue_id': show.venue.id,
                'artist_id': show.artist.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } for show in upcoming_shows]

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)
    
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'past_shows': self.past_shows,
            'upcoming_shows': self.upcoming_shows,
            'past_shows_count': self.past_shows_count,
            'upcoming_shows_count': self.upcoming_shows_count
        }

    def __repr__(self):
        return f'<Artist name={self.name}, city={self.city}, state={self.state}, genres={self.genres}, past_shows_count={self.past_shows_count}, upcoming_shows_count={self.upcoming_shows_count}>'
    
    def __getitem__(self, key):
        return getattr(self, key)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f'<Artist name={self.name}, city={self.city}, state={self.state}, genres={self.genres}, past_shows_count={self.past_shows_count}, upcoming_shows_count={self.upcoming_shows_count}>'

    def __init__(self, name, genres, city, state, phone, facebook_link, image_link, website_link,seeking_venue,seeking_description):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.facebook_link = facebook_link
        self.image_link = image_link
        self.website = website_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description

    @property
    def past_shows(self):
        past_shows = list(
            filter(lambda show: show.start_time < datetime.now(), self.shows))
        return [
            {
                'venue_id': show.venue.id,
                'artist_id': show.artist.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } for show in past_shows]

    @property
    def upcoming_shows(self):
        upcoming_shows = list(
            filter(lambda show: show.start_time > datetime.now(), self.shows))
        return [
            {
                'venue_id': show.venue.id,
                'artist_id': show.artist.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } for show in upcoming_shows]

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', backref='shows', lazy=True)
    artist = db.relationship('Artist', backref='shows', lazy=True)

    def __repr__(self):
        return f'<Show start_time={self.start_time}, venue={self.venue}, artist={self.artist}>'

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time
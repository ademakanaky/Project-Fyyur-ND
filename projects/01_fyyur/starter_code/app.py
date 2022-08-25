#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort,jsonify, make_response
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import collections
collections.Callable = collections.abc.Callable
from sqlalchemy import exc, and_, UniqueConstraint, distinct
import itertools
from flask_wtf.csrf import CSRFProtect
from models import *
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
db.create_all(app=app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
csrf = CSRFProtect(app)
logger = logging.getLogger(__name__)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
      if format == 'full':
          format="EEEE MMMM, d, y 'at' h:mma"
      elif format == 'medium':
          format="EE MM, dd, y h:mma"
  else:
      date = value
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  distinct_city_state = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()  
  for city_state in distinct_city_state:
    city = city_state[0]
    state = city_state[1]
    venues = Venue.query.filter_by(city=city, state=state).all()   
    shows = venues[0].upcoming_shows
    data.append({
      "city": city,
      "state": state,
      "venues": venues
      })
  return render_template('pages/venues.html', areas=data, shows=shows);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '').strip()
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  
  result_set = []
  now = datetime.now()
  for venue in venues:
      venue_shows = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming = 0
      for show in venue_shows:
          if show.start_time > now:
              num_upcoming += 1

      result_set.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming
      })

  response = {
      "count": len(venues),
      "data": result_set
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()

  if venue is None:
    return abort(404)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form_data = VenueForm(request.form)
  # TODO: modify data to be the data object returned from db insertion
  if not form_data.validate():
        error_message = 'There are one or more errors in your submission. Please check your input and try again.'
  else:
      try:
          venue = form_data.name.data
          venue_exists = db.session.query(Venue.id).filter_by(name=venue).scalar() is not None

          if venue_exists:
              error_message = f'{venue} is already exist! Please change the name and try again.'
          else:
              newly_created_venue = Venue(
                  name=venue,
                  city=form_data.city.data,
                  state=form_data.state.data,
                  address=form_data.address.data,
                  phone=form_data.phone.data,
                  facebook_link=form_data.facebook_link.data,
                  image_link = form_data.image_link.data,
                  genres=', '.join(form_data.genres.data),
                  website = form_data.website.data,
                  seeking_talent = form_data.seeking_talent.data,
                  seeking_description = form_data.seeking_description.data
              )
              db.session.add(newly_created_venue)
              db.session.commit()
              # on successful db insert, flash success
              venue_id = newly_created_venue.id
              flash(
                  f'{venue} was successfully created!', 'success')
              
              return redirect(url_for('show_venue', venue_id=venue_id))

      except exc.SQLAlchemyError as error:
          logger.exception(error, exc_info=True)
          error_message = f'An error occurred. Venue {venue} could not be created.'
          db.session.rollback()
      finally:
          db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  if error_message is not None:
        flash(error_message, 'danger')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  return jsonify({'success': True})

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '').strip()
  matching_artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  
  result = []
  now = datetime.now()
  for artist in matching_artists:
      artist_shows = Show.query.filter_by(artist_id=artist.id).all()
      num_upcoming = 0
      for show in artist_shows:
          if show.start_time > now:
              num_upcoming += 1

      result.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming
      })

  response = {
      "count": len(matching_artists),
      "data": result
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.filter_by(id=artist_id).first()

  if data is None:
    return abort(404)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)  

  if artist is None:
        abort(404)

  form = ArtistForm(request.form)

  if form.validate():
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(artist)
    try:
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + artist.name + ' was successfully updated.')
      return redirect(url_for('show_artist', artist_id=artist_id))
    except exc.SQLAlchemyError as e:
      error = str(e.__dict__['orig'])
      flash('An error occurred. Artist could not be updated.' + error)
      db.session.rollback()
      flash('An error occurred. Artist ' + artist.name + ' could not be updated.')
      return render_template('pages/home.html')
    finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm(obj=venue)

  if venue is None:
    return abort(404)
    
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)  

  if venue is None:
        abort(404)

  form = VenueForm(request.form)

  if form.validate():
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(venue)
    try:
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully updated.')
      return redirect(url_for('show_venue', venue_id=venue_id))
    except exc.SQLAlchemyError as e:
      error = str(e.__dict__['orig'])
      flash('An error occurred. Venue could not be updated.' + error)
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
      return render_template('pages/home.html')
    finally:
      db.session.close()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form_data = ArtistForm(request.form)
  # TODO: modify data to be the data object returned from db insertion
  if not form_data.validate():
        error_message = 'There are one or more errors in your submission. Please check your input and try again.'
  else:
      try:
          artist = form_data.name.data
          artist_exists = db.session.query(Artist.id).filter_by(name=artist).scalar() is not None

          if artist_exists:
              error_message = f'{artist} already exist! Please change the name and try again.'
          else:
              newly_created_artist = Artist(
                  name=artist,
                  city=form_data.city.data,
                  state=form_data.state.data,
                  phone=form_data.phone.data,
                  facebook_link=form_data.facebook_link.data,
                  image_link = form_data.image_link.data,
                  genres=', '.join(form_data.genres.data),
                  website_link = form_data.website.data,
                  seeking_venue = form_data.seeking_venue.data,
                  seeking_description = form_data.seeking_description.data
              )
              db.session.add(newly_created_artist)
              db.session.commit()
              # on successful db insert, flash success
              artist_id = newly_created_artist.id
              flash(
                  f'{artist} was successfully created!', 'success')
              
              return redirect(url_for('show_artist', artist_id=artist_id))

      except exc.SQLAlchemyError as error:
          logger.exception(error, exc_info=True)
          error_message = f'An error occurred. Artist {artist} could not be created.'
          db.session.rollback()
      finally:
          db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  if error_message is not None:
        flash(error_message, 'danger')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

  # displays list of shows at /shows
  query = Show.query.join(
    Venue, (Venue.id == Show.venue_id)
  ).join(
      Artist, (Artist.id == Show.artist_id)
    ).with_entities(Show.venue_id, Venue.name.label('venue_name'), Show.artist_id, Artist.name.label('artist_name'), Artist.image_link, Show.start_time)
  
  data=[]
  for row in query:
    data.append({
      "venue_id": row.venue_id,
      "venue_name": row.venue_name,
      "artist_id": row.artist_id,
      "artist_name": row.artist_name,
      "artist_image_link": row.image_link,
      "start_time": row.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form_data = ShowForm(request.form)
  # TODO: modify data to be the data object returned from db insertion
  if not form_data.validate():
        error_message = 'There are one or more errors in your submission. Please check your input and try again.'
  else:
      try:
          artist_id = form_data.artist_id.data
          venue_id = form_data.venue_id.data
          show_start_time = form_data.start_time.data
          show_exists = db.session.query(Show.start_time).filter_by(start_time=show_start_time).scalar() is not None

          if show_exists:
              error_message = f'Show already exist! Please change the time and try again.'
          else:
              newly_created_show = Show(
                  start_time = form_data.start_time.data,
                  venue_id = form_data.venue_id.data,
                  artist_id = form_data.artist_id.data
              )
              db.session.add(newly_created_show)
              db.session.commit()
              # on successful db insert, flash success
              artist_id = newly_created_show.id
              flash(f'Show was successfully created!', 'success')
              return redirect(url_for('shows'))

      except exc.SQLAlchemyError as error:
          logger.exception(error, exc_info=True)
          error_message = f'An error occurred. Show could not be created.'
          db.session.rollback()
      finally:
          db.session.close()

      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  if error_message is not None:
        flash(error_message, 'danger')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

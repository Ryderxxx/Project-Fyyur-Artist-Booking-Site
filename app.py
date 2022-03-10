#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from unicodedata import name
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for, abort
from logging import Formatter, FileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from flask_wtf import FlaskForm
from flask_moment import Moment
from datetime import datetime
from models import *
from forms import *
import dateutil.parser
import logging
import babel
import sys
import os


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
# TODO: connect to a local postgresql database ✔
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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

def find_city(data, city_name):
  for i in range(len(data)):
    if data[i]['city'] == city_name:
      return i
  return -1

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. ✔
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.all()
  for i in range(len(venues)):
    shows_counter = 0
    current = datetime.now()
    for show in Show.query.filter_by(venue_id=venues[i].id):
      if show.start_time > current:
        shows_counter += 1
    venue_dict = {'id':venues[i].id, 'name':venues[i].name, 'num_upcoming_shows': shows_counter}
    city_index = find_city(data, venues[i].city)
    if city_index == -1:
      city_dict = {'city': venues[i].city, 'state': venues[i].state, 'venues': [venue_dict]}
      data.append(city_dict)
    else:
      venue_list = data[city_index]['venues']
      venue_list.append(venue_dict)
      data[city_index]['venues'] = venue_list
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. ✔
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  shows_counter = 0
  current = datetime.now()
  search_term = request.form.get('search_term', type=str)
  for element in Venue.query.filter(Venue.name.ilike('%'+search_term+'%')):
    for show in Show.query.filter_by(venue_id=element.id):
      if show.start_time > current:
        shows_counter += 1
    element = element.__dict__
    element['num_upcoming_shows'] = shows_counter
    data.append(element)
  response={"count": len(data), "data": data}
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id ✔
  '''
  venue1 = Venue(name='The Musical Hop', address='1015 Folsom Street', city='San Francisco', state='CA', phone='123-123-1234', website='https://www.themusicalhop.com', facebook_link='https://www.facebook.com/TheMusicalHop', seeking_talent=True, seeking_description='We are on the lookout for a local artist to play every two weeks. Please call us.', image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60')
  venue2 = Venue(name='The Dueling Pianos Bar', address='335 Delancey Street', city='New York', state='NY', phone='914-003-1132', website='https://www.theduelingpianos.com', facebook_link='https://www.facebook.com/theduelingpianos', seeking_talent=False, image_link='https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80')
  venue3 = Venue(name='Park Square Live Music & Coffee', address='34 Whiskey Moore Ave', city='San Francisco', state='CA', phone='415-000-1234', website='https://www.parksquarelivemusicandcoffee.com', facebook_link='https://www.facebook.com/ParkSquareLiveMusicAndCoffee', seeking_talent=False, image_link='https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80')
  '''
  try:
    venue = Venue.query.get(venue_id)
    data = venue.__dict__
    data['website'] = data['website_link']
    genres = []
    for genre in venue.genres:
      genres.append(genre.name)
    data['genres'] = genres
  except:
    print(sys.exc_info())
    return abort(404, description="Resource not found")
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead ✔
  # TODO: modify data to be the data object returned from db insertion ✔
  try:
    form = VenueForm()
    genres = []
    for genre_name in form.genres.data:
      genres.append(Genre.query.filter_by(name=genre_name).first())
    new_venue = Venue(name=form.name.data, 
                      city=form.city.data, 
                      state=form.state.data, 
                      address=form.address.data, 
                      phone=form.phone.data,
                      genres=genres,
                      image_link=form.image_link.data,
                      website_link=form.website_link.data,
                      facebook_link=form.facebook_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data)
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead. ✔
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using ✔
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred, Venue deleting failed.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database ✔
  data = Artist.query.order_by(Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. ✔
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  shows_counter = 0
  current = datetime.now()
  search_term = request.form.get('search_term', type=str)
  for element in Artist.query.filter(Artist.name.ilike('%'+search_term+'%')):
    for show in Show.query.filter_by(artist_id=element.id):
      if show.start_time > current:
        shows_counter += 1
    element = element.__dict__
    element['num_upcoming_shows'] = shows_counter
    data.append(element)
  response = {'count': len(data), 'data': data}
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id ✔
  '''
  artist1 = Artist(name='Guns N Petals', city='San Francisco', state='CA', phone='326-123-5000', website='https://www.gunsnpetalsband.com', facebook_link='https://www.facebook.com/GunsNPetals', seeking_venue=True, seeking_description='Looking for shows to perform at in the San Francisco Bay Area!', image_link='https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80')
  artist2 = Artist(name='Matt Quevedo', city='New York', state='NY', phone='300-400-5000', facebook_link='https://www.facebook.com/mattquevedo923251523', seeking_venue=False, image_link='https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80')
  artist3 = Artist(name='The Wild Sax Band', city='San Francisco', state='CA', phone='432-325-5432', seeking_venue=False, image_link='https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80')
  '''
  try:
    artist = Artist.query.get(artist_id)
    data = artist.__dict__
    data['website'] = data['website_link']
    genres = []
    for genre in artist.genres:
      genres.append(genre.name)
    data['genres'] = genres
  except:
    print(sys.exc_info())
    return abort(404, description="Resource not found")
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id> ✔
  artist = Artist.query.get(artist_id)
  if artist is None:
    return abort(404, description="Resource not found")
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing ✔
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  if artist is None:
    return abort(404, description="Resource not found")
  form = ArtistForm()
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))
  try:
    artist.name = form.name.data.strip()
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website_link = form.website_link.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.genres.clear()
    genre_names = form.genres.data
    for genre_name in genre_names:
      genre = Genre.query.filter_by(name=genre_name).one_or_none()
      if genre:
        artist.genres.append(genre)
    db.session.commit()
    flash('Success!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Failed.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id> ✔
  venue = Venue.query.get(venue_id)
  if venue is None:
    return abort(404, description="Resource not found")
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue.__dict__)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing ✔
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  if venue is None:
    return abort(404, description="Resource not found")
  form = VenueForm()
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))
  try:
    venue.name = form.name.data.strip()
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.state.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.genres.clear()
    genre_names = form.genres.data
    for genre_name in genre_names:
      genre = Genre.query.filter_by(name=genre_name).one_or_none()
      if genre:
        venue.genres.append(genre)
    db.session.commit()
    flash('Success!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Failed.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead ✔
  # TODO: modify data to be the data object returned from db insertion ✔
  try:
    form = ArtistForm()
    genres = []
    for genre_name in form.genres.data:
      genres.append(Genre.query.filter_by(name=genre_name).first())
    new_artist = Artist(name=form.name.data,
                        city=form.city.data,
                        state=form.state.data,
                        phone=form.phone.data,
                        genres=genres,
                        image_link=form.image_link.data,
                        website_link=form.website_link.data,
                        facebook_link=form.facebook_link.data,
                        seeking_talent=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data)
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
  # TODO: on unsuccessful db insert, flash an error instead. ✔
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist' + request.form['name'] + 'could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. ✔
  data = []
  for element in Show.query.all():
    element = element.__dict__
    element['venue_name'] = Venue.query.get(element['venue_id']).name
    element['artist_name'] = Artist.query.get(element['artist_id']).name
    element['artist_image_link'] = Artist.query.get(element['artist_id']).image_link
    element['start_time'] = element['start_time'].strftime('%Y-%m-%dT%H:%M:%S.000Z')
    data.append(element)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead ✔
  try:
    form = ShowForm()
    venue = Venue.query.get(form.venue_id.data)
    artist = Artist.query.get(form.artist_id.data)
    new_show = Show(venue_id=form.venue_id.data,
                    artist_id=form.artist_id.data,
                    start_time=form.start_time.data,
                    venue=venue, artist=artist)
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead. ✔
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

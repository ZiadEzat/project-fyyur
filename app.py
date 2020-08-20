#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    show = db.relationship('Show',backref='list')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    show = db.relationship('Show',backref='venue')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key = True)
    start_time = db.Column(db.String(120))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
    
  return babel.dates.format_datetime(date, format, locale = 'en')

app.jinja_env.filters['datetime'] = format_datetime

def fix_array(obj, attr):
    arr = getattr(obj, attr)
    if isinstance(arr, list) and len(arr) > 1:
        arr = arr[2:-2]
        arr = ''.join(arr).split(",")
        setattr(obj,attr, arr)
# 'Tue 05, 21, 2019 9:30PM'
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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  area = []
  state = []
  data = []
  for v in venues:
    if v.city in area:
      print('already exists')
    else:
      area.append(v.city)
      state.append(v.state)
  for i in range(len(area)):
    data.append({
      "city": area[i],
      "state": state[i],
      "venues": Venue.query.filter_by(city=area[i])
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike('%'+search+'%')).all()
  count = len(result)
  if (count >= 1 ):
    response={
      "count": count,
      "data": Venue.query.filter(Venue.name.ilike('%'+search+'%')).all()
    }
  else:
    response={
      "count": 0,
      "data": [{
        "name": "Venue not found"
      }]
    }
      
      
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = Venue.query.get(venue_id)
  upcoming_shows = []
  past_shows = []
  for show in data.show:
     if(datetime.fromisoformat(show.start_time) >= datetime.today()):
       upcoming_shows.append(show)
     else:
       past_shows.append(show)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  for show in data.upcoming_shows:
    show.artist_image_link = Artist.query.get(show.artist_id).image_link
  for show in data.past_shows:
    show.artist_image_link = Artist.query.get(show.artist_id).image_link
  data.upcoming_shows_count = len(data.upcoming_shows)
  data.past_shows_count = len(data.past_shows)
  return render_template('pages/show_venue.html',  venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    data = Venue( id = Venue.query.order_by(Venue.id.desc()).first().id + 1,
                  name=request.form['name'],
                  city=request.form['city'],
                  state=request.form['state'],
                  address=request.form['address'],
                  phone=request.form['phone'],
                  genres = request.form.getlist('genres'),
                  facebook_link=[request.form['facebook_link']])
    db.session.add(data)
    db.session.commit()
    flash('Venue ' + data.name + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()
  count = len(result)
  if (count >= 1 ):
    response={
      "count": count,
      "data": Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()
    }
  else:
    response={
      "count": 0,
      "data": [{
        "name": "Artist not found"
      }]
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  data = Artist.query.get(artist_id)
  fix_array(data,'genres')
  upcoming_shows = []
  past_shows = []
  if len(data.show) > 0:
    for show in data.show:
      if (datetime.fromisoformat(show.start_time) >= datetime.today()):
        upcoming_shows.append(show)
      else:
        past_shows.append(show)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  for show in data.upcoming_shows:
    show.venue_image_link = Venue.query.get(show.venue_id).image_link
  for show in data.past_shows:
    show.venue_image_link = Venue.query.get(show.venue_id).image_link
  data.upcoming_shows_count = len(upcoming_shows)
  data.past_shows_count = len(past_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data =  artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name'],
    artist.city = request.form['city'],
    artist.state = request.form['state'],
    artist.phone = request.form['phone'],
    artist.genres = request.form.getlist('genres'),
    artist.facebook_link = request.form['facebook_link']
    db.session.add(artist)
    db.session.commit()
  except:
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name'],
    venue.city = request.form['city'],
    venue.state = request.form['state'],
    venue.phone = request.form['phone'],
    venue.genres = request.form.getlist('genres'),
    venue.facebook_link = request.form['facebook_link']
    db.session.add(venue)
    db.session.commit()
  except:
    print(sys.exc_info())
    db.session.rollback()
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
  try:
    data = Artist(id =   Artist.query.order_by(Artist.id.desc()).first().id + 1,
                  name = request.form['name'],
                  city = request.form['city'],
                  state = request.form['state'],
                  phone = request.form['phone'],
                  genres = request.form.getlist('genres'),
                  facebook_link = request.form['facebook_link'],)
    db.session.add(data)
    db.session.commit()
    flash('Artist ' + data.name + ' was successfully listed!')
  except:
    db.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    data = Show( id = Show.query.order_by(Show.id.desc()).first().id + 1,
                start_time=request.form['start_time'],
                artist_id=request.form['artist_id'],
                venue_id=request.form['venue_id'])
    db.session.add(data)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()

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
    app.run(host='192.168.1.2', port=port)


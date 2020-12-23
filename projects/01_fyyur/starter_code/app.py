#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, make_response, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from constants import state_choices, genre_choices
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
# Validators.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  try:
      returnedDate = babel.dates.format_datetime(date, format, locale='en')
  except:
      returnedDate = str(date)
  return returnedDate

def format_phone(phone):
  phone=phone.replace('-','')
  if(len(phone)==10):
    phone = phone[:3] +'-' +phone[3:6]+'-'+phone[6:]
  return phone

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  # Adjusted the model to the account for new attributes
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  genres = db.Column(db.String, nullable=False)
  address = db.Column(db.String(120),nullable=False)
  city = db.Column(db.String(120),nullable=False)
  state = db.Column(db.String(120),nullable=False)
  phone = db.Column(db.String(120))
  website = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean(), nullable=False , default=True)
  seeking_description = db.Column(db.String())
  image_link = db.Column(db.String(500))
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
  shows = db.relationship('Show', backref='venue', lazy=True,cascade="all, delete")

  # Compares the show start time with now, to show upcoming and past shows. 
  def showsDictionary(self):
    upcoming_shows = []
    past_shows = []
    time_now = datetime.now()
    for show in self.shows:
      entry = {}
      entry['id'] = show.id
      entry['artist_id'] = show.artist.id
      entry['artist_name'] = show.artist.name
      entry['artist_image_link'] = show.artist.image_link
      entry['start_time'] = str(show.start_time)
      if (show.start_time > time_now):
        upcoming_shows.append(entry)
      else:
        past_shows.append(entry)
    shows_dict = {}
    shows_dict['upcoming_shows'] = upcoming_shows
    shows_dict['past_shows'] = past_shows
    return(shows_dict)

  def num_upcoming_shows(self):
    num_upcoming = 0 
    time_now = datetime.now()
    
    for show in self.shows:
      if (show.start_time > time_now):
        num_upcoming=num_upcoming+1
    return(num_upcoming)

  #converts venue object to data dictionary required for the view
  def adjust_data(self):
    data = {}
    data['id'] = self.id
    data['name'] = self.name
    data['genres'] = self.genres.split(',')
    data['address'] = self.address
    data['city'] = self.city
    data['state'] = self.state
    data['phone'] = self.phone
    data['website'] = self.website
    data['facebook_link'] = self.facebook_link
    data['seeking_talent'] = self.seeking_talent
    data['seeking_description'] = self.seeking_description
    data['image_link'] = self.image_link
    shows = self.showsDictionary()
    data['past_shows']  = shows['past_shows']
    data['upcoming_shows'] = shows['upcoming_shows']
    data['past_shows_count']  = len(shows['past_shows'])
    data['upcoming_shows_count'] = len(shows['upcoming_shows']) 
    return(data)

class Artist(db.Model):
  __tablename__ = 'artists'

  # Adjusted the model to the account for new attributes
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String,nullable=False)
  genres = db.Column(db.String(120),nullable=False)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  website = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  seeking_venues = db.Column(db.Boolean(), nullable=False , default=True)
  seeking_description = db.Column(db.String())
  image_link = db.Column(db.String(500))
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  shows = db.relationship('Show', backref='artist', lazy=True,cascade="all, delete")

  def num_upcoming_shows(self):
    num_upcoming = 0 
    time_now = datetime.now()
    
    for show in self.shows:
      if (show.start_time > time_now):
        num_upcoming=num_upcoming+1
    return(num_upcoming)

  #returns a dictionary of upcoming and past shows compared to datetime.now()
  def showsDictionary(self):
    upcoming_shows = []
    past_shows = []
    time_now = datetime.now()
    for show in self.shows:
      entry = {}
      entry['id'] = show.id
      entry['venue_id'] = show.venue.id
      entry['venue_name'] = show.venue.name
      entry['venue_image_link'] = show.venue.image_link
      entry['start_time'] = str(show.start_time)
      if (show.start_time > time_now):
        upcoming_shows.append(entry)
      else:
        past_shows.append(entry)
    shows_dict = {}
    shows_dict['upcoming_shows'] = upcoming_shows
    shows_dict['past_shows'] = past_shows
    return(shows_dict)
    
  def adjust_data(self):
    data = {}
    data['id'] = self.id
    data['name'] = self.name
    data['genres'] = self.genres.split(',')
    data['city'] = self.city
    data['state'] = self.state
    data['phone'] = self.phone
    data['website'] = self.website
    data['facebook_link'] = self.facebook_link
    data['seeking_venue'] = self.seeking_venues
    data['seeking_description'] = self.seeking_description
    data['image_link'] = self.image_link
    shows = self.showsDictionary()
    data['past_shows']  = shows['past_shows']
    data['upcoming_shows'] = shows['upcoming_shows']
    data['past_shows_count']  = len(shows['past_shows'])
    data['upcoming_shows_count'] = len(shows['upcoming_shows']) 
    return(data)

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime(), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  cities_dict = {}
  data = []
  venues_list = Venue.query.all()
  
  for venue in venues_list:
    city_state = venue.city+'$split$'+venue.state
    if city_state in cities_dict:
      cities_dict[city_state].append(venue)
    else:
      cities_dict[city_state] = [venue]

  for city in cities_dict:
    entry = {}
    city_state = city.split('$split$')
    entry['city'] = city_state[0]
    entry['state'] = city_state[1]
    entry['venues'] = []
    for venue in cities_dict[city]:
      venue_dict = {}
      venue_dict['id'] = venue.id
      venue_dict['name'] = venue.name
      venue_dict['num_upcoming_shows'] = venue.num_upcoming_shows()
      entry['venues'].append(venue)
    data.append(entry)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  response={}
  response['count'] = len(venues)
  for venue in venues:
    entry = {}
    entry['id'] = venue.id
    entry['name'] = venue.name
    entry['num_upcoming_shows'] = venue.num_upcoming_shows()
    data.append(entry)
  response['data'] =data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  try:
    venue = Venue.query.get(venue_id)
    print('venue from db is', venue)
    return render_template('pages/show_venue.html', venue=venue)
  except:
    return(render_template('errors/404.html'))

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  error = False
  try:
    name = form.name.data
    if(db.session.query(Venue.name).filter_by(name=name).scalar() is not None):
      flash('The venue : "'+ name+'" already exists', 'error')
      return render_template('forms/new_venue.html', form=form)
    form.validate()
    if(len(form.phone.errors)>0):
      flash(','.join(form.phone.errors))
      return render_template('forms/new_venue.html', form=form)
    venue = Venue()
    venue.name = name
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = format_phone(form.phone.data)
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    error = True
    print('Error in creating venue', e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Venue ' +request.form['name'] + ' Could not be listed.', 'error')
   
  else:
    flash('Venue ' + request.form['name'] +' was successfully listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/Delete', methods=['GET'])
def delete_venue(venue_id):
  error = False 
  print('Deleting venue')
  try:  
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Venue ' +str(venue_id) + ' Could not be listed.', 'error')
    return redirect(url_for('venues'))
  else:
    flash('Venue ' + str(venue_id) +' was successfully deleted.')
    return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists_list = Artist.query.all()
  data=[]
  for artist in artists_list:
    entry = {'id':artist.id ,'name':artist.name }
    data.append(entry)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  response={}
  response['count'] = len(artists)
  for artist in artists:
    entry = {}
    entry['id'] = artist.id
    entry['name'] = artist.name
    entry['num_upcoming_shows'] = artist.num_upcoming_shows()
    data.append(entry)
  response['data'] =data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  try:
    artist = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=artist)
  except:
    return(render_template('errors/404.html'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm()
  try:
    name = form.name.data
    if(db.session.query(Artist.name).filter_by(name=name).scalar() is not None):
      flash('The artist : "'+ name+'" already exists', 'error')
      return render_template('forms/new_artist.html', form=form)
    form.validate()
    if(len(form.phone.errors)>0):
      flash(','.join(form.phone.errors))
      return render_template('forms/new_artist.html', form=form)
    artist = Artist()
    artist.name = name
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = format_phone(form.phone.data)
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website.data
    artist.image_link = form.image_link.data
    artist.seeking_venues = form.seeking_venues.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. artist ' +request.form['name'] + ' Could not be listed.', 'error')
  else:
    flash('Artist ' + request.form['name'] +' was successfully listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data=[]
  shows = Show.query.order_by(db.desc(Show.start_time)).all()
  for show in shows:
    data.append(
      {
        "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
      }
    )

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  artists_ids = [(artist.id,artist.name+' (id:'+str(artist.id)+')') for artist in Artist.query.all()]
  venues_ids = [(venue.id,venue.name+' (id:'+str(venue.id)+')') for venue in Venue.query.all()]
  form = ShowForm()
  form.venue_id.choices = venues_ids
  form.artist_id.choices = artists_ids
  return render_template('forms/new_show.html', form=form , data={'artists_ids':artists_ids,'venues_ids':venues_ids})

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    show = Show()
    show.start_time = request.form['start_time']
    show.venue_id = request.form['venue_id']
    show.artist_id = request.form['artist_id']
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. show starting at ' +request.form['start_time'] + ' Could not be listed.', 'error')
  else:
    flash('Show starting at' + request.form['start_time'] + ' was successfully listed!')
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

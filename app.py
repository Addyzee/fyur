#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.command.config import config
from email.policy import default
import json
from sre_parse import State
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import babel
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import sys
from wtforms import Form,validators
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://andy:AndyK@localhost:5432/fyurr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)
migrate=Migrate(app,db)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://andy:AndyK@localhost:5432/fyurr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False


# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    website_link = db.Column(db.String(120),nullable=False)
    seeking_talent = db.Column(db.Boolean, default=True,nullable=False)
    seeking_description = db. Column(db.String())
    shows=db.relationship('Show',backref='venue')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    look_venue = db.Column(db.Boolean, default=True,nullable=False)
    description = db. Column(db.String())
    shows=db.relationship('Show',backref='artist')

# # #    TODO: implement any missing fields, as a database migration using Flask-Migrate

# # # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__='Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
  start_time = db.Column(db.DateTime,nullable=False)
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
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venue_places=db.session.query(Venue.city,Venue.state).distinct()
  data=[]
  for venue_place in venue_places:
    venues_data=[]
    for venue in Venue.query.filter_by(city=venue_place.city).filter_by(state=venue_place.state).all():
      venues_data.append({
        'id':venue.id,
        'name':venue.name,
        'num_upcoming_shows':0
      })
      data.append({
        'city':venue_place.city,
        'state':venue_place.state,
        'venues':venues_data
      })
    
  return render_template('pages/venues.html',areas=data)

  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  # using like,ilike==case insensitive
  venues=db.session.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  data=[]
  for venue in venues:
    data.append({
      "id": venue.id,
      "name":venue.name,
      "num_shows":0
    })
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    past_shows = list(filter(lambda x: x.start_time <
                             datetime.today(), venue.shows))
    upcoming_shows = list(filter(lambda x: x.start_time >=
                                 datetime.today(), venue.shows))

    past_shows = list(map(lambda x: x.show_artist(), past_shows))
    upcoming_shows = list(map(lambda x: x.show_artist(), upcoming_shows))

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf':False})

  if form.validate():
    try:
      venue = Venue(name  = form.name.data,city  = form.city.data,state = form.state.data,phone = form.phone.data,address = form.address.data,genres = form.genres.data,image_link = form.image_link.data,facebook_link = form.facebook_link.data,seeking_talent = form.seeking_talent.data,website_link  = form.website_link.data,seeking_description = form.seeking_description.data)
      db.session.add(venue)
      db.session.commit()
      flash(request.form['name'] +'successfully added!')
      return render_template('pages/venues.html')
    except:
      db.session.rollback()
      flash(request.form['name'] + ' could not be listed.')  
    finally:
      db.session.close()
  else:
      flash('Error from validate!!')
  return render_template('forms/new_venue.html', form=form)
    #  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data=[]
  # fill the list from Artist data
  for artist in artists:
    data.append({
      'id':artist.id,
      'name':artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  result = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  data = []
  for artist in result:
    data.append({
      "id" : artist.id,
      "name": artist.name,
      "num_upcoming_shows":0
    })
  response={
    "count": len(result),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = db.session.query(Show,Artist,Venue).join(Artist).join(Venue).filter(Show.id==Artist.id).filter(Show.venue_id==Venue.id).filter(Artist.id==artist_id).all()
  past_shows = []
  upcoming_shows = []
  for s in shows:
    past_shows.append({
      "venue_id" : s.Venue.id ,
      "venue_name":s.Venue.name , 
      "venue_image_link":"https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",   
      "start_time":s.Shows.start_time
    })
  data = {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.look_venue,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),        
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows)
    }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_id = request.args.get('artist_id')
  artist = Artist.query.get(artist_id)
  artist_info={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.genres = request.form['genres']
  artist.image_link = request.form['image_link']
  artist.website = request.form['website']
  try:
    db.session.commit()
    flash("Artist {} is updated successfully".format(artist.name))
  except:
    db.session.rollback()
    flash("Artist {} isn't updated successfully".format(artist.name))
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_id = request.args.get('venue_id')
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_info={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_info)
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.facebook_link = request.form['facebook_link']
  venue.genres = request.form['genres']
  venue.image_link = request.form['image_link']
  venue.website = request.form['website']
  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  new_artist = Artist()
  new_artist.name = request.form['name']
  new_artist.city = request.form['city']
  new_artist.state = request.form['state']
  new_artist.genres = request.form['genres']
  new_artist.phone = request.form['phone']
  new_artist.facebook_link = request.form['facebook_link']
  new_artist.image_link = request.form['image_link']
  try:
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
  finally:
    db.session.close()
  return redirect(url_for('index'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.order_by(Show.start_time.desc()).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data.extend([{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }])
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form =ShowForm(request.form, meta={'csrf':False})
  if form.validate():
    try:
        show = Show(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('Error! Show not listed!')
    finally:
          db.session.close()
  else:
    flash('Error from validate!!')
    return render_template('forms/new_show.html', form=form)
    
  return render_template('pages/shows.html')


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

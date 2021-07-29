#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import stat
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from sqlalchemy.orm import backref, query, session
from forms import *
from models import Venue,Venue_Types,Artist,Artist_Types,Show,db
from flask_script import Manager
from flask_migrate import Migrate


import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app,db)
manger = Manager(app = app)
manger.add_command('db')
#db.create_all(app = app) 

if __name__ == "__main__":
    migrate.run()


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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=Venue.query.all()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_text= request.form.get('search_term')
  SearchedVenues =  Venue.query.filter(Venue.name.like('%'+search_text+'%')).all()
  data = []
  for x in SearchedVenues:
    data.append({"id" : x.id,"name":x.name}) 
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  GetVenuesById = Venue.query.filter_by(id = venue_id).one_or_none()
 
  past_shows = db.session.query(Show).join(Venue).filter(Show.VenueId==venue_id).filter(Show.startTime < datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.VenueId==venue_id).filter(Show.startTime>datetime.now()).all()
  data = []
  pastShowsCount =len(past_shows)
  UpcomingShowsCount = len(upcoming_shows) 
  data.append(
    {
    "id": GetVenuesById.id,
    "name": GetVenuesById.name,
    "genres": GetVenuesById.VenueGenres,
    "address": GetVenuesById.address,
    "city": GetVenuesById.city,
    "state": GetVenuesById.state,
    "phone": GetVenuesById.phone,
    "website": GetVenuesById.website_link,
    "facebook_link": GetVenuesById.facebook_link,
    "seeking_talent": GetVenuesById.seeking_talent,
    "image_link": GetVenuesById.image_link,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": pastShowsCount,
    "upcoming_shows_count": UpcomingShowsCount
    }
  )
  data = list(filter(lambda d: d['id'] == venue_id,data))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
  
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      image_link = request.form.get('image_link')
      website_link = request.form.get('website_link')
      if request.form.get('seeking_talent') == 'y' :
        seeking_talent = True
      else:
        seeking_talent = False
      seeking_description = request.form.get('seeking_description')
      newVenue = Venue(name = name,city = city ,state = state , address = address,phone = phone , facebook_link = facebook_link,image_link = image_link,website_link = website_link
      ,seeking_talent = seeking_talent , seeking_description = seeking_description)
      for x in genres:
        newVenue.VenueGenres.append(Venue_Types(Genres = x))
      db.session.add(newVenue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    flash('An error occurred. Venue ' + newVenue.name + ' could not be listed.')
  finally:
    db.session.close()  

  return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    GetVenueById =  Venue.query.filter_by(id = venue_id).one_or_none()
    db.session.remove(GetVenueById)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  All_artists = Artist.query.all()
  data=[]
  for x in All_artists:
    data.append({"id":x.id,"name" : x.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  GetArtist = Artist.query.filter(Artist.name.like("%{}%".format(search_term))).all()
  data = []
  for x in GetArtist:
    data.append({"id":x.id,"name":x.name,"num_upcoming_shows":0})
  response={
    "count": len(GetArtist),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  GetArtistById = Artist.query.filter_by(id = artist_id).one_or_none()
  past_shows = db.session.query(Show).join(Venue).filter(Show.ArtistId==artist_id).filter(Show.startTime < datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.ArtistId==artist_id).filter(Show.startTime>datetime.now()).all()
  data = []
  pastShowsCount =len(past_shows)
  UpcomingShowsCount = len(upcoming_shows)
  data.append(
    {
    "id": GetArtistById.id,
    "name": GetArtistById.name,
    "genres": GetArtistById.ArtistGenres,
    "city": GetArtistById.city,
    "state": GetArtistById.state,
    "phone": GetArtistById.phone,
    "website": GetArtistById.website_link,
    "facebook_link": GetArtistById.facebook_link,
    "seeking_venue": GetArtistById.seeking_venue,
    "image_link": GetArtistById.image_link,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": pastShowsCount,
    "upcoming_shows_count": UpcomingShowsCount
    }
  )
  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  genres = []
  GetArtistById= Artist.query.filter_by(id = artist_id).one_or_none()
  for x in GetArtistById.ArtistGenres:
     genres.append(x.Genres)
  artist = {
      "id": GetArtistById.id,
      "name": GetArtistById.name,
      "genres": genres,
      "city": GetArtistById.city,
      "state": GetArtistById.state,
      "phone": GetArtistById.phone,
      "website": GetArtistById.website_link,
      "facebook_link": GetArtistById.facebook_link,
      "seeking_venue": GetArtistById.seeking_venue,
      "seeking_description": GetArtistById.seeking_description,
      "image_link": GetArtistById.image_link
          }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist= Artist.query.filter_by(id = artist_id).one_or_none()
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    if request.form.get('seeking_venue') == 'y' :
      seeking_venue = True
    else:
      seeking_venue = False
    seeking_description = request.form.get('seeking_description')
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.facebook_link = facebook_link
    artist.image_link = image_link
    artist.website_link = website_link
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    if len(artist.ArtistGenres) > 0 :
      artist.ArtistGenres.clear()
    for x in genres:
      artist.ArtistGenres.append(Artist_Types(Genres = x))
      
        
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()  

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  try:
    GetVenueWithId = Venue.query.filter_by(id = venue_id).one_or_none()
    genres=[]
    for x in GetVenueWithId.VenueGenres:
      genres.append(x.Genres)
    Myvenue ={
      "id": GetVenueWithId.id,
      "name": GetVenueWithId.name,
      "genres": genres,
      "address": GetVenueWithId.address,
      "city": GetVenueWithId.city,
      "state": GetVenueWithId.state,
      "phone": GetVenueWithId.phone,
      "website": GetVenueWithId.website_link,
      "facebook_link": GetVenueWithId.facebook_link,
      "seeking_talent": GetVenueWithId.seeking_talent,
      "seeking_description": GetVenueWithId.seeking_description,
      "image_link": GetVenueWithId.image_link
        }
  except:
    print(sys.exc_info)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=Myvenue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    GetVeuneWithId = Venue.query.filter_by(id = venue_id).one_or_none()
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    if request.form.get('seeking_talent') == 'y' :
      seeking_talent = True
    else:
      seeking_talent = False
    seeking_description = request.form.get('seeking_description')
    GetVeuneWithId.name = name
    GetVeuneWithId.city = city
    GetVeuneWithId.state= state
    GetVeuneWithId.address = address
    GetVeuneWithId.phone = phone
    GetVeuneWithId.facebook_link = facebook_link
    GetVeuneWithId.image_link = image_link
    GetVeuneWithId.website_link= website_link
    GetVeuneWithId.seeking_talent = seeking_talent
    GetVeuneWithId.seeking_description =seeking_description
    if len(GetVeuneWithId.VenueGenres) > 0:
      GetVeuneWithId.VenueGenres.clear()
    for x in genres:
      GetVeuneWithId.VenueGenres.append(Venue_Types(Genres = x))
    db.session.commit()
  except: 
    db.session.rollback()
    print(sys.exc_info)
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
  
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      image_link = request.form.get('image_link')
      website_link = request.form.get('website_link')
      if request.form.get('seeking_venue') == 'y' :
        seeking_venue = True
      else:
        seeking_venue = False
      seeking_description = request.form.get('seeking_description')
      newArtist = Artist(name = name,city = city ,state = state ,phone = phone , facebook_link = facebook_link,image_link = image_link,website_link = website_link,seeking_venue = seeking_venue , seeking_description = seeking_description)
      for x in genres:
        newArtist.ArtistGenres.append(Artist_Types(Genres = x))
      db.session.add(newArtist)
      db.session.commit()
      flash('Artist' + request.form['name'] + ' was successfully listed!')
      
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()  

  return render_template('pages/home.html')
 


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []
  GetAllArtists = Artist.query.all()
  for artist in GetAllArtists:
    for venue in artist.Venues:
      data.append(
        { 
          "venue_id": venue.VenueId,
          "venue_name":venue.venue.name,
          "artist_id":artist.id,
          "artist_name":artist.name,
          "artist_image_link":artist.image_link,
          "start_time":venue.startTime
          
           }
      )

    

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
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    artist = Artist.query.filter_by(id = artist_id).one_or_none()
    venue = Venue.query.filter_by(id = venue_id).one_or_none()
    SetShow = Show(ArtistId = artist_id,VenueId = venue_id,startTime = start_time)
    SetShow.venue = venue
    
    artist.Venues.append(SetShow)
    # 
    # db.session.add(SetShow)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Error in list Show')
  finally:
    db.session.close()

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

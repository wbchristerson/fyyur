#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# TODO: connect to a local postgresql database - DONE

migrate = Migrate(app, db)

DEFAULT_ARTIST_IMAGE = "https://artcentereast.org/wp-content/uploads/2017/07/8415275-Artist-s-palette-with-paintbrushes-isolated-over-white-background-With-clipping-path-Stock-Photo.jpg"
DEFAULT_VENUE_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/e/e8/Vienna_-_Vienna_Opera_main_auditorium_-_9825.jpg"

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500), default="")
    children = db.relationship('VenueGenre', backref="venue", lazy=True,
                               collection_class=list, cascade="all, delete, delete-orphan")
    venue_shows = db.relationship("Show", backref="show_venue", cascade="all, delete, delete-orphan")

    def __repr__ (self):
      return f'<Venue %r>' % self.name


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500))
    children = db.relationship('ArtistGenre', backref="artist", lazy=True,
                               collection_class=list,
                               cascade="all, delete, delete-orphan"
                              )
    artist_shows = db.relationship("Show", backref="show_artist", cascade="all, delete, delete-orphan")


class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))


# Is there a way to make these two genre classes extend a single Genre class without SQL-
# Alchemy creating a database for that prototypical Genre class when calling 'flask db
# migrate'?

class VenueGenre(db.Model):
  __tablename__ = 'venueGenre'
  name = db.Column(db.String(20), primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False, primary_key=True)

  def __repr__(self):
    return f'<VenueGenre {self.name} {self.venue_id}>'


class ArtistGenre(db.Model):
  __tablename__ = 'artistGenre'
  name = db.Column(db.String(20), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False, primary_key=True)

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
  all_venues = Venue.query.order_by("city").all()
  data = []
  for venue in all_venues:
    num_upcoming_shows = Show.query.filter(Show.venue_id==venue.id, Show.start_time > datetime.now()).count()
    if len(data) == 0 or data[-1]["city"] != venue.city:
      data.append({ "city": venue.city, "state": venue.state, "venues": [] })
    data[-1]["venues"].append({ "id": venue.id, "name": venue.name,
                             "num_upcoming_shows": num_upcoming_shows})
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  #  seach for Hop should return "The Musical Hop".
  #  search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #
  venue_matches = Venue.query.filter(Venue.name.ilike(f'%{request.form.get("search_term", "")}%')).all()

  search_responses = [{"id": v.id, "name": v.name} for v in venue_matches]
  search_counts = []
  for s in search_responses:
    search_counts.append(Show.query.filter(Show.venue_id == s["id"], Show.start_time > datetime.now()).count())

  response = {
    "count": len(venue_matches),
    "data": [{"id": vm["id"], "name": vm["name"], "num_upcoming_shows": sc} for (vm, sc) in zip(search_responses, search_counts)]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


def get_venue_show_data(show_record):
  displayed_artist_image_link = show_record.show_artist.image_link
  if displayed_artist_image_link is None:
    displayed_artist_image_link = DEFAULT_ARTIST_IMAGE
  return {
    "artist_id": show_record.artist_id,
    "artist_name": show_record.show_artist.name,
    "artist_image_link": displayed_artist_image_link,
    "start_time": str(show_record.start_time)
  }


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  error_code = None
  data = {}

  try:
    venue = Venue.query.get(venue_id)
    genres = VenueGenre.query.filter(VenueGenre.venue_id==venue.id).all()
    past_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time < datetime.now()).all()
    upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time >= datetime.now()).all()

    data["id"] = venue_id
    data["name"] = venue.name
    data["genres"] = [g.name for g in genres]
    data["address"] = venue.address
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone
    data["website"] = venue.website
    data["facebook_link"] = venue.facebook_link
    data["seeking_talent"] = venue.seeking_talent

    data["seeking_description"], = venue.seeking_description,
    if data["seeking_description"] is None:
      data["seeking_description"] = ""

    data["image_link"], = venue.image_link,
    if data["image_link"] is None:
      data["image_link"] = DEFAULT_VENUE_IMAGE

    data["past_shows"] = [get_venue_show_data(show_record) for show_record in past_shows]
    data["upcoming_shows"] = [get_venue_show_data(show_record) for show_record in upcoming_shows]
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)
  except AttributeError:
    db.session.rollback()
    error_code = 404
    print(sys.exc_info())
    flash('An error occurred. Are you sure that the venue has all attributes?')
  except:
    db.session.rollback()
    error_code = 500
    print(sys.exc_info())
    flash('An error occurred. The venue could not be displayed.')
  finally:
    db.session.close()

  if error_code:
    abort(error_code)
  else:
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error_code = None

  try:
    venue = Venue(
      name=request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      facebook_link = request.form.get('facebook_link')
    )

    genre_list = request.form.getlist('genres')
    db.session.add(venue)
    db.session.commit()

    for genre in genre_list:
      db.session.add(VenueGenre(venue_id=venue.id, name=genre))
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error_code=404
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()

  if error_code:
    abort(error_code)
  return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error_code = None

  try:
    venue_match = Venue.query.filter(Venue.id==venue_id).first()
    db.session.delete(venue_match)
    db.session.commit()
    flash('The venue with id ' + venue_id + ' was successfully deleted.')
  except AttributeError:
    db.session.rollback()
    error_code = 404
    print(sys.exc_info())
    flash('An error occurred. Are you sure that the venue has all attributes?')
  except:
    db.session.rollback()
    error_code = 500
    print(sys.exc_info())
    flash('An error occurred. The venue could not be displayed.')
  finally:
    db.session.close()

  if error_code:
    abort(error_code)
  return jsonify({ 'success': True })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  all_artists = Artist.query.order_by(Artist.name).all()
  data = []
  for artist in all_artists:
    data.append({ "id": artist.id, "name": artist.name })
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  artist_matches = Artist.query.filter(Artist.name.ilike(f'%{request.form.get("search_term", "")}%')).all()
  search_responses = [{"id": a.id, "name": a.name} for a in artist_matches]
  search_counts = []
  for s in search_responses:
    search_counts.append(Show.query.filter(Show.artist_id == s["id"], Show.start_time > datetime.now()).count())
  response = {
    "count": len(artist_matches),
    "data": [{"id": am["id"], "name": am["name"], "num_upcoming_shows": sc} for (am, sc) in zip(search_responses, search_counts)]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


def get_artist_show_data(show_record):
  displayed_venue_image_link = show_record.show_artist.image_link
  if displayed_venue_image_link is None:
    displayed_venue_image_link = DEFAULT_VENUE_IMAGE
  return {
    "venue_id": show_record.venue_id,
    "venue_name": show_record.show_venue.name,
    "venue_image_link": displayed_venue_image_link,
    "start_time": str(show_record.start_time),
  }


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  error_code = None
  data = {}

  try:
    artist = Artist.query.get(artist_id)

    if artist is None:
      error_code = 404
    else:
      genres = ArtistGenre.query.filter(ArtistGenre.artist_id==artist.id).all()
      past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
      upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time >= datetime.now()).all()

      data["id"] = artist_id
      data["name"] = artist.name
      data["genres"] = [g.name for g in genres]
      data["city"] = artist.city
      data["state"] = artist.state
      data["phone"] = artist.phone
      data["website"] = artist.website
      data["facebook_link"] = artist.facebook_link
      data["seeking_venue"] = artist.seeking_venue

      data["seeking_description"], = artist.seeking_description,
      if data["seeking_description"] is None:
        data["seeking_description"] = ""

      data["image_link"], = artist.image_link,
      if data["image_link"] is None:
        data["image_link"] = DEFAULT_ARTIST_IMAGE

      data["past_shows"] = [get_artist_show_data(show_record) for show_record in past_shows]
      data["upcoming_shows"] = [get_artist_show_data(show_record) for show_record in upcoming_shows]
      data["past_shows_count"] = len(past_shows)
      data["upcoming_shows_count"] = len(upcoming_shows)
  except AttributeError:
    db.session.rollback()
    error_code = 404
    print(sys.exc_info())
    flash('An error occurred. Are you sure that the artist exists and has all attributes?')
  except:
    db.session.rollback()
    error_code = 500
    print(sys.exc_info())
    flash('An error occurred. The artist could not be displayed.')
  finally:
    db.session.close()

  if error_code:
    abort(error_code)
  else:
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  error_code = None
  edited_artist = {}

  try:
    artist = Artist.query.get(artist_id)

    if artist is None:
      error_code = 404
    else:
      edited_artist["id"] = artist.id
      edited_artist["name"] = artist.name

      genres = ArtistGenre.query.filter(ArtistGenre.artist_id==artist.id).all()
      edited_artist["genres"] = [g.name for g in genres]

      edited_artist["city"] = artist.city
      edited_artist["state"] = artist.state
      edited_artist["phone"] = artist.phone
      edited_artist["website"] = artist.website
      edited_artist["facebook_link"] = artist.facebook_link
      edited_artist["seeking_venue"] = artist.seeking_venue
      edited_artist["seeking_description"] = artist.seeking_description
      edited_artist["image_link"] = artist.image_link
  except AttributeError:
    db.session.rollback()
    error_code = 404
    print(sys.exc_info())
    flash('An error occurred. Are you sure that the artist exists and has all attributes?')
  except:
    db.session.rollback()
    error_code = 500
    print(sys.exc_info())
    flash('An error occurred. The artist could not be displayed.')
  finally:
    db.session.close()

  if error_code:
    abort(error_code)
  else:
    return render_template('forms/edit_artist.html', form=form, artist=edited_artist)


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
  # called upon submitting the new artist listing form
  error_code = None

  try:
    artist = Artist(
      name=request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      facebook_link = request.form.get('facebook_link')
    )

    genre_list = request.form.getlist('genres')
    db.session.add(artist)
    db.session.commit()

    for genre in genre_list:
      db.session.add(ArtistGenre(artist_id=artist.id, name=genre))
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error_code=404
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()

  if error_code:
    abort(error_code)
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  all_shows = Show.query.all()

  data = []

  for show in all_shows:
    data.append({
      "venue_id": show.venue_id,
      # "venue_name": show.venue.name,
      "venue_name": "The VNNUYE",
      "artist_id": show.artist_id,
      # "artist_name": show.artist.name,
      "artist_name": "HINGERH HIN ER HINGER GINGER DINGER GINGR HINGER",

      # "artist_image_link": show.artist.image_link,
      "artist_image_link": "https://i.ytimg.com/vi/1yBwWLunlOM/maxresdefault.jpg",
      
      "start_time": str(show.start_time)
    })

  # data = [{
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
  error_code = None

  try:
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    show = Show(
      venue_id=venue_id,
      artist_id=artist_id,
      start_time=request.form.get('start_time')
    )
    # venue = Venue.query.get(venue_id)
    # artist = Artist.query.get(artist_id)

    # show.show_artist = artist
    # venue.artists.append(show)

    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed!')
  except AttributeError:
    db.session.rollback()
    error_code = 404
    print(sys.exc_info())
    flash('An error occurred. Are you sure that the venue and artist IDs used exist?')
  except:
    db.session.rollback()
    error_code = 500
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  if error_code:
    abort(error_code)

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))


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

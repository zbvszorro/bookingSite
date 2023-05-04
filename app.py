#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import logging
import traceback
from logging import Formatter, FileHandler
import sys
import babel
import dateutil.parser
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for,
  abort,
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Import Model
#----------------------------------------------------------------------------#
from model import *

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

###################################################################
# Controllers.
###################################################################
@app.route('/')
def index():
  return render_template('pages/home.html')

###################################################################
#  Venues
#  ----------------------------------------------------------------
###################################################################
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venue_list_by_city_state = Venue.query.distinct(Venue.city, Venue.state).all()
  data = [venue.demo_venue_by_city_state() for venue in venue_list_by_city_state]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term_input = request.form.get('search_term', '')
  venue_list = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term_input))).all()
  response = {
    "count": len(venue_list),
    "data": [venue.demo_info_with_upcoming_show_number() for venue in venue_list] if len(venue_list) > 0 else []
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()
  data = venue.demo_individual()

  return render_template('pages/show_venue.html', venue=data)

# =================================================================
# >>> Create Venue
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
      new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )

      new_venue.add()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as ex:
      db.session.rollback()
      print(ex)
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

    return render_template('pages/home.html')

  else:
    message = []
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    # create_venue_form()
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  venue_info = venue.demo_info()
  form = VenueForm(data=venue_info)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  # if form.validate():
  try:
    venue = Venue.query.filter(Venue.id == venue_id).one()
    venue.name = form.name.data,
    venue.city = form.city.data,
    venue.state = form.state.data,
    venue.address = form.address.data,
    venue.phone = form.phone.data,
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data,
    venue.website = form.website_link.data,
    venue.image_link = form.image_link.data,
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except Exception as ex:
    db.session.rollback()
    print(ex)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))
  # else:
  #   message = []
  #   for field, errors in form.errors.items():
  #       for error in errors:
  #           message.append(f"{field}: {error}")
  #   flash('Please fix the following errors: ' + ', '.join(message))
  #   venue = Venue.query.get(venue_id)
  #   venue_info = venue.demo_info()
  #   form = VenueForm(data=venue_info)
  #
  #   return render_template('forms/edit_venue.html', form=form, venue=venue)

### My way
# @app.route('/venues/<int:venue_id>', methods=['DELETE'])
# def delete_venue(venue_id):
#   # TODO: Complete this endpoint for taking a venue_id, and using
#   # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
#
#   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
#   # clicking that button delete it from the db then redirect the user to the homepage
#
#   try:
#     venue = Venue.query.filter(Venue.id == venue_id).one()
#     db.session.delete(venue)
#     db.session.commit()
#     flash("Venue {0} has been deleted successfully".format(venue['name']))
#   except Exception as ex:
#     db.session.rollback()
#     abort(404)
#     print(ex)
#     flash(f'An error occurred. Venue {venue_id} could not be deleted.')
#   finally:
#     db.session.close()
#
#   return redirect(url_for('venues'))


### TA's way
@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  """
  If a session error occurs, for example:
  SQLAlchemy Object already attached to session
  Use the commented code (current_session).
  """
  try:
    venue = Venue.query.get_or_404(venue_id)
    current_session = db.object_session(venue)
    current_session.delete(venue)
    current_session.commit()
    # db.session.delete(venue)
    # db.session.commit()
    flash('The venue has been removed together with all of its shows.')
    return render_template('pages/home.html')
  except ValueError:
    db.session.rollback()
    flash('It was not possible to delete this Venue')
  finally:
    db.session.close()

  return redirect(url_for('venues'))


###################################################################
#  Artists
#  ----------------------------------------------------------------
###################################################################
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_list = Artist.query.all()
  data = [artist.demo_info() for artist in artist_list]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term_input = request.form.get('search_term', '')
  artist_list = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term_input))).all()
  response = {
    "count": len(artist_list),
    "data": [artist.demo_individual() for artist in artist_list] if len(artist_list) > 0 else []
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """
  data1={
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
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  """
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter(Artist.id == artist_id).first()
  data = artist.demo_individual()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist_info = artist.demo_info()
  form = ArtistForm(data=artist_info)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  try:
    artist = Artist.query.filter_by(id=artist_id).one()
    artist.name = form.name.data,
    artist.city = form.city.data,
    artist.state = form.state.data,
    artist.phone = form.phone.data,
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data,
    artist.image_link = form.image_link.data,
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except Exception as ex:
    db.session.rollback()
    print(ex)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

# =================================================================
# >>> Create Artists

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)
  if form.validate():
    try:
      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )

      new_artist.add()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as ex:
      db.session.rollback()
      print(ex)
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))

    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

#  delete
#  ----------------------------------------------------------------
# @app.route('/artists/<int:artist_id>', methods=['DELETE'])
# def delete_artist(artist_id):
#   try:
#     artist = Artist.query.filter(Artist.id == artist_id).one()
#     db.session.delete(artist)
#     db.session.commit()
#     flash("Venue {0} has been deleted successfully".format(artist['name']))
#   except Exception as ex:
#     db.session.rollback()
#     abort(404)
#     print(ex)
#     flash(f'An error occurred. Venue {artist_id} could not be deleted.')
#   finally:
#     db.session.close()
#
#   return artists()


@app.route('/artists/<int:artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
  """
  If a session error occurs, for example:
  SQLAlchemy Object already attached to session
  Use the commented code (current_session).
  """
  try:
    artist = Artist.query.get_or_404(artist_id)
    # current_session = db.object_session(venue)
    # current_session.delete(venue)
    # current_session.commit()
    db.session.delete(artist)
    db.session.commit()
    flash('The artist has been removed together with all of its shows.')
    return render_template('pages/home.html')
  except ValueError:
    db.session.rollback()
    flash('It was not possible to delete this Artist')
  finally:
    db.session.close()

  return redirect(url_for('artists'))

###################################################################
#  Shows
#  ----------------------------------------------------------------
###################################################################
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  """
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  """
  show_list = Show.query.all()
  data = [show.demo_info_with_venue_artist() for show in show_list]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  if form.validate():
    try:
      show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data
      )
      show.add()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except Exception as ex:
      db.session.rollback()
      print(ex)
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()

    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

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

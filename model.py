# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from app import db
from datetime import datetime

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    # id
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

    def demo_info(self):
        data = {'id': self.id,
                'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
                'venue_id': self.venue_id,
                'artist_id': self.artist_id
                }

        return data

    """
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    """
    def demo_info_with_venue_artist(self):
        data = self.demo_info()
        venue = Venue.query.filter(Venue.id == data['venue_id']).first()
        artist = Artist.query.filter(Artist.id == data['artist_id']).first()
        data['venue_id'] = venue.id
        data['venue_name'] = venue.name
        data['artist_id'] = artist.id
        data['artist_name'] = artist.name
        data['artist_image_link'] = artist.image_link

        return data
    # functions
    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Show {}{}>'.format(self.artist_id, self.venue_id)

class Venue(db.Model):  # parent
    __tablename__ = 'Venue'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # parent-child relationship
    # shows = db.relationship('Show', backref="venue", lazy=True)
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")

    # expressive format
    # 1. basic info:
    # @property
    def demo_info(self):
        data = {'id': self.id,
                'name': self.name,
                'genres': self.genres,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'website': self.website,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description
                }

        return data

    # 2. venue grouped by city + state
    def demo_venue_by_city_state(self):
        venues = [venue.demo_info_with_upcoming_show_number() for venue in Venue.query.filter(Venue.city == self.city, Venue.state == self.state).all()]
        data = {'city': self.city,
                'state': self.state,
                'venues': venues}

        return data

    # 3. show count:
    # @app.route('/venues')
    def demo_info_with_upcoming_show_number(self):
        upcoming_show_number = Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == self.id)
        data = self.demo_info()
        data['upcoming_show_number'] = upcoming_show_number

        return data

    # 4. search show nothing; not needed

    # 5. show_venues: @app.route('/venues/<int:venue_id>'); individual venue page
    """ Format:
      "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
    """
    def getUpcomingAndPastShows(self):
        upcoming_shows, past_shows = [], []
        # don't use Show.query.filter by venue_id, instead use join
        # shows = Show.query.filter(Show.venue_id == self.id).all()
        # for show in shows:

        # get all shows and john with show.venues
        shows = db.session.query(Show).join(Venue).\
                                        join(Artist).\
                                        filter(Venue.id == self.id).all()
        for show in shows:
            # show_data = show.demo_info_with_venue_artist()
            show_data = show.demo_info()
            venue = show.venue
            artist = show.artist
            # show_data['venue_image_link'] = self.image_link
            show_data['venue_image_link'] = venue.image_link
            show_data['venue_id'] = venue.id
            show_data['venue_name'] = venue.name
            show_data['artist_id'] = artist.id
            show_data['artist_name'] = artist.name
            show_data['artist_image_link'] = artist.image_link
            if show.start_time > datetime.now():
                upcoming_shows.append(show_data)
            else:
                past_shows.append(show_data)

        return upcoming_shows, past_shows

    def demo_individual(self):
        # improvement: get all shows and then split by time
        data = self.demo_info()
        data['upcoming_shows'], data['past_shows'] = self.getUpcomingAndPastShows()
        data['upcoming_shows_count'] = len(data['upcoming_shows'])
        data['past_shows_count'] = len(data['past_shows'])

        return data

    # improve with decoration
    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.query(Venue).filter(Venue.id == self.id).update(self)
        db.session.commit()

    def __repr__(self):
        return '<Venue %r>' % self

class Artist(db.Model):  # child
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # parent-child relationship
    # shows = db.relationship('Show', backref="artist", lazy=True)
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")

    # expressive format
    # 1. basic info:
    # @property
    def demo_info(self):
        data = {'id': self.id,
                'name': self.name,
                # 'genres': self.genres.split(','),
                'genres': self.genres,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'website': self.website,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description
                }

        return data

    # 2. show_artist: @app.route('/venues/<int:venue_id>'); individual artist page
    # !!!! need to change "show.demo_info_with_venue_artist" !!!!
    """
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,    
    """
    def getUpcomingAndPastShows(self):
        upcoming_shows, past_shows = [], []
        shows = db.session.query(Show).join(Venue).\
                                        join(Artist).\
                                        filter(Artist.id == self.id).all()

        for show in shows:
            show_data = show.demo_info()
            venue = show.venue
            artist = show.artist
            show_data['venue_image_link'] = venue.image_link
            show_data['venue_id'] = venue.id
            show_data['venue_name'] = venue.name
            show_data['artist_id'] = artist.id
            show_data['artist_name'] = artist.name
            show_data['artist_image_link'] = artist.image_link
            if show.start_time > datetime.now():
                upcoming_shows.append(show_data)
            else:
                past_shows.append(show_data)

        return upcoming_shows, past_shows

    def demo_individual(self):
        # improvment: get all shows and then split by time
        data = self.demo_info()
        data['upcoming_shows'], data['past_shows'] = self.getUpcomingAndPastShows()

        # calculate show counts
        data['upcoming_shows_count'] = len(data['upcoming_shows'])
        data['past_shows_count'] = len(data['past_shows'])

        return data

    # improve with decoration
    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Artist {}>'.format(self.name)


#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask import Flask


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

venue_genres = db.Table('venue_genres',
                        db.Column('venue_id', db.Integer, db.ForeignKey(
                            'venues.id'), primary_key=True),
                        db.Column('genre_id', db.Integer, db.ForeignKey(
                            'genres.id'), primary_key=True)
                        )


artist_genres = db.Table('artist_genres',
                         db.Column('artist_id', db.Integer, db.ForeignKey(
                             'artists.id'), primary_key=True),
                         db.Column('genres_id', db.Integer, db.ForeignKey(
                             'genres.id'), primary_key=True)
                         )


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)


class Show(db.Model):
    __tablename__ = 'shows'
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)
    venue = db.relationship("Venue", back_populates="artists")
    artist = db.relationship("Artist", back_populates="venues")


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate ✔
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    genres = db.relationship(
        'Genre', secondary=venue_genres, backref=db.backref('venues'), lazy=True)
    artists = db.relationship("Show", back_populates="venue")


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate ✔
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    genres = db.relationship(
        'Genre', secondary=artist_genres, backref=db.backref('artists'), lazy=True)
    venues = db.relationship("Show", back_populates="artist")
#from flask_sqlalchemy import SQLAlchemy

from flask_sqlalchemy import SQLAlchemy
#from app import app


db = SQLAlchemy()


class Show(db.Model):
    __tablename__ = 'Show'
    #Id = db.Column(db.Integer,primary_key=True)
    ArtistId = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    VenueId = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    startTime = db.Column(db.DateTime())
    venue = db.relationship("Venue", back_populates="Artists")
    artist = db.relationship("Artist", back_populates="Venues")

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    ArtistGenres = db.relationship('Artist_Types',backref = 'ArtistGenres',lazy = True)
    Venues = db.relationship('Show',back_populates="artist")
    def __repr__(self) :
     return f'<Artist {self.id}{self.name}{self.city}{self.state}{self.phone}{self.image_link}{self.facebook_link}{self.website_link}{self.seeking_venue}{self.seeking_description}'

class Artist_Types(db.Model):
   __tablename__ = 'Artist_Types'
   id = db.Column(db.Integer, primary_key=True)
   Genres = db.Column(db.String(120))
   Artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)
   def __repr__(self) :
        return f'<Artist_Types {self.id}{self.Genres}{self.Artist_id}'

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    VenueGenres = db.relationship('Venue_Types',backref = 'VenueGenres',lazy = True)
    Artists = db.relationship('Show',back_populates="venue")
    
    def __repr__(self) :
        return f'<Venue {self.id}{self.name}{self.city}{self.state}{self.address}{self.phone}{self.image_link}{self.facebook_link}'

class Venue_Types(db.Model):
   __tablename__ = 'Venue_Types'
   id = db.Column(db.Integer, primary_key=True)
   Genres = db.Column(db.String(120))
   Venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
   def __repr__(self) :
        return f'<Venue_Types {self.id}{self.Genres}{self.Venue_id}'



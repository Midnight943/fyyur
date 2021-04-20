#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import logging
from datetime import datetime
from logging import Formatter, FileHandler
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from forms import *
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
db.init_app(app)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    areas = db.session.query(Venue.city, Venue.state).distinct(
        Venue.city, Venue.state).order_by('state').all()
    data = []
    for area in areas:
        venues = Venue.query.filter_by(state=area.state).filter_by(
            city=area.city).order_by('name').all()
        venue_data = []
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': venue_data
        })
        for venue in venues:
            venue_data.append({
                'id': venue.id,
                'name': venue.name
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(
        Venue.name.ilike('%' + search_term + '%')).all()
    data = []
    response = {
        'count': len(venues),
        'data': data
    }
    for venue in venues:
        data.append({
            'id': venue.id,
            'name': venue.name,
        })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    upcoming_shows = Show.query.filter(
        Show.start_time > datetime.now(), Show.venue_id == venue_id)
    past_shows = Show.query.filter(
        Show.start_time < datetime.now(), Show.venue_id == venue_id)
    upcoming_show_data = []
    past_show_data = []
    for show in upcoming_shows:
        upcoming_show_data.append({
            'artist_id': show.artist_id,
            'artist_name': show.Artist.name,
            'artist_image_link': show.Artist.image_link,
            'start_time': str(show.start_time)
        })

    for show in past_shows:
        past_show_data.append({
            'artist_id': show.artist_id,
            'artist_name': show.Artist.name,
            'artist_image_link': show.Artist.image_link,
            'start_time': str(show.start_time)
        })

    data = {
        'name': venue.name,
        'id': venue.id,
        'genres': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'address': venue.address,
        'facebook_link': venue.facebook_link,
        'website': venue.website,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'upcoming_shows': upcoming_show_data,
        'past_shows': past_show_data,
        'past_shows_count': past_shows.count(),
        'upcoming_shows_count': upcoming_shows.count()
    }
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
        form = VenueForm(request.form)
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, genres=form.genres.data, facebook_link=form.facebook_link.data,
                      image_link=form.image_link.data, website=form.website_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>/delete', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' +
              venue.name + ' was successfully deleted.')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = db.session.query(Artist).all()
    data = []
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(
        Artist.name.ilike("%" + search_term + "%")).all()
    data = []
    response = {
        'count': len(artists),
        'data': data
    }
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name,
        })
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    upcoming_shows = Show.query.filter(
        Show.start_time > datetime.now(), Show.artist_id == artist_id)
    past_shows = Show.query.filter(
        Show.start_time < datetime.now(), Show.artist_id == artist_id)
    upcoming_show_data = []
    past_show_data = []
    for show in upcoming_shows:
        upcoming_show_data.append({
            'venue_id': show.venue_id,
            'venue_name': show.Venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.Artist.name,
            'venue_image_link': show.Venue.image_link,
            'start_time': str(show.start_time)
        })

    for show in past_shows:
        past_show_data.append({
            'venue_id': show.venue_id,
            'venue_name': show.Venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.Artist.name,
            'venue_image_link': show.Venue.image_link,
            'start_time': str(show.start_time)
        })

    data = {
        'name': artist.name,
        'id': artist.id,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'facebook_link': artist.facebook_link,
        'website': artist.website,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'upcoming_shows': upcoming_show_data,
        'past_shows': past_show_data,
        'past_shows_count': past_shows.count(),
        'upcoming_shows_count': upcoming_shows.count()

    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(request.form)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form)
    venue.name = form.name.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm(request.form)
        artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, genres=form.genres.data, facebook_link=form.facebook_link.data,
                        image_link=form.image_link.data, website=form.website_link.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.Venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.Artist.name,
            'artist_image_link': show.Artist.image_link,
            'start_time': str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        form = ShowForm(request.form)
        show = Show(artist_id=form.artist_id.data,
                    venue_id=form.venue_id.data, start_time=form.start_time.data)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

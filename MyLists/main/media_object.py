import secrets
import pykakasi
from MyLists import app
from flask import url_for
from datetime import datetime
from flask_login import current_user
from MyLists.API_data import ApiData
from MyLists.models import ListType, Status


def latin_alphabet(original_name):
    try:
        original_name.encode('iso-8859-1')
        return True
    except UnicodeEncodeError:
        try:
            kks = pykakasi.kakasi()
            kks.setMode("H", "a")
            kks.setMode("K", "a")
            kks.setMode("J", "a")
            kks.setMode("s", True)
            try:
                conv = kks.getConverter().do(original_name).split('.')
            except:
                conv = kks.getConverter().do(original_name).split()
            cap_parts = [p.capitalize() for p in conv]
            cap_message = " ".join(cap_parts)
            return cap_message
        except:
            return False


def change_air_format(date, media_sheet=False):
    if media_sheet:
        try:
            return datetime.strptime(date, '%Y-%m-%d').strftime("%b %Y")
        except:
            return 'Unknown'
    else:
        try:
            return datetime.strptime(date, '%Y-%m-%d').strftime("%d %b %Y")
        except:
            return 'Unknown'


# Parsing the DB data to the <MediaSheet> route
class MediaDict:
    def __init__(self, media_data, list_type):
        self.data = media_data
        self.list_type = list_type
        self.media_info = {}

    def create_list_dict(self):
        self.media_dict()
        return self.media_info

    def media_dict(self):
        self.media_info = {"id": self.data.id,
                           "homepage": self.data.homepage,
                           "vote_average": self.data.vote_average,
                           "vote_count": self.data.vote_count,
                           "synopsis": self.data.synopsis,
                           "popularity": self.data.popularity,
                           "lock_status": self.data.lock_status,
                           "actors": ', '.join([r.name for r in self.data.actors]),
                           "genres": ', '.join([r.genre for r in self.data.genres]),
                           "in_user_list": False,
                           "score": "---",
                           "favorite": False,
                           "rewatched": 0,
                           "comment": None}

        return_latin = latin_alphabet(self.data.original_name)
        if return_latin is True:
            self.media_info["display_name"] = self.data.original_name
            self.media_info["other_name"] = self.data.name
        elif return_latin is False:
            self.media_info["display_name"] = self.data.name
            self.media_info["other_name"] = self.data.original_name
        else:
            self.media_info["display_name"] = self.data.name
            self.media_info["other_name"] = return_latin

        if self.data.original_name == self.data.name:
            self.media_info["other_name"] = None

        self.add_genres()
        self.add_follow_list()

        if self.list_type != ListType.MOVIES:
            self.add_tv_dict()
        else:
            self.add_movies_dict()

    def add_tv_dict(self):
        self.media_info["created_by"] = self.data.created_by
        self.media_info["total_seasons"] = self.data.total_seasons
        self.media_info["total_episodes"] = self.data.total_episodes
        self.media_info["prod_status"] = self.data.status
        self.media_info["episode_duration"] = self.data.episode_duration
        self.media_info["in_production"] = self.data.in_production
        self.media_info["origin_country"] = self.data.origin_country
        self.media_info["eps_per_season"] = [r.episodes for r in self.data.eps_per_season]
        self.media_info["networks"] = ', '.join([r.network for r in self.data.networks])
        self.media_info["first_air_date"] = self.data.first_air_date
        self.media_info["last_air_date"] = self.data.last_air_date
        self.media_info["status"] = Status.WATCHING.value
        self.media_info["last_episode_watched"] = 1
        self.media_info["current_season"] = 1

        # Change <first_air_time> format
        self.media_info['first_air_date'] = change_air_format(self.data.first_air_date, media_sheet=True)

        # Change <last_air_time> format
        self.media_info['last_air_date'] = change_air_format(self.data.last_air_date, media_sheet=True)

        # Time to complete
        self.media_info['time_to_complete'] = (self.data.total_episodes * self.data.episode_duration)

        if self.list_type == ListType.SERIES:
            self.media_info["media_type"] = 'Series'
            self.media_info["cover"] = 'series_covers/{}'.format(self.data.image_cover)
            self.media_info["cover_path"] = 'series_covers'
        elif self.list_type == ListType.ANIME:
            self.media_info['name'] = self.data.original_name
            self.media_info['original_name'] = self.data.name
            self.media_info["media_type"] = 'Anime'
            self.media_info["cover"] = 'anime_covers/{}'.format(self.data.image_cover)
            self.media_info["cover_path"] = 'anime_covers'

        in_user_list = self.add_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["last_episode_watched"] = in_user_list.last_episode_watched
            self.media_info["current_season"] = in_user_list.current_season
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["rewatched"] = in_user_list.rewatched
            self.media_info["comment"] = in_user_list.comment

    def add_movies_dict(self):
        self.media_info["media_type"] = "Movies"
        self.media_info["cover_path"] = 'movies_covers'
        self.media_info["cover"] = 'movies_covers/{}'.format(self.data.image_cover)
        self.media_info["original_language"] = self.data.original_language
        self.media_info["director"] = self.data.director_name
        self.media_info["runtime"] = self.data.runtime
        self.media_info["budget"] = self.data.budget
        self.media_info["revenue"] = self.data.revenue
        self.media_info["tagline"] = self.data.tagline
        self.media_info["tmdb_id"] = self.data.themoviedb_id
        self.media_info['release_date'] = 'Unknown'
        self.media_info["status"] = Status.COMPLETED.value

        # Change <release_date> format
        self.media_info['release_date'] = change_air_format(self.data.release_date)

        in_user_list = self.add_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["rewatched"] = in_user_list.rewatched
            self.media_info["comment"] = in_user_list.comment

    def add_genres(self):
        genres_list = [r.genre for r in self.data.genres]
        genre_str = ','.join([g for g in genres_list])
        if len(genres_list) > 2:
            genres_list = genres_list[:2]
            genre_str = ','.join([g for g in genres_list[:2]])

        self.media_info['same_genres'] = self.data.get_same_genres(genres_list, genre_str)

    def add_follow_list(self):
        self.media_info['in_follows_lists'] = self.data.in_follows_lists(current_user.id)

    def add_user_list(self):
        return self.data.in_user_list(current_user.id)


# Parsing the DB data to the <MediaList> route
class MediaListDict:
    def __init__(self, media_data, common_media, list_type):
        self.data = media_data
        self.list_type = list_type
        self.common_media = common_media
        self.media_info = {}

        if self.list_type == ListType.SERIES:
            self.cover_path = url_for('static', filename='covers/series_covers/')
        elif self.list_type == ListType.ANIME:
            self.cover_path = url_for('static', filename='covers/anime_covers/')
        elif self.list_type == ListType.MOVIES:
            self.cover_path = url_for('static', filename='covers/movies_covers/')

    def redirect_medialist(self):
        self.create_medialist_dict()
        return self.media_info

    def create_medialist_dict(self):
        self.media_info = {"id": self.data[0].id,
                           "tmdb_id": self.data[0].themoviedb_id,
                           "cover": "{}{}".format(self.cover_path, self.data[0].image_cover),
                           "score": self.data[1].score,
                           "favorite": self.data[1].favorite,
                           "rewatched": self.data[1].rewatched,
                           "comment": self.data[1].comment,
                           "category": self.data[1].status.value,
                           "common": False,
                           "media": "Movies"}

        if not self.media_info['score'] or self.media_info['score'] == -1:
            self.media_info['score'] = '---'

        return_latin = latin_alphabet(self.data[0].original_name)
        if return_latin is True:
            self.media_info["display_name"] = self.data[0].original_name
            self.media_info["other_name"] = self.data[0].name
        elif return_latin is False:
            self.media_info["display_name"] = self.data[0].name
            self.media_info["other_name"] = self.data[0].original_name
        else:
            self.media_info["display_name"] = self.data[0].name
            self.media_info["other_name"] = return_latin

        if self.data[0].id in self.common_media:
            self.media_info['common'] = True

        if self.list_type != ListType.MOVIES:
            self.add_tv_dict()

    def add_tv_dict(self):
        self.media_info['media'] = 'Series'
        if self.list_type == ListType.ANIME:
            self.media_info['media'] = 'Anime'

        self.media_info['last_episode_watched'] = self.data[1].last_episode_watched
        self.media_info['eps_per_season'] = [eps.episodes for eps in self.data[0].eps_per_season]
        self.media_info['current_season'] = self.data[1].current_season
        try:
            self.media_info['eps_per_season'][self.media_info['current_season'] - 1]
        except:
            self.media_info['current_season'] = 1
            self.media_info['last_episode_watched'] = 1


# Parsing the <API_data> to dict
class MediaDetails:
    def __init__(self, media_data, list_type, updating=False):
        self.media_data = media_data
        self.list_type = list_type
        self.updating = updating
        self.media_details = {}
        self.all_data = {}

    def get_media_cover(self):
        media_cover_name = 'default.jpg'
        media_cover_path = self.media_data.get('poster_path') or None

        if media_cover_path:
            media_cover_name = '{}.jpg'.format(secrets.token_hex(8))
            try:
                ApiData().save_api_cover(media_cover_path, media_cover_name, self.list_type)
            except Exception as e:
                app.logger.error('[ERROR] - Trying to recover the poster: {}'.format(e))
                media_cover_name = 'default.jpg'

        return media_cover_name

    def get_next_eps_seas(self):
        next_episode_to_air = self.media_data.get("next_episode_to_air") or None
        self.media_details['next_episode_to_air'] = None
        self.media_details['season_to_air'] = None
        self.media_details['episode_to_air'] = None
        if next_episode_to_air:
            self.media_details['next_episode_to_air'] = next_episode_to_air['air_date']
            self.media_details['season_to_air'] = next_episode_to_air['season_number']
            self.media_details['episode_to_air'] = next_episode_to_air['episode_number']

    def get_episode_duration(self):
        episode_duration = self.media_data.get("episode_run_time") or None
        if episode_duration:
            self.media_details['episode_duration'] = episode_duration[0]
        else:
            if self.list_type == ListType.ANIME:
                self.media_details['episode_duration'] = 24
            elif self.list_type == ListType.SERIES:
                self.media_details['episode_duration'] = 45

    def get_origin_country(self):
        origin_country = self.media_data.get("origin_country") or None
        self.media_details['origin_country'] = 'Unknown'
        if origin_country:
            self.media_details['origin_country'] = origin_country[0]

    def get_created_by(self):
        created_by = self.media_data.get("created_by") or None
        self.media_details['created_by'] = 'Unknown'
        if created_by:
            self.media_details['created_by'] = ", ".join(creator['name'] for creator in created_by)

    def get_seasons(self):
        seasons = self.media_data.get('seasons') or None
        seasons_list = []
        if seasons:
            for i in range(0, len(seasons)):
                if seasons[i]['season_number'] <= 0:
                    continue
                season_dict = {'season': seasons[i]['season_number'],
                               'episodes': seasons[i]['episode_count']}
                seasons_list.append(season_dict)
        else:
            season_dict = {'season': 1,
                           'episodes': 1}
            seasons_list.append(season_dict)

        return seasons_list

    def get_genres(self):
        genres = self.media_data.get('genres') or None
        genres_list = []
        if genres:
            for i in range(0, len(genres)):
                genres_dict = {'genre': genres[i]['name'],
                               'genre_id': int(genres[i]['id'])}
                genres_list.append(genres_dict)
        else:
            genres_dict = {'genre': 'No genres found',
                           'genre_id': 0}
            genres_list.append(genres_dict)

        return genres_list

    def get_anime_genres(self):
        a_genres_list = []
        try:
            anime_search = ApiData().anime_search(self.media_data.get("name"))
            anime_genres = ApiData().get_anime_genres(anime_search["results"][0]["mal_id"])['genres']
        except Exception as e:
            app.logger.error('[ERROR] - Requesting the Jikan API: {}'.format(e), {'API': 'Jikan'})
            anime_genres = None

        if anime_genres:
            for i in range(0, len(anime_genres)):
                genres_dict = {'genre': anime_genres[i]['name'],
                               'genre_id': int(anime_genres[i]['mal_id'])}
                a_genres_list.append(genres_dict)

        return a_genres_list

    def get_actors(self):
        actors = self.media_data.get('credits', {'cast': None}).get('cast') or None
        actors_list = []
        if actors:
            for actor in actors[:5]:
                actors_dict = {'name': actor["name"]}
                actors_list.append(actors_dict)
        else:
            actors_dict = {'name': 'Unknown'}
            actors_list.append(actors_dict)

        return actors_list

    def get_networks(self):
        networks = self.media_data.get('networks') or None
        networks_list = []
        if networks:
            for network in networks[:4]:
                networks_dict = {'network': network["name"]}
                networks_list.append(networks_dict)
        else:
            networks_dict = {'network': 'Unknown'}
            networks_list.append(networks_dict)

        return networks_list

    def get_director_name(self):
        the_crew = self.media_data.get('credits', {'crew': None}).get('crew') or None
        self.media_details['director_name'] = 'Unknown'
        if the_crew:
            for element in the_crew:
                if element['job'] == 'Director':
                    self.media_details['director_name'] = element['name']
                    break

    def get_tv_details(self):
        self.media_details = {'name': self.media_data.get('name', 'Unknown') or 'Unknown',
                              'original_name': self.media_data.get('original_name', 'Unknown') or 'Unknown',
                              'first_air_date': self.media_data.get('first_air_date', 'Unknown') or 'Unknown',
                              'last_air_date': self.media_data.get('last_air_date', 'Unknown') or 'Unknown',
                              'homepage': self.media_data.get('homepage', 'Unknown') or 'Unknown',
                              'in_production': self.media_data.get('in_production', False) or False,
                              'total_seasons': self.media_data.get('number_of_seasons', 1) or 1,
                              'total_episodes': self.media_data.get('number_of_episodes', 1) or 1,
                              'status': self.media_data.get('status', 'Unknown') or 'Unknown',
                              'vote_average': self.media_data.get('vote_average', 0) or 0,
                              'vote_count': self.media_data.get('vote_count', 0) or 0,
                              'synopsis': self.media_data.get('overview', 'Not defined.') or 'Not defined.',
                              'popularity': self.media_data.get('popularity', 0) or 0,
                              'themoviedb_id': self.media_data.get('id'),
                              'image_cover': self.get_media_cover(),
                              'last_update': datetime.utcnow()}

        self.get_next_eps_seas()
        self.get_episode_duration()
        self.get_origin_country()
        self.get_created_by()
        seasons_list = self.get_seasons()

        a_genres_list = []
        genres_list = []
        actors_list = []
        networks_list = []
        if not self.updating:
            genres_list = self.get_genres()
            actors_list = self.get_actors()
            networks_list = self.get_networks()
            if self.list_type == ListType.ANIME:
                a_genres_list = self.get_anime_genres()

        self.all_data = {'tv_data': self.media_details,
                         'seasons_data': seasons_list,
                         'genres_data': genres_list,
                         'anime_genres_data': a_genres_list,
                         'actors_data': actors_list,
                         'networks_data': networks_list}

    def get_movies_details(self):
        self.media_details = {'name': self.media_data.get('title', 'Unknown') or 'Unknown',
                              'original_name': self.media_data.get('original_title', 'Unknown') or 'Unknown',
                              'release_date': self.media_data.get('release_date', 'Unknown') or 'Unknown',
                              'homepage': self.media_data.get('homepage', 'Unknown') or 'Unknown',
                              'released': self.media_data.get('status', 'Unknown') or '"Unknown',
                              'vote_average': self.media_data.get('vote_average', 0) or 0,
                              'vote_count': self.media_data.get('vote_count', 0) or 0,
                              'synopsis': self.media_data.get('overview', 'Not defined.') or 'Not defined.',
                              'popularity': self.media_data.get('popularity', 0) or 0,
                              'budget': self.media_data.get('budget', 0) or 0,
                              'revenue': self.media_data.get('revenue', 0) or 0,
                              'tagline': self.media_data.get('tagline', '-') or '-',
                              'runtime': self.media_data.get('runtime', 0) or 0,
                              'original_language': self.media_data.get('original_language', 'Unknown') or 'Unknown',
                              'themoviedb_id': self.media_data.get('id'),
                              'image_cover': self.get_media_cover()}

        self.get_director_name()

        genres_list = []
        actors_list = []
        if not self.updating:
            genres_list = self.get_genres()
            actors_list = self.get_actors()

        self.all_data = {'movies_data': self.media_details,
                         'genres_data': genres_list,
                         'actors_data': actors_list}

    def get_media_details(self):
        if self.list_type == ListType.SERIES or self.list_type == ListType.ANIME:
            self.get_tv_details()
        elif self.list_type == ListType.MOVIES:
            self.get_movies_details()

        return self.all_data


# Parsing the <API_data> to dict to display the autocomplete
class Autocomplete:
    def __init__(self, result):
        self.tmdb_cover_link = "http://image.tmdb.org/t/p/w300"
        self.result = result
        self.info = {}

    def get_autocomplete_dict(self):
        self.info['tmdb_id'] = self.result.get('id')

        self.info['image_cover'] = url_for('static', filename="covers/series_covers/default.jpg")
        if self.result.get('poster_path'):
            self.info['image_cover'] = "{}{}".format(self.tmdb_cover_link, self.result.get('poster_path'))

        if self.result.get('media_type') == 'tv':
            self.get_tv_dict()
        elif self.result.get('media_type') == 'movie':
            self.get_movies_dict()

        return self.info

    def get_user_dict(self):
        self.info = {'display_name': self.result.username,
                     'image_cover': '/static/profile_pics/' + self.result.image_file,
                     'date': datetime.strftime(self.result.registered_on, '%d %b %Y'),
                     'category': 'Users',
                     'type': 'User'}

        return self.info

    def get_tv_dict(self):
        self.info['category'] = 'Series/Anime'

        return_latin = latin_alphabet(self.result.get('original_name'))
        self.info['display_name'] = self.result.get('name')
        if return_latin is True:
            self.info['display_name'] = self.result.get('original_name')

        self.info['date'] = change_air_format(self.result.get('first_air_date'))
        self.info['type'] = 'Series'
        if self.result.get('origin_country') == 'JP' or self.result.get('original_language') == 'ja' \
                and 16 in self.result.get('genre_ids'):
            self.info['type'] = 'Anime'

    def get_movies_dict(self):
        self.info['category'] = 'Movies'

        return_latin = latin_alphabet(self.result.get('original_title'))
        self.info['display_name'] = self.result.get('title')
        if return_latin is True:
            self.info['display_name'] = self.result.get('original_title')

        self.info['date'] = change_air_format(self.result.get('release_date'))
        self.info['type'] = 'Movie'

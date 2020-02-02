import pytz

from pathlib import Path
from flask import url_for
from MyLists import db, app
from sqlalchemy import func, or_
from flask_login import current_user
from MyLists.models import ListType, UserLastUpdate, SeriesList, AnimeList, MoviesList, Status, User, Series, Anime, \
    AnimeEpisodesPerSeason, SeriesEpisodesPerSeason, SeriesGenre, AnimeGenre, MoviesGenre, Movies, Badges, Ranks


def get_count_and_percentage(user_id, list_type):
    if list_type == ListType.SERIES:
        media_count = db.session.query(SeriesList.status, func.count(SeriesList.status))\
            .filter_by(user_id=user_id).group_by(SeriesList.status).all()
    if list_type == ListType.ANIME:
        media_count = db.session.query(AnimeList.status, func.count(AnimeList.status)) \
            .filter_by(user_id=user_id).group_by(AnimeList.status).all()
    if list_type == ListType.MOVIES:
        media_count = db.session.query(MoviesList.status, func.count(MoviesList.status)) \
            .filter_by(user_id=user_id).group_by(MoviesList.status).all()

    data = {}
    total = sum(x[1] for x in media_count)
    categories = [Status.WATCHING, Status.COMPLETED, Status.COMPLETED_ANIMATION, Status.ON_HOLD, Status.RANDOM,
                  Status.DROPPED, Status.PLAN_TO_WATCH]
    for media in media_count:
        if media[0] in categories:
            data[media[0].value] = {"count": media[1],
                                    "percent": (media[1]/total)*100}
    for media in categories:
        if media.value not in data.keys():
            data[media.value] = {"count": 0,
                                 "percent": 0}

    data['total'] = total
    if total == 0:
        data['nodata'] = True
    else:
        data['nodata'] = False
    return data


def get_total_episodes(user_id, list_type):
    if list_type == ListType.SERIES:
        media_data = db.session.query(SeriesList, SeriesEpisodesPerSeason,
                                       func.group_concat(SeriesEpisodesPerSeason.episodes)) \
            .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.series_id == SeriesList.series_id) \
            .filter(SeriesList.user_id == user_id).group_by(SeriesList.series_id).all()
    elif list_type == ListType.ANIME:
        media_data = db.session.query(AnimeList, AnimeEpisodesPerSeason,
                                      func.group_concat(AnimeEpisodesPerSeason.episodes)) \
            .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.anime_id == AnimeList.anime_id) \
            .filter(AnimeList.user_id == user_id).group_by(AnimeList.anime_id)

    nb_eps_watched = 0
    for element in media_data:
        if element[0].status != Status.PLAN_TO_WATCH and element[0].status != Status.RANDOM:
            episodes = element[2].split(",")
            episodes = [int(x) for x in episodes]
            for i in range(1, element[0].current_season):
                nb_eps_watched += episodes[i - 1]
            nb_eps_watched += element[0].last_episode_watched

    return nb_eps_watched


def get_level_and_grade(user, list_type):
    if list_type == ListType.SERIES:
        total_time_min = user.time_spent_series
    elif list_type == ListType.ANIME:
        total_time_min = user.time_spent_anime
    elif list_type == ListType.MOVIES:
        total_time_min = user.time_spent_movies

    # Compute the corresponding level and percentage from the media time
    element_level_tmp = "{:.2f}".format(round((((400+80*total_time_min)**(1/2))-20)/40, 2))
    element_level = int(element_level_tmp.split('.')[0])
    element_percentage = int(element_level_tmp.split('.')[1])

    query_rank = Ranks.query.filter_by(level=element_level, type='media_rank\n').first()
    if query_rank:
        grade_id = url_for('static', filename='img/levels_ranks/{}'.format(query_rank.image_id))
        grade_title = query_rank.name
    else:
        grade_id = url_for('static', filename='img/levels_ranks/ReachRank49')
        grade_title = "Inheritor"

    level_info = {"level": element_level,
                  "level_percent": element_percentage,
                  "grade_id": grade_id,
                  "grade_title": grade_title}

    return level_info


def get_knowledge_grade(user):
    # Compute the corresponding level and percentage from the media time
    total_time = int(user.time_spent_series + user.time_spent_anime + user.time_spent_movies)
    knowledge_level = int((((400+80*total_time)**(1/2))-20)/40)

    query_rank = Ranks.query.filter_by(level=knowledge_level, type='knowledge_rank\n').first()
    if query_rank:
        grade_id = url_for('static', filename='img/knowledge_ranks/{}'.format(query_rank.image_id))
        grade_title = query_rank.name
    else:
        grade_id = url_for('static', filename='img/knowledge_ranks/Knowledge_Emperor_Grade_4')
        grade_title = "Knowledge Emperor Grade 4"

    return {"level": knowledge_level,
            "grade_id": grade_id,
            "grade_title": grade_title}


def get_time_spent(user, list_type):
    if list_type == ListType.SERIES:
        time_in_min = user.time_spent_series
    elif list_type == ListType.ANIME:
        time_in_min = user.time_spent_anime
    elif list_type == ListType.MOVIES:
        time_in_min = user.time_spent_movies

    return time_in_min


def get_updates(last_update):
    update = []
    for element in last_update:
        element_data = {}
        # Season or episode update
        if element.old_status is None and element.new_status is None:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element.old_season, element.old_episode),
                                      "S{:02d}.E{:02d}".format(element.new_season, element.new_episode)]

        # Category update
        elif element.old_status is not None and element.new_status is not None:
            element_data["update"] = ["{}".format(element.old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element.new_status.value).replace("Animation", "Anime")]

        # Newly added media
        elif element.old_status is None and element.new_status is not None:
            element_data["update"] = ["{}".format(element.new_status.value)]

        # Update date and add media name
        element_data["date"] = element.date.replace(tzinfo=pytz.UTC).isoformat()
        element_data["media_name"] = element.media_name

        if element.media_type == ListType.SERIES:
            element_data["category"] = "series"
        elif element.media_type == ListType.ANIME:
            element_data["category"] = "anime"
        elif element.media_type == ListType.MOVIES:
            element_data["category"] = "movie"

        update.append(element_data)

    return update


# -----------------------------------------------


def get_user_data(user):
    # Recover the view count of the account and the media lists
    if current_user.id != 1 and user.id != current_user.id:
        user.profile_views += 1
        profile_view_count = user.profile_views
        db.session.commit()
    else:
        profile_view_count = user.profile_views
    view_count = {"profile": profile_view_count,
                  "series": user.series_views,
                  "anime": user.anime_views,
                  "movies": user.movies_views}

    # Check if the current user follows the user's account
    if user.id != current_user.id and current_user.is_following(user):
        isfollowing = True
    else:
        isfollowing = False

    # Recover the number of person that follows you
    followers = user.followers.count()

    # Recover the knowledge grade and level of the user
    knowledge_info = get_knowledge_grade(user)

    # Recover the last update (in the overview) of the user if current_user != target_user
    last_update = UserLastUpdate.query.filter_by(user_id=user.id).order_by(UserLastUpdate.date.desc()).limit(4)
    media_update = get_updates(last_update)

    user_data = {"id": str(user.id),
                 "username": user.username,
                 "profile_picture": url_for('static', filename='profile_pics/{0}'.format(user.image_file)),
                 "register": user.registered_on.strftime("%d %b %Y"),
                 "biography": user.biography,
                 "followers": followers,
                 "isfollowing": isfollowing,
                 "knowledge_info": knowledge_info,
                 "media_update": media_update,
                 "view_count": view_count}

    return user_data


def get_media_data(user, list_type):
    media_count_percentage = get_count_and_percentage(user.id, list_type)
    levels_and_grades = get_level_and_grade(user, list_type)
    time_spent = get_time_spent(user, list_type)
    if list_type != ListType.MOVIES:
        media_total_episodes = get_total_episodes(user.id, list_type)
    else:
        media_total_episodes = None

    media_data = {"time_spent_hour": round(time_spent/60),
                  "time_spent_day": round(time_spent/1440, 2),
                  "count_and_percentage": media_count_percentage,
                  "nb_ep_watched": media_total_episodes,
                  "level_and_grades": levels_and_grades}

    return media_data


def get_follows_data(user):
    # Recover the follows list
    follows_data = []
    for follow in user.followed.all():
        follow_data = {"username": follow.username,
                       "user_id": follow.id,
                       "picture": url_for('static', filename='profile_pics/{0}'.format(follow.image_file))}

        if follow.private:
            if current_user.id == 1 or current_user.is_following(follow):
                follows_data.append(follow_data)
            elif current_user.id == follow.id:
                follows_data.append(follow_data)
        else:
            follows_data.append(follow_data)

    return follows_data


def get_follows_full_last_update(user):
    follows_update = user.followed_last_updates()

    tmp = ""
    follows_data = []
    for i in range(0, len(follows_update)):
        element = follows_update[i]
        if element[0].username != tmp:
            tmp = element[0].username
            follow_data = {"username": element[0].username,
                           "update": []}

        element_data = {}
        # Season or episode update
        if element[3].old_status is None and element[3].new_status is None:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element[3].old_season, element[3].old_episode),
                                      "S{:02d}.E{:02d}".format(element[3].new_season, element[3].new_episode)]

        # Category update
        elif element[3].old_status is not None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element[3].new_status.value).replace("Animation", "Anime")]

        # Media newly added
        elif element[3].old_status is None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].new_status.value)]

        element_data["date"] = element[3].date.replace(tzinfo=pytz.UTC).isoformat()
        element_data["media_name"] = element[3].media_name

        if element[3].media_type == ListType.SERIES:
            element_data["category"] = "series"
        elif element[3].media_type == ListType.ANIME:
            element_data["category"] = "anime"
        elif element[3].media_type == ListType.MOVIES:
            element_data["category"] = "movie"

        # TODO: TEMP FIX
        if len(follow_data["update"]) <= 5:
            follow_data["update"].append(element_data)

        try:
            if element[0].username != follows_update[i+1][0].username:
                follows_data.append(follow_data)
            else:
                pass
        except:
            follows_data.append(follow_data)

    return follows_data


def get_follows_last_update(user):
    follows_update = user.followed_last_updates_overview()

    update = []
    for element in follows_update:
        element_data = {}
        # Season or episode update
        if element[3].old_status is None and element[3].new_status is None:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element[3].old_season, element[3].old_episode),
                                      "S{:02d}.E{:02d}".format(element[3].new_season, element[3].new_episode)]

        # Category update
        elif element[3].old_status is not None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element[3].new_status.value).replace("Animation", "Anime")]

        # Newly added media
        elif element[3].old_status is None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].new_status.value)]

        # Update date
        element_data["date"] = element[3].date.replace(tzinfo=pytz.UTC).isoformat()

        element_data["media_name"] = element[3].media_name

        if element[3].media_type == ListType.SERIES:
            element_data["category"] = "series"
        elif element[3].media_type == ListType.ANIME:
            element_data["category"] = "anime"
        elif element[3].media_type == ListType.MOVIES:
            element_data["category"] = "movie"

        element_data["username"] = element[0].username

        update.append(element_data)

    return update


def get_badges(user_id):
    user = User.query.filter_by(id=user_id).first()

    def get_queries():
        series_data = db.session.query(Series, SeriesList, func.group_concat(SeriesGenre.genre.distinct()),
                                       func.group_concat(SeriesEpisodesPerSeason.season.distinct()),
                                       func.group_concat(SeriesEpisodesPerSeason.episodes))\
            .join(SeriesList, SeriesList.series_id == Series.id)\
            .join(SeriesGenre, SeriesGenre.series_id == Series.id)\
            .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.series_id == Series.id)\
            .filter(SeriesList.user_id == user_id)\
            .filter(or_(SeriesGenre.genre == "Animation", SeriesGenre.genre == "Comedy", SeriesGenre.genre == "Crime",
                        SeriesGenre.genre == "Documentary", SeriesGenre.genre == "Mystery",
                        SeriesGenre.genre == "Historical", SeriesGenre.genre == "War & Politics",
                        SeriesGenre.genre == "Sci-Fi & Fantasy"))\
            .group_by(Series.id).all()

        anime_data = db.session.query(Anime, AnimeList, func.group_concat(AnimeGenre.genre.distinct()),
                                      func.group_concat(AnimeEpisodesPerSeason.season.distinct()),
                                      func.group_concat(AnimeEpisodesPerSeason.episodes))\
            .join(AnimeList, AnimeList.anime_id == Anime.id)\
            .join(AnimeGenre, AnimeGenre.anime_id == Anime.id)\
            .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.anime_id == Anime.id)\
            .filter(AnimeList.user_id == user_id) \
            .filter(or_(AnimeGenre.genre == "Comedy", AnimeGenre.genre == "Police", AnimeGenre.genre == "Supernatural",
                        AnimeGenre.genre == "Music", AnimeGenre.genre == "Mystery", AnimeGenre.genre == "Historical",
                        AnimeGenre.genre == "Romance", AnimeGenre.genre == "Sci-Fi", AnimeGenre.genre == "Fantasy",
                        AnimeGenre.genre == "Horror", AnimeGenre.genre == "Thriller", AnimeGenre.genre == "Sports",
                        AnimeGenre.genre == "Slice of Life", AnimeGenre.genre == "School")) \
            .group_by(Anime.id).all()

        movies_data = db.session.query(Movies, MoviesList, func.group_concat(MoviesGenre.genre.distinct()))\
            .join(MoviesList, MoviesList.movies_id == Movies.id)\
            .join(MoviesGenre, MoviesGenre.movies_id == Movies.id)\
            .filter(MoviesList.user_id == user_id) \
            .filter(or_(MoviesGenre.genre == "Comedy", MoviesGenre.genre == "Crime", MoviesGenre.genre == "Music",
                        MoviesGenre.genre == "Mystery", MoviesGenre.genre == "History",
                        MoviesGenre.genre == "Documentary", MoviesGenre.genre == "Romance",
                        MoviesGenre.genre == "Horror", MoviesGenre.genre == "War", MoviesGenre.genre == "Fantasy",
                        MoviesGenre.genre == "Thriller", MoviesGenre.genre == "Animation",
                        MoviesGenre.genre == "Science Fiction"))\
            .group_by(Movies.id).all()

        sum_data = series_data + anime_data + movies_data

        return sum_data

    def get_episodes_and_time(element):
        if element[1].status == Status.COMPLETED or element[1].status == Status.COMPLETED_ANIMATION:
            try:
                return [1, element[0].runtime]
            except:
                return [element[0].total_episodes, int(element[0].episode_duration) * element[0].total_episodes]
        elif element[1].status != Status.PLAN_TO_WATCH and element[1].status != Status.RANDOM:
            nb_season = len(element[3].split(","))
            nb_episodes = element[4].split(",")[:nb_season]

            ep_duration = int(element[0].episode_duration)
            ep_counter = 0
            for i in range(0, element[1].current_season - 1):
                ep_counter += int(nb_episodes[i])
            episodes_watched = ep_counter + element[1].last_episode_watched
            time_watched = (ep_duration * episodes_watched)
            return [episodes_watched, time_watched]
        else:
            return [0, 0]

    def create_badge_dict(badge, unlocked, time=None, count=None):
        if time is not None:
            value = int(time/60)
        else:
            value = count

        badge_data = {"type": badge.type,
                      "image_id": badge.image_id,
                      "title": badge.title,
                      "unlocked": unlocked,
                      "value": value}

        return badge_data

    total_data = get_queries()
    time_spent = int(user.time_spent_anime) + int(user.time_spent_series) + int(user.time_spent_movies)

    all_badges = []
    time_by_genre = {}
    time_classic = 0
    count_completed = 0
    long_media_shows = 0
    long_media_movies = 0
    for element in total_data:
        eps_and_time = get_episodes_and_time(element)
        episodes_watched = eps_and_time[0]
        time_watched = eps_and_time[1]

        # Genres badges
        genres = element[2].split(',')
        for genre in genres:
            if genre not in time_by_genre:
                if genre == "Supernatural":
                    if "Mystery" not in time_by_genre:
                        time_by_genre["Mystery"] = time_watched
                    else:
                        time_by_genre["Mystery"] += time_watched
                elif genre == "Police":
                    if "Crime" not in time_by_genre:
                        time_by_genre["Crime"] = time_watched
                    else:
                        time_by_genre["Crime"] += time_watched
                elif genre == "War" or genre == "War & Politics" or genre == "History":
                    if "Historical" not in time_by_genre:
                        time_by_genre["Historical"] = time_watched
                    else:
                        time_by_genre["Historical"] += time_watched
                elif genre == "Sci-Fi & Fantasy":
                    if "Fantasy" not in time_by_genre:
                        time_by_genre["Fantasy"] = time_watched
                    else:
                        time_by_genre["Fantasy"] += time_watched
                    if "Science Fiction" not in time_by_genre:
                        time_by_genre["Science Fiction"] = time_watched
                    else:
                        time_by_genre["Science Fiction"] += time_watched
                elif genre == "Sci-Fi":
                    if "Science Fiction" not in time_by_genre:
                        time_by_genre["Science Fiction"] = time_watched
                    else:
                        time_by_genre["Science Fiction"] += time_watched
                elif genre == "School":
                    if "Slice of Life" not in time_by_genre:
                        time_by_genre["Slice of Life"] = time_watched
                    else:
                        time_by_genre["Slice of Life"] += time_watched
                else:
                    time_by_genre[genre] = time_watched
            else:
                time_by_genre[genre] += time_watched

        # Classic media bagdes, before 1990 without movies
        try:
            first_year = int(element[0].first_air_date.split('-')[0])
            if first_year <= 1990 and element[1].status != Status.PLAN_TO_WATCH \
                    and element[1].status != Status.RANDOM:
                time_classic += time_watched
        except:
            pass
        # Classic media bagdes, before 1990 movies
        try:
            release_date = int(element[0].release_date.split('-')[0])
            if release_date <= 1990 and element[1].status != Status.PLAN_TO_WATCH:
                time_classic += time_watched
        except:
            pass

        # Completed media badges without movies
        try:
            status = element[0].status
            if (status == "Ended" or status == "Canceled" or status == "Released") \
                    and (element[1].status == Status.COMPLETED or element[1].status == Status.COMPLETED_ANIMATION):
                count_completed += 1
        except:
            pass
        # Completed media badges movies
        try:
            status = element[0].released
            if status == "Released" and element[1].status == Status.COMPLETED \
                    or element[1].status == Status.COMPLETED_ANIMATION:
                count_completed += 1
        except:
            pass

        # Long media shows, more than 100 episodes
        try:
            if int(episodes_watched) >= 100:
                long_media_shows += 1
        except:
            pass

        # Long media movies, more than 2h30
        try:
            if element[0].runtime >= 150:
                long_media_movies += 1
        except:
            pass

    # Genres badges
    genres_values = ["Mystery", "Historical", "Horror", "Music", "Romance", "Sports", "Slice of Life", "Comedy",
                     "Crime", "Documentary", "Science Fiction", "Animation", "Fantasy", "Thriller"]
    for i in range(0, len(genres_values)):
        badge = db.session.query(Badges).filter_by(title=genres_values[i]).first()
        try:
            genre_time_data = time_by_genre[genres_values[i]]
        except:
            genre_time_data = 0
        count_unlocked = int((genre_time_data/60)/badge.threshold)
        badge_data = create_badge_dict(badge, count_unlocked, time=genre_time_data)
        all_badges.append(badge_data)

    # Classic badges
    badge = db.session.query(Badges).filter_by(type="classic").first()
    count_unlocked = int((time_classic/60)/badge.threshold)
    badge_data = create_badge_dict(badge, count_unlocked, time=time_classic)
    all_badges.append(badge_data)

    # Completed badges
    badge = db.session.query(Badges).filter_by(type="completed").first()
    count_unlocked = int(count_completed/badge.threshold)
    badge_data = create_badge_dict(badge, count_unlocked, count=count_completed)
    all_badges.append(badge_data)

    # Time badges
    badge = db.session.query(Badges).filter_by(type="total-time").first()
    count_unlocked = int((time_spent/1440)/badge.threshold)
    badge_data = create_badge_dict(badge, count_unlocked, time=(time_spent/24))
    all_badges.append(badge_data)

    # Long shows badges
    badge = db.session.query(Badges).filter_by(type="longshows").first()
    count_unlocked = int(long_media_shows/badge.threshold)
    badge_data = create_badge_dict(badge, count_unlocked, count=long_media_shows)
    all_badges.append(badge_data)

    # Long movies badges
    badge = db.session.query(Badges).filter_by(type="longmovies").first()
    count_unlocked = int(long_media_movies/badge.threshold)
    badge_data = create_badge_dict(badge, count_unlocked, count=long_media_movies)
    all_badges.append(badge_data)

    all_badges.sort(key=lambda x: (x['unlocked'], x['value']), reverse=True)
    total_unlocked = 0
    for item in all_badges:
        total_unlocked += item["unlocked"]

    return [all_badges, total_unlocked]

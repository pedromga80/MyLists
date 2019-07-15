import json
import os
import platform
import secrets
import sys
import urllib
import time
import requests
import pandas as pd

from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from MyLists import app, db, bcrypt, mail, config
from MyLists.admin_views import User
from MyLists.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchSeriesForm, SearchAnimeForm, \
    ChangePasswordForm, AddFriendForm, ResetPasswordForm, ResetPasswordRequestForm, SearchBookForm
from MyLists.models import Series, SeriesList, SeriesEpisodesPerSeason, Status, ListType, SeriesGenre, SeriesNetwork, \
    Friend, SeriesEpisodeTimestamp, Anime, AnimeList, AnimeEpisodesPerSeason, AnimeGenre, AnimeNetwork, AnimeEpisodeTimestamp, \
    HomePage, HallOfFame, Status_book, Book, BookList


config.read('config.ini')
try:
    themoviedb_api_key = config['TheMovieDB']['api_key']
except:
    print("Config file error. Exit.")
    sys.exit()


@app.before_first_request
def create_user():
    db.create_all()
    if User.query.filter_by(id='1').first() is None:
        admin = User(username='admin',
                     email='admin@admin.com',
                     password=bcrypt.generate_password_hash("password").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(admin)

    if User.query.filter_by(id='2').first() is None:
        test = User(username='test',
                    email='test@test.com',
                    password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                    image_file='default.jpg',
                    active=True,
                    private=True,
                    registered_on=datetime.utcnow(),
                    activated_on=datetime.utcnow())
        db.session.add(test)

    if User.query.filter_by(id='3').first() is None:
        test2 = User(username='test2',
                     email='test2@test2.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test2)

    if User.query.filter_by(id='4').first() is None:
        test3 = User(username='test3',
                     email='test3@test3.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test3)

    if User.query.filter_by(id='5').first() is None:
        test4 = User(username='test4',
                     email='test4@test4.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test4)

    if User.query.filter_by(id='6').first() is None:
        test5 = User(username='aaaa',
                     email='test5@test5.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test5)

    if User.query.filter_by(id='7').first() is None:
        test6 = User(username='Sudoer',
                     email='test6@test6.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test6)

    if User.query.filter_by(id='8').first() is None:
        test7 = User(username='aaa',
                     email='test7@test7.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test7)

    if User.query.filter_by(id='9').first() is None:
        test8 = User(username='I_Love_Anime',
                     email='test8@test8.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test8)

    if User.query.filter_by(id='10').first() is None:
        test9 = User(username='0010100011',
                     email='test9@test9.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test9)

    if User.query.filter_by(id='11').first() is None:
        test10 = User(username='Crossoufire',
                     email='test10@test10.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test10)

    if User.query.filter_by(id='12').first() is None:
        test11 = User(username='WynroZ',
                     email='test11@test11.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test11)
    db.session.commit()


################################################### Anonymous routes ###################################################


@app.route("/", methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.login_username.data).first()
        if user and not user.active:
            app.logger.info('[{}] Connexion attempt while account not activated'.format(user.id))
            flash('Your Account is not activated. Please check your e-mail address to activate your account.', 'danger')
        elif user and bcrypt.check_password_hash(user.password, login_form.login_password.data):
            login_user(user, remember=login_form.login_remember.data)
            next_page = request.args.get('next')
            app.logger.info('[{}] Logged in'.format(user.id))
            flash("You're now logged in. Welcome {0}".format(login_form.login_username.data), "success")
            home_page = str(user.home_page.value)
            return redirect(next_page) if next_page else redirect(url_for(home_page))
        else:
            flash('Login Failed. Please check Username and Password', 'warning')

    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.register_password.data).decode('utf-8')
        user = User(username=register_form.register_username.data,
                    email=register_form.register_email.data,
                    password=hashed_password,
                    active=False,
                    private=False,
                    registered_on=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        app.logger.info('[{}] New account registration : username = {}, email = {}'.format(user.id,
                                                                                           register_form.register_username.data,
                                                                                           register_form.register_email.data))
        if send_register_email(user):
            flash('Your account has been created. Check your e-mail address to activate your account!', 'info')
            return redirect(url_for('home'))
        else:
            app.logger.error('[SYSTEM] Error while sending the registration email to {}'.format(user.email))
            image_error = url_for('static', filename='img/error.jpg')
            return render_template('error.html', error_code=500, title='Error', image_error=image_error), 500

    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.get_id()).first()
        if user.home_page == HomePage.ACCOUNT:
            return redirect(url_for('account'))
        elif user.home_page == HomePage.HALL_OF_FAME:
            return redirect(url_for('hall_of_fame'))
        elif user.home_page == HomePage.MYSERIESLIST:
            return redirect(url_for('myserieslist'))
        elif user.home_page == HomePage.MYANIMELIST:
            return redirect(url_for('myanimelist'))

    else:
        home_header = url_for('static', filename='img/home_header.jpg')
        img1 = url_for('static', filename='img/home_img1.jpg')
        img2 = url_for('static', filename='img/home_img2.jpg')
        return render_template('home.html',
                               title='Home',
                               login_form=login_form,
                               register_form=register_form,
                               image_header=home_header,
                               img1=img1,
                               img2=img2)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('myserieslist'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if send_reset_email(user):
            app.logger.info('[{}] Reset password email sent'.format(user.id))
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('home'))
        else:
            app.logger.error('[SYSTEM] Error while sending the reset password email to {}'.format(user.email))
            flash("There was an error while sending the reset password email. Please try again later.")
            return redirect(url_for('home'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('myserieslist'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        app.logger.info('[{}] Password reset via reset password email'.format(user.id))
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/register_account/<token>", methods=['GET', 'POST'])
def register_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('myserieslist'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))

    user.active = True
    user.activated_on = datetime.utcnow()
    db.session.commit()
    app.logger.info('[{}] Account activated'.format(user.id))
    flash('Your account has been activated.', 'success')
    return redirect(url_for('home'))


@app.route("/test")
def test():
    crawl_tmdb()
    return render_template('test.html')


################################################# Authenticated routes #################################################


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    pass


@app.route("/logout")
@login_required
def logout():
    user = User.query.filter_by(id=current_user.get_id()).first()
    logout_user()
    app.logger.info('[{}] Logged out'.format(user.id))
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    add_friend_form = AddFriendForm()
    if add_friend_form.validate_on_submit():
        if str(add_friend_form.add_friend.data) == str(current_user.username):
            flash("You cannot add yourself.", 'info')
            return redirect(url_for('account'))
        add_friend(add_friend_form.add_friend.data)

    # Profile picture
    profile_picture = url_for('static', filename='profile_pics/{0}'.format(current_user.image_file))

    # Friends list
    friends_list = Friend.query.filter_by(user_id=current_user.get_id()).all()
    friends_list_data = []
    for friend in friends_list:
        friend_data = {}
        friend_username = User.query.filter_by(id=friend.friend_id).first().username
        friend_data["username"] = friend_username
        friend_data["user_id"] = friend.friend_id
        friend_data["status"] = friend.status
        friends_list_data.append(friend_data)

    # Series Statistics
    nb_of_series = get_list_count(ListType.SERIES)
    total_series = sum(nb_of_series)
    if total_series == 0:
        series_rate = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        series_rate = [(float(nb_of_series[0]/total_series))*100,
                              (float(nb_of_series[1]/total_series))*100,
                              (float(nb_of_series[2]/total_series))*100,
                              (float(nb_of_series[3]/total_series))*100,
                              (float(nb_of_series[4]/total_series))*100,
                              (float(nb_of_series[5]/total_series))*100]

    total_time_series = get_total_time_spent(current_user.get_id(), ListType.SERIES)

    # Animes Statistics
    nb_of_animes = get_list_count(ListType.ANIME)
    total_anime = sum(nb_of_animes)
    if total_anime == 0:
        anime_rate = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        anime_rate = [(float(nb_of_animes[0]/total_anime))*100,
                              (float(nb_of_animes[1]/total_anime))*100,
                              (float(nb_of_animes[2]/total_anime))*100,
                              (float(nb_of_animes[3]/total_anime))*100,
                              (float(nb_of_animes[4]/total_anime))*100,
                              (float(nb_of_animes[5]/total_anime))*100]

    total_time_animes = get_total_time_spent(current_user.get_id(), ListType.ANIME)

    return render_template('account.html',
                           title='Account',
                           profile_picture=profile_picture,
                           nb_of_series=nb_of_series,
                           series_rate=series_rate,
                           total_time_series=total_time_series,
                           nb_of_animes=nb_of_animes,
                           total_time_animes=total_time_animes,
                           anime_rate=anime_rate,
                           friends_list_data=friends_list_data,
                           form=add_friend_form)


@app.route("/account_settings", methods=['GET', 'POST'])
@login_required
def account_settings():
    form = UpdateAccountForm()

    user = User.query.filter_by(id=current_user.get_id()).first()
    is_private = user.private
    if is_private:
        is_private = "checked"
    else:
        is_private = "unchecked"

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            old_picture_file = user.image_file
            user.image_file = picture_file
            db.session.commit()
            app.logger.info(
                '[{}] Settings updated : old picture file = {}, new picture file = {}'.format(user.id, old_picture_file,
                                                                                              user.image_file))
        if form.username.data != user.username:
            old_username = user.username
            user.username = form.username.data
            db.session.commit()
            app.logger.info('[{}] Settings updated : old username = {}, new username = {}'.format(user.id, old_username,
                                                                                                  user.username))
        email_changed = False
        if form.email.data != user.email:
            old_email = user.email
            user.transition_email = form.email.data
            db.session.commit()
            app.logger.info('[{}] Settings updated : old email = {}, new email = {}'.format(user.id, old_email,
                                                                                            user.transition_email))
            email_changed = True
            if send_email_update_email(user):
                success = True
            else:
                success = False
                app.logger.error('[SYSTEM] Error while sending the email update email to {}'.format(user.email))

        if not email_changed:
            flash("Your account has been updated ! ", 'success')
        else:
            if success:
                flash("Your account has been updated ! Please click on the link to validate your new email address.",
                      'success')
            else:
                flash("There was an error internal error. Please contact the administrator.", 'danger')

        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/{0}'.format(current_user.image_file))
    return render_template('account_settings.html', title='Settings', image_file=image_file, form=form,
                           value_privacy=is_private, home_page=str(user.home_page.value), default_hof=str(user.default_hof.value))


@app.route("/default_page", methods=['POST'])
@login_required
def default_page():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        home_page = int(json_data['home_page'])
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    user = User.query.filter_by(id=current_user.get_id()).first()

    if home_page == 0:
        user.home_page = HomePage.ACCOUNT
    elif home_page == 1:
        user.home_page = HomePage.HALL_OF_FAME
    elif home_page == 2:
        user.home_page = HomePage.MYSERIESLIST
    elif home_page == 3:
        user.home_page = HomePage.MYANIMELIST
    else:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    db.session.commit()
    return '', 204


@app.route("/default_hof", methods=['POST'])
@login_required
def default_hof():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        default_hof = int(json_data['default_hof'])
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    user = User.query.filter_by(id=current_user.get_id()).first()

    if default_hof == 0:
        user.default_hof = HallOfFame.MYSERIESLIST
    elif default_hof == 1:
        user.default_hof = HallOfFame.MYANIMELIST
    else:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    db.session.commit()
    return '', 204


@app.route("/email_update/<token>", methods=['GET'])
@login_required
def email_update_token(token):

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))

    if str(user.id) != current_user.get_id():
        return redirect(url_for('myserieslist'))

    old_email = user.email
    user.email = user.transition_email
    user.transition_email = None
    db.session.commit()
    app.logger.info('[{}] Email successfully changed from {} to {}'.format(user.id, old_email, user.email))
    flash('Email successfully updated !', 'success')
    return redirect(url_for('myserieslist'))


@app.route('/private_mode', methods=['POST'])
@login_required
def private_data():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        triggered = json_data['private']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    user = User.query.filter_by(id=current_user.get_id()).first()
    is_private = user.private
    if is_private:
        user.private = False
    else:
        user.private = True
    db.session.commit()
    app.logger.info('[{}] Private mode updated'.format(user.id))
    return '', 204


@app.route('/change_pass', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.get_id()).first()
        if user and bcrypt.check_password_hash(user.password, form.actual_password.data):
            hashed_password = bcrypt.generate_password_hash(form.confirm_new_password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            app.logger.info('[{}] Password updated'.format(user.id))
            flash('Your password has been successfully updated!', 'success')
            return redirect(url_for('account'))
        else:
            flash('Current password incorrect', 'danger')
    return render_template('change_pass.html', form=form)


@app.route("/accept_friend_request", methods=['POST'])
@login_required
def accept_friend_request():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        friend_id = json_data['reponse']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        friend_id = int(friend_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if there is an actual pending request
    user = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id, status="pending").first()
    if user is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    user.status = 'accepted'
    db.session.commit()

    user2 = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.get_id(), status="request").first()
    if user2 is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    user2.status = 'accepted'
    db.session.commit()
    app.logger.info('[{}] Friend request accepted from user with ID {}'.format(current_user.get_id(), friend_id))
    return '', 204


@app.route("/decline_friend_request", methods=['POST'])
@login_required
def decline_friend_request():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        decline_friend = json_data['reponse']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        decline_friend = int(decline_friend)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if there is an actual pending request
    # Otherwise delete the pending request
    if not Friend.query.filter_by(user_id=current_user.get_id(), friend_id=decline_friend, status="pending").delete():
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    db.session.commit()

    if not Friend.query.filter_by(user_id=decline_friend, friend_id=current_user.get_id(), status="request").delete():
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    db.session.commit()
    app.logger.info('[{}] Friend request declined from user with ID {}'.format(current_user.get_id(), decline_friend))
    return '', 204


@app.route('/delete_friend', methods=['POST'])
@login_required
def delete_friend():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        friend_id = json_data['delete']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        friend_id = int(friend_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the friend to delete is in the friend list
    if Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id).delete()
    Friend.query.filter_by(user_id=friend_id, friend_id=current_user.get_id()).delete()
    db.session.commit()
    app.logger.info('[{}] Friend with ID {} deleted'.format(current_user.get_id(), friend_id))
    return '', 204


@app.route("/hall_of_fame")
@login_required
def hall_of_fame():
    # Get list of all users except admin
    users = User.query.filter(User.id >= "2").order_by(User.username.asc()).all()

    current_user_friends = Friend.query.filter_by(user_id=current_user.get_id(), status="accepted").all()
    friends_list = []
    for friend in current_user_friends:
        friends_list.append(friend.friend_id)

    current_user_pending_friends = Friend.query.filter_by(user_id=current_user.get_id(), status="request").all()
    friends_pending_list = []
    for friend in current_user_pending_friends:
        friends_pending_list.append(friend.friend_id)

    # Series hall of fame
    all_user_data_series = []
    for user in users:
        watching     = SeriesList.query.filter_by(user_id=user.id, status='WATCHING').count()
        completed    = SeriesList.query.filter_by(user_id=user.id, status='COMPLETED').count()
        onhold       = SeriesList.query.filter_by(user_id=user.id, status='ON_HOLD').count()
        random       = SeriesList.query.filter_by(user_id=user.id, status='RANDOM').count()
        dropped      = SeriesList.query.filter_by(user_id=user.id, status='DROPPED').count()
        plantowatch  = SeriesList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').count()

        total = watching + completed + onhold + random + dropped + plantowatch
        spent = get_total_time_spent(user.id, ListType.SERIES)

        # profile picture
        profile_picture = url_for('static', filename='profile_pics/{0}'.format(user.image_file))

        user_data = {"profile_picture": profile_picture,
                     "username": user.username,
                     "watching": watching,
                     "completed": completed,
                     "onhold": onhold,
                     "random": random,
                     "dropped": dropped,
                     "plantowatch": plantowatch,
                     "total": total,
                     "days": spent[2],
                     "episodes": spent[0]}

        if user.id in friends_list:
            user_data["isfriend"] = True
            user_data["ispendingfriend"] = False
        else:
            if user.id in friends_pending_list:
                user_data["ispendingfriend"] = True
            else:
                user_data["ispendingfriend"] = False
            user_data["isfriend"] = False

        if str(user.id) == current_user.get_id():
            user_data["isprivate"] = False
            user_data["iscurrentuser"] = True
        else:
            user_data["isprivate"] = user.private
            user_data["iscurrentuser"] = False

        all_user_data_series.append(user_data)

    # Anime hall of fame
    all_user_data_animes = []
    for user in users:
        watching    = AnimeList.query.filter_by(user_id=user.id, status='WATCHING').count()
        completed   = AnimeList.query.filter_by(user_id=user.id, status='COMPLETED').count()
        onhold      = AnimeList.query.filter_by(user_id=user.id, status='ON_HOLD').count()
        random      = AnimeList.query.filter_by(user_id=user.id, status='RANDOM').count()
        dropped     = AnimeList.query.filter_by(user_id=user.id, status='DROPPED').count()
        plantowatch = AnimeList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').count()

        total = watching + completed + onhold + random + dropped + plantowatch
        spent = get_total_time_spent(user.id, ListType.ANIME)

        # profile picture
        profile_picture = url_for('static', filename='profile_pics/{0}'.format(user.image_file))

        user_data = {"profile_picture": profile_picture,
                     "username": user.username,
                     "watching": watching,
                     "completed": completed,
                     "onhold": onhold,
                     "random": random,
                     "dropped": dropped,
                     "plantowatch": plantowatch,
                     "total": total,
                     "days": spent[2],
                     "episodes": spent[0]}

        if user.id in friends_list:
            user_data["isfriend"] = True
            user_data["ispendingfriend"] = False
        else:
            if user.id in friends_pending_list:
                user_data["ispendingfriend"] = True
            else:
                user_data["ispendingfriend"] = False
            user_data["isfriend"] = False

        if str(user.id) == current_user.get_id():
            user_data["isprivate"] = False
            user_data["iscurrentuser"] = True
        else:
            user_data["isprivate"] = user.private
            user_data["iscurrentuser"] = False

        all_user_data_animes.append(user_data)

    return render_template("hall_of_fame.html",
                           title='Hall of Fame',
                           series_data=all_user_data_series,
                           anime_data=all_user_data_animes)


@app.route("/add_friend_hof", methods=['POST'])
@login_required
def add_friend_hof():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        user_name = json_data['user_name']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    add_friend(user_name)
    return '', 204


@app.route("/anonymous")
@login_required
def anonymous():
    image_anonymous = url_for('static', filename='img/anonymous.jpg')
    return render_template("anonymous.html", title="Anonymous", image_anonymous=image_anonymous)


##################################################### Series routes ####################################################


@app.route("/myserieslist", methods=['GET', 'POST'])
@login_required
def myserieslist():
    form = SearchSeriesForm()
    if form.validate_on_submit():
        add_element(form.serie.data.strip(), ListType.SERIES)

    watching_list    = SeriesList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').all()
    completed_list   = SeriesList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list      = SeriesList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    random_list      = SeriesList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').all()
    dropped_list     = SeriesList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantowatch_list = SeriesList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').all()

    series_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    series_data = get_list_data(series_list, ListType.SERIES)
    return render_template('myserieslist.html', title='MySeriesList', form=form, all_data=series_data)


@app.route('/update_series_season', methods=['POST'])
@login_required
def update_series_season():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        season = json_data['season']
        series_id = json_data['series_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        season = int(season)
        series_id = int(series_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Series.query.filter_by(id=series_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=series_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the season number is between 1 and <last_season>
    last_season = SeriesEpisodesPerSeason.query.filter_by(series_id=series_id).order_by(
        SeriesEpisodesPerSeason.season.desc()).first().season
    if season + 1 < 1 or season + 1 > last_season:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    update = SeriesList.query.filter_by(series_id=series_id, user_id=current_user.get_id()).first()

    old_season = update.current_season

    if old_season < season + 1:
        for i in range(old_season, season + 1):
            for j in range(1, SeriesEpisodesPerSeason.query.filter_by(series_id=series_id, season=i).first().episodes + 1):
                if SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), series_id=series_id, season=i,
                                                          episode=j).first() is None:
                    ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                                series_id=series_id,
                                                season=i,
                                                episode=j,
                                                timestamp=datetime.utcnow())
                    db.session.add(ep)
        ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                    series_id=series_id,
                                    season=season + 1,
                                    episode=1,
                                    timestamp=datetime.utcnow())
        db.session.add(ep)
        db.session.commit()

    elif old_season > season + 1:
        for i in range(season + 1, old_season + 1):
            SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), series_id=series_id, season=i).delete()
        ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                    series_id=series_id,
                                    season=season + 1,
                                    episode=1,
                                    timestamp=datetime.utcnow())
        db.session.add(ep)
        db.session.commit()

    update.current_season = season + 1
    update.last_episode_watched = 1
    db.session.commit()
    app.logger.info(
        '[{}] Season of the serie with ID {} updated to {}'.format(current_user.get_id(), series_id, season + 1))
    return '', 204


@app.route('/update_series_episode', methods=['POST'])
@login_required
def update_series_episode():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        episode = json_data['episode']
        series_id = json_data['series_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        episode = int(episode)
        series_id = int(series_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Series.query.filter_by(id=series_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=series_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the episode number is between 1 and <last_episode>
    current_season = SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=series_id).first().current_season
    last_episode = SeriesEpisodesPerSeason.query.filter_by(series_id=series_id, season=current_season).first().episodes
    if episode + 1 < 1 or episode + 1 > last_episode:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    update = SeriesList.query.filter_by(series_id=series_id, user_id=current_user.get_id()).first()
    old_last_episode_watched = update.last_episode_watched
    current_season = update.current_season

    if episode + 1 > old_last_episode_watched:
        for i in range(old_last_episode_watched + 1, episode + 2):
            ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                        series_id=series_id,
                                        season=current_season,
                                        episode=i,
                                        timestamp=datetime.utcnow())
            db.session.add(ep)
        db.session.commit()
    elif episode + 1 < old_last_episode_watched:
        for i in range(episode + 2, old_last_episode_watched + 1):
            SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), series_id=series_id, season=current_season,
                                                   episode=i).delete()
        db.session.commit()

    update.last_episode_watched = episode + 1
    db.session.commit()

    app.logger.info(
        '[{}] Episode of the serie with ID {} updated to {}'.format(current_user.get_id(), series_id, episode + 1))
    return '', 204


@app.route('/delete_serie', methods=['POST'])
@login_required
def delete_serie():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        series_id = json_data['delete']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        series_id = int(series_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Series.query.filter_by(id=series_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=series_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    SeriesList.query.filter_by(series_id=series_id, user_id=current_user.get_id()).delete()
    db.session.commit()

    SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), series_id=series_id).delete()
    db.session.commit()

    app.logger.info('[{}] Serie with ID {} deleted'.format(current_user.get_id(), series_id))
    return '', 204


@app.route('/change_series_category', methods=['POST'])
@login_required
def change_series_status():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        series_new_category = json_data['status']
        series_id = json_data['series_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    category_list = ["Watching", "Completed", "On Hold", "Random", "Dropped", "Plan to Watch"]
    if series_new_category not in category_list:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        series_id = int(series_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    serie = SeriesList.query.filter_by(series_id=series_id, user_id=current_user.get_id()).first()
    if series_new_category == 'Watching':
        serie.status = 'WATCHING'
    elif series_new_category == 'Completed':
        serie.status = 'COMPLETED'
        # Set Season / Episode to max
        number_season = SeriesEpisodesPerSeason.query.filter_by(series_id=series_id).count()
        for i in range(number_season):
            number_episode = SeriesEpisodesPerSeason.query.filter_by(series_id=series_id, season=i + 1).first().episodes
            for j in range(number_episode):
                if SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                          series_id=series_id,
                                                          season=i+1,
                                                          episode=j+1).first() is None:
                    ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                                series_id=series_id,
                                                season=i+1,
                                                episode=j+1,
                                                timestamp=datetime.utcnow())
                    db.session.add(ep)
        serie.current_season = number_season
        serie.last_episode_watched = number_episode
        db.session.commit()
    elif series_new_category == 'On Hold':
        serie.status = 'ON_HOLD'
    elif series_new_category == 'Random':
        serie.status = 'RANDOM'
    elif series_new_category == 'Dropped':
        serie.status = 'DROPPED'
    elif series_new_category == 'Plan to Watch':
        serie.status = 'PLAN_TO_WATCH'
    db.session.commit()
    app.logger.info('[{}] Category of the serie with ID {} changed to {}'.format(current_user.get_id(), series_id,
                                                                                 series_new_category))
    return '', 204


@app.route('/refresh_single_series', methods=['POST'])
@login_required
def refresh_single_serie():
    image_error = url_for('static', filename='img/error.jpg')

    try:
        json_data = request.get_json()
        series_id = json_data['series_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400


    # Check if the inputs are digits
    try:
        series_id = int(series_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is currently in the user's list
    if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=series_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if there is more than 30 min since the last update
    last_update = Series.query.filter_by(id=series_id).first().last_update
    time_delta = datetime.utcnow() - last_update
    if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
        refresh_element_data(series_id, ListType.SERIES)

    return '', 204


@app.route('/refresh_all_series', methods=['POST'])
@login_required
def refresh_all_series():
    series = SeriesList.query.filter_by(user_id=current_user.get_id()).all()
    for serie in series:
        # Check if there is more than 30 min since the last update
        last_update = Series.query.filter_by(id=serie.series_id).first().last_update
        time_delta = datetime.utcnow() - last_update
        if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
            refresh_element_data(serie.series_id, ListType.SERIES)
        else:
            pass
    return '', 204


@app.route("/user/series/<user_name>")
@login_required
def user_series_list(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404

    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('myserieslist'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()

    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))

    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    watching_list    = SeriesList.query.filter_by(user_id=user.id, status='WATCHING').all()
    completed_list   = SeriesList.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list      = SeriesList.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    random_list      = SeriesList.query.filter_by(user_id=user.id, status='RANDOM').all()
    dropped_list     = SeriesList.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantowatch_list = SeriesList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').all()

    series_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    series_data = get_list_data(series_list, ListType.SERIES)
    return render_template('user_series_list.html', title='{}\'s list'.format(user.username), all_data=series_data)


@app.route('/autocomplete_series2', methods=['GET'])
@login_required
def autocomplete_series2():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])
    query = db.session.query(Series.name).filter(Series.name.like(search + '%'))
    results = [mv[0] for mv in query.all()]
    results = sorted(results, key=str.lower)
    # Get only the first 8 matching results
    results = results[:8]
    return jsonify(matching_results=results)


@app.route('/autocomplete_series', methods=['GET'])
@login_required
def autocomplete_series():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])

    results = auto_element_on_themoviedb(search)
    return jsonify(matching_results=results)


##################################################### Anime routes #####################################################


@app.route("/myanimelist", methods=['GET', 'POST'])
@login_required
def myanimelist():
    form = SearchAnimeForm()
    if form.validate_on_submit():
        add_element(form.anime.data.strip(), ListType.ANIME)

    watching_list    = AnimeList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').all()
    completed_list   = AnimeList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list      = AnimeList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    random_list      = AnimeList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').all()
    dropped_list     = AnimeList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantowatch_list = AnimeList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').all()

    anime_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    anime_data = get_list_data(anime_list, ListType.ANIME)

    return render_template('myanimelist.html', title='MyAnimeList', form=form, all_data=anime_data)


@app.route('/update_anime_season', methods=['POST'])
@login_required
def update_anime_season():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        season = json_data['season']
        anime_id = json_data['anime_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        season = int(season)
        anime_id = int(anime_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the anime exists
    if Anime.query.filter_by(id=anime_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the anime is in the current user's list
    if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=anime_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the season number is between 1 and <last_season>
    last_season = AnimeEpisodesPerSeason.query.filter_by(anime_id=anime_id).order_by(
        AnimeEpisodesPerSeason.season.desc()).first().season
    if season + 1 < 1 or season + 1 > last_season:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    update = AnimeList.query.filter_by(anime_id=anime_id, user_id=current_user.get_id()).first()

    old_season = update.current_season

    if old_season < season + 1:
        for i in range(old_season, season + 1):
            for j in range(1, AnimeEpisodesPerSeason.query.filter_by(anime_id=anime_id,
                                                                     season=i).first().episodes + 1):
                if AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                         anime_id=anime_id,
                                                         season=i,
                                                         episode=j).first() is None:
                    ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                               anime_id=anime_id,
                                               season=i,
                                               episode=j,
                                               timestamp=datetime.utcnow())
                    db.session.add(ep)
        ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                   anime_id=anime_id,
                                   season=season + 1,
                                   episode=1,
                                   timestamp=datetime.utcnow())
        db.session.add(ep)
        db.session.commit()

    elif old_season > season + 1:
        for i in range(season + 1, old_season + 1):
            AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), anime_id=anime_id, season=i).delete()
        ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                   anime_id=anime_id,
                                   season=season + 1,
                                   episode=1,
                                   timestamp=datetime.utcnow())
        db.session.add(ep)
        db.session.commit()

    update.current_season = season + 1
    update.last_episode_watched = 1
    db.session.commit()
    app.logger.info('[{}] Season of the anime with ID {} updated to {}'.format(current_user.get_id(), anime_id, season + 1))
    return '', 204


@app.route('/update_anime_episode', methods=['POST'])
@login_required
def update_anime_episode():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        episode = json_data['episode']
        anime_id = json_data['anime_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        episode = int(episode)
        anime_id = int(anime_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the anime exists
    if Anime.query.filter_by(id=anime_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the anime is in the current user's list
    if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=anime_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the episode number is between 1 and <last_episode>
    current_season = AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=anime_id).first().current_season
    last_episode = AnimeEpisodesPerSeason.query.filter_by(anime_id=anime_id, season=current_season).first().episodes
    if episode + 1 < 1 or episode + 1 > last_episode:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    update = AnimeList.query.filter_by(anime_id=anime_id, user_id=current_user.get_id()).first()
    old_last_episode_watched = update.last_episode_watched
    current_season = update.current_season

    if episode + 1 > old_last_episode_watched:
        for i in range(old_last_episode_watched + 1, episode + 2):
            ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                       anime_id=anime_id,
                                       season=current_season,
                                       episode=i,
                                       timestamp=datetime.utcnow())
            db.session.add(ep)
        db.session.commit()
    elif episode + 1 < old_last_episode_watched:
        for i in range(episode + 2, old_last_episode_watched + 1):
            AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                  anime_id=anime_id,
                                                  season=current_season,
                                                  episode=i).delete()
        db.session.commit()

    update.last_episode_watched = episode + 1
    db.session.commit()

    app.logger.info(
        '[{}] Episode of the anime with ID {} updated to {}'.format(current_user.get_id(), anime_id, episode + 1))
    return '', 204


@app.route('/delete_anime', methods=['POST'])
@login_required
def delete_anime():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        anime_id = json_data['delete']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        anime_id = int(anime_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Anime.query.filter_by(id=anime_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=anime_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    AnimeList.query.filter_by(anime_id=anime_id, user_id=current_user.get_id()).delete()
    db.session.commit()

    AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), anime_id=anime_id).delete()
    db.session.commit()

    app.logger.info('[{}] Anime with ID {} deleted'.format(current_user.get_id(), anime_id))
    return '', 204


@app.route('/change_anime_category', methods=['POST'])
@login_required
def change_anime_category():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        anime_new_category = json_data['status']
        anime_id = json_data['anime_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    category_list = ["Watching", "Completed", "On Hold", "Random", "Dropped", "Plan to Watch"]
    if anime_new_category not in category_list:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        anime_id = int(anime_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    anime = AnimeList.query.filter_by(anime_id=anime_id, user_id=current_user.get_id()).first()
    if anime_new_category == 'Watching':
        anime.status = 'WATCHING'
    elif anime_new_category == 'Completed':
        anime.status = 'COMPLETED'
        # Set Season / Episode to max
        number_season = AnimeEpisodesPerSeason.query.filter_by(anime_id=anime_id).count()
        for i in range(number_season):
            number_episode = AnimeEpisodesPerSeason.query.filter_by(anime_id=anime_id, season=i + 1).first().episodes
            for j in range(number_episode):
                if AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                         anime_id=anime_id,
                                                         season=i+1,
                                                         episode=j+1).first() is None:
                    ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                                anime_id=anime_id,
                                                season=i+1,
                                                episode=j+1,
                                                timestamp=datetime.utcnow())
                    db.session.add(ep)
        anime.current_season = number_season
        anime.last_episode_watched = number_episode
        db.session.commit()
    elif anime_new_category == 'On Hold':
        anime.status = 'ON_HOLD'
    elif anime_new_category == 'Random':
        anime.status = 'RANDOM'
    elif anime_new_category == 'Dropped':
        anime.status = 'DROPPED'
    elif anime_new_category == 'Plan to Watch':
        anime.status = 'PLAN_TO_WATCH'
    db.session.commit()
    app.logger.info('[{}] Category of the anime with ID {} changed to {}'.format(current_user.get_id(),
                                                                                 anime_id,
                                                                                 anime_new_category))
    return '', 204


@app.route('/refresh_single_anime', methods=['POST'])
@login_required
def refresh_single_anime():
    image_error = url_for('static', filename='img/error.jpg')

    try:
        json_data = request.get_json()
        anime_id = json_data['anime_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        anime_id = int(anime_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the anime is currently in the user's list
    if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=anime_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if there is more than 30 min since the last update
    last_update = Anime.query.filter_by(id=anime_id).first().last_update
    time_delta = datetime.utcnow() - last_update
    if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
        refresh_element_data(anime_id, ListType.ANIME)
    return '', 204


@app.route('/refresh_all_animes', methods=['POST'])
@login_required
def refresh_all_animes():
    animes = AnimeList.query.filter_by(user_id=current_user.get_id()).all()
    for anime in animes:
        # Check if there is more than 30 min since the last update
        last_update = Anime.query.filter_by(id=anime.anime_id).first().last_update
        time_delta = datetime.utcnow() - last_update
        if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
            refresh_element_data(anime.anime_id, ListType.ANIME)
        else:
            pass
    return '', 204


@app.route("/user/anime/<user_name>")
@login_required
def user_anime(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404

    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('myanimelist'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()

    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))

    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    watching_list    = AnimeList.query.filter_by(user_id=user.id, status='WATCHING').all()
    completed_list   = AnimeList.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list      = AnimeList.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    random_list      = AnimeList.query.filter_by(user_id=user.id, status='RANDOM').all()
    dropped_list     = AnimeList.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantowatch_list = AnimeList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').all()

    anime_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    anime_data = get_list_data(anime_list, ListType.ANIME)
    return render_template('user_anime_list.html', title='{}\'s list'.format(user.username), all_data=anime_data)


@app.route('/autocomplete_anime2', methods=['GET'])
@login_required
def autocomplete_anime2():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])
    query = db.session.query(Anime.name).filter(Anime.name.like(search + '%'))
    results = [mv[0] for mv in query.all()]
    results = sorted(results, key=str.lower)
    # Get only the first 8 matching results
    results = results[:8]
    return jsonify(matching_results=results)


@app.route('/testducul', methods=['POST'])
@login_required
def testducul():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        anime_id = json_data['test']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    add_element_2(anime_id, ListType.ANIME)
    return '', 204


@app.route('/autocomplete_anime', methods=['GET'])
@login_required
def autocomplete_anime():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])

    results = auto_element_on_themoviedb(search)
    return jsonify(matching_results=results)


###################################################### Books Routes ####################################################


@app.route("/mybookslist", methods=['GET', 'POST'])
@login_required
def mybookslist():
    form = SearchBookForm()
    if form.validate_on_submit():
        add_book(form.book.data.strip())

    reading_list = BookList.query.filter_by(user_id=current_user.get_id(), status='READING').all()
    completed_list = BookList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list = BookList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    dropped_list = BookList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantoread_list = BookList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_READ').all()

    book_list = [reading_list, completed_list, onhold_list, dropped_list, plantoread_list]
    book_data = get_booklist_data(book_list)
    return render_template('mybookslist.html', title='MyBooksList', form=form, all_data=book_data)


@app.route('/delete_book', methods=['POST'])
@login_required
def delete_book():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        book_id = json_data['delete']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        book_id = int(book_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Book.query.filter_by(id=book_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if BookList.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    BookList.query.filter_by(book_id=book_id, user_id=current_user.get_id()).delete()
    db.session.commit()

    app.logger.info('[{}] Book with ID {} deleted'.format(current_user.get_id(), book_id))
    return '', 204


@app.route('/change_book_category', methods=['POST'])
@login_required
def change_book_category():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        book_new_category = json_data['status']
        book_id = json_data['book_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    category_list = ["Reading", "Completed", "On Hold", "Dropped", "Plan to Read"]
    if book_new_category not in category_list:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        book_id = int(book_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    book = BookList.query.filter_by(book_id=book_id, user_id=current_user.get_id()).first()
    if book_new_category == 'Reading':
        book.status = 'READING'
    elif book_new_category == 'Completed':
        book.status = 'COMPLETED'
    elif book_new_category == 'On Hold':
        book.status = 'ON_HOLD'
    elif book_new_category == 'Dropped':
        book.status = 'DROPPED'
    elif book_new_category == 'Plan to Read':
        book.status = 'PLAN_TO_READ'
    db.session.commit()
    app.logger.info('[{}] Category of the book with ID {} changed to {}'.format(current_user.get_id(),
                                                                                book_id,
                                                                                book_new_category))
    return '', 204


@app.route("/user/book/<user_name>")
@login_required
def user_book(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404

    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('myanimelist'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()

    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))

    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    reading_list     = BookList.query.filter_by(user_id=user.id, status='READING').all()
    completed_list   = BookList.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list      = BookList.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    dropped_list     = BookList.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantoread_list  = BookList.query.filter_by(user_id=user.id, status='PLAN_TO_READ').all()

    book_list = [reading_list, completed_list, onhold_list, dropped_list, plantoread_list]
    book_data = get_booklist_data(book_list)
    return render_template('user_book_list.html', title='{}\'s list'.format(user.username), all_data=book_data)


@app.route('/tata', methods=['POST'])
@login_required
def tata():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        book_id = json_data['test']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    add_book_2(book_id)
    return '', 204


@app.route('/autocomplete_book', methods=['GET'])
@login_required
def autocomplete_book():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])

    results = auto_book_on_google_API(search)
    return jsonify(matching_results=results)


@app.route('/autocomplete_book2', methods=['GET'])
@login_required
def autocomplete_book2():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])
    query = db.session.query(Book.title).filter(Book.title.like(search + '%'))
    results = [mv[0] for mv in query.all()]
    results = sorted(results, key=str.lower)
    # Get only the first 8 matching results
    results = results[:8]
    return jsonify(matching_results=results)


###################################################### OwnList Routes ##################################################


@app.route("/myownlist", methods=['GET', 'POST'])
@login_required
def myownlist():
    return render_template('myownlist.html', title='MyOwnList')


###################################################### Functions #######################################################


def add_element(element_name, element_type):
    if element_name == "":
        if element_type == ListType.SERIES:
            return redirect(url_for('myserieslist'))
        elif element_type == ListType.ANIME:
            return redirect(url_for('myanimelist'))

    # Check if the exact name exist in the database
    if element_type == ListType.SERIES:
        element = Series.query.filter_by(name=element_name).first()
    elif element_type == ListType.ANIME:
        element = Anime.query.filter_by(name=element_name).first()

    # If exact name, we know which one to add in the user's list
    if element is not None:
        # Check if the element is already in the current's user list
        if element_type == ListType.SERIES:
            if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element.id).first() is not None:
                return flash("This series is already in your list", "warning")

        elif element_type == ListType.ANIME:
            if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element.id).first() is not None:
                return flash("This anime is already in your list", "warning")

        # Check if there is more than 30 min since the last update
        last_update = element.last_update
        time_delta = datetime.utcnow() - last_update
        if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
            refresh_element_data(element.id, element_type)
        else:
            pass

        add_element_to_user(element.id, int(current_user.get_id()), element_type)

    # Otherwise we need to search online
    else:
        result_id = 0
        while True:
            themoviedb_id = search_element_on_themoviedb(element_name, result_id)
            result_id += 1
            if themoviedb_id is None:
                return flash("Not found", "warning")
            else:
                # Keep looking online
                if element_type == ListType.SERIES:
                    if Series.query.filter_by(themoviedb_id=themoviedb_id).first() is not None:
                        continue
                    # We got a match, add the series in the base
                    else:
                        series_data = get_element_data_from_api(themoviedb_id)
                        if series_data is None:
                            return flash("There was a problem while getting series' info. Please try again later.",
                                         "warning")

                        cover_id = save_themoviedb_cover(series_data["poster_path"], ListType.SERIES)
                        if cover_id is None:
                            return flash("There was a problem while getting series' poster. Please try again later.",
                                         "warning")

                        series_id = add_element_in_base(series_data, cover_id, ListType.SERIES)
                        add_element_to_user(series_id, int(current_user.get_id()), element_type)
                        return redirect(url_for('myserieslist'))

                elif element_type == ListType.ANIME:
                    if Anime.query.filter_by(themoviedb_id=themoviedb_id).first() is not None:
                        continue
                    # We got a match, add the series in the base
                    else:
                        anime_data = get_element_data_from_api(themoviedb_id)
                        if anime_data is None:
                            return flash("There was a problem while getting series' info. Please try again later.",
                                         "warning")

                        cover_id = save_themoviedb_cover(anime_data["poster_path"], ListType.ANIME)
                        if cover_id is None:
                            return flash("There was a problem while getting series' poster. Please try again later.",
                                         "warning")

                        anime_id = add_element_in_base(anime_data, cover_id, element_type)
                        add_element_to_user(anime_id, int(current_user.get_id()), element_type)
                        return redirect(url_for('myanimelist'))


def search_element_on_themoviedb(element_name, result=0):
    while True:
        try:
            response = requests.get(
                "https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}".format(themoviedb_api_key, element_name))
        except:
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
            return None

        app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

        if response.headers["X-RateLimit-Remaining"] == "0":
            app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
            time.sleep(3)
            continue
        else:
            break

    data = json.loads(response.text)
    if data["total_results"] == 0 or result+1 > data["total_results"] or result > 19:
        return None
    return data["results"][result]["id"]


def get_element_data_from_api(themoviedb_id):
    try:
        response = requests.get(
            "https://api.themoviedb.org/3/tv/{0}?api_key={1}".format(themoviedb_id, themoviedb_api_key))
    except:
        return None

    if response.status_code == 401:
        app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
        return None

    app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

    if response.headers["X-RateLimit-Remaining"] == "0":
        app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
        time.sleep(3)
        get_element_data_from_api(themoviedb_id)
    else:
        pass
    return json.loads(response.text)


def save_themoviedb_cover(cover_path, list_type):
    if cover_path is None:
        return "default.jpg"
    cover_id = "{}.jpg".format(secrets.token_hex(8))
    if list_type == ListType.SERIES:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\series_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/series_covers/")
    elif list_type == ListType.ANIME:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\\anime_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/anime_covers/")
    else:
        print("TODO")
    try:
        urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{0}".format(cover_path),
                                   "{}{}".format(local_covers_path, cover_id))
    except:
        return None

    img = Image.open("{}{}".format(local_covers_path, cover_id))
    img = img.resize((300, 450), Image.ANTIALIAS)
    img.save("{}{}".format(local_covers_path, cover_id), quality=90)
    return cover_id


def add_element_in_base(element_data, element_cover_id, element_type):
    if element_type == ListType.SERIES:
        element = Series.query.filter_by(themoviedb_id=element_data["id"]).first()
    elif element_type == ListType.ANIME:
        element = Anime.query.filter_by(themoviedb_id=element_data["id"]).first()

    if element is not None:
        return element.id

    name = element_data["name"]
    original_name = element_data["original_name"]
    first_air_date = element_data["first_air_date"]
    last_air_date = element_data["last_air_date"]
    homepage = element_data["homepage"]
    in_production = element_data["in_production"]
    total_seasons = element_data["number_of_seasons"]
    total_episodes = element_data["number_of_episodes"]
    status = element_data["status"]
    vote_average = element_data["vote_average"]
    vote_count = element_data["vote_count"]
    synopsis = element_data["overview"]
    popularity = element_data["popularity"]
    themoviedb_id = element_data["id"]

    try:
        created_by = ""
        for person in element_data["created_by"]:
            created_by = created_by + person["name"] + ", "
        if len(element_data["created_by"]) > 0:
            created_by = created_by[:-2]
        else:
            created_by = None
    except:
        created_by = None

    try:
        episode_duration = element_data["episode_run_time"][0]
    except:
        episode_duration = None

    try:
        origin_country = ""
        for country in element_data["origin_country"]:
            origin_country = origin_country + country + ", "
        if len(element_data["origin_country"]) > 0:
            origin_country = origin_country[:-2]
        else:
            origin_country = None
    except:
        origin_country = None

    # Check if there is a special season
    # We do not want to take it into account
    seasons_data = []
    if len(element_data["seasons"]) == 0:
        return None

    if element_data["seasons"][0]["season_number"] == 0:  # Special season
        for i in range(len(element_data["seasons"])):
            try:
                seasons_data.append(element_data["seasons"][i + 1])
            except:
                pass
    else:
        for i in range(len(element_data["seasons"])):
            try:
                seasons_data.append(element_data["seasons"][i])
            except:
                pass

    genres_data = []
    for i in range(len(element_data["genres"])):
        try:
            genres_data.append(element_data["genres"][i]["name"])
        except:
            pass

    networks_data = []
    for i in range(len(element_data["networks"])):
        try:
            networks_data.append(element_data["networks"][i]["name"])
        except:
            pass

    # Add the element into the table
    if element_type == ListType.SERIES:
        element = Series(name=name,
                         original_name=original_name,
                         image_cover=element_cover_id,
                         first_air_date=first_air_date,
                         last_air_date=last_air_date,
                         homepage=homepage,
                         in_production=in_production,
                         created_by=created_by,
                         total_seasons=total_seasons,
                         total_episodes=total_episodes,
                         episode_duration=episode_duration,
                         origin_country=origin_country,
                         status=status,
                         vote_average=vote_average,
                         vote_count=vote_count,
                         synopsis=synopsis,
                         popularity=popularity,
                         themoviedb_id=themoviedb_id,
                         last_update=datetime.utcnow())
    elif element_type == ListType.ANIME:
        element = Anime(name=name,
                        original_name=original_name,
                        image_cover=element_cover_id,
                        first_air_date=first_air_date,
                        last_air_date=last_air_date,
                        homepage=homepage,
                        in_production=in_production,
                        created_by=created_by,
                        total_seasons=total_seasons,
                        total_episodes=total_episodes,
                        episode_duration=episode_duration,
                        origin_country=origin_country,
                        status=status,
                        vote_average=vote_average,
                        vote_count=vote_count,
                        synopsis=synopsis,
                        popularity=popularity,
                        themoviedb_id=themoviedb_id,
                        last_update=datetime.utcnow())

    db.session.add(element)
    db.session.commit()

    # Add genres
    for genre_data in genres_data:
        if element_type == ListType.SERIES:
            genre = SeriesGenre(series_id=element.id,
                                genre=genre_data)
        elif element_type == ListType.ANIME:
            genre = AnimeGenre(anime_id=element.id,
                               genre=genre_data)
        db.session.add(genre)

    # Add the different networks for each serie
    for network_data in networks_data:
        if element_type == ListType.SERIES:
            networks = SeriesNetwork(series_id=element.id,
                                     network=network_data)
        elif element_type == ListType.ANIME:
            networks = AnimeNetwork(anime_id=element.id,
                                    network=network_data)
        db.session.add(networks)

    # Add number of episodes for each season
    for season_data in seasons_data:
        if element_type == ListType.SERIES:
            season = SeriesEpisodesPerSeason(series_id=element.id,
                                             season=season_data["season_number"],
                                             episodes=season_data["episode_count"])
        elif element_type == ListType.ANIME:
            season = AnimeEpisodesPerSeason(anime_id=element.id,
                                            season=season_data["season_number"],
                                            episodes=season_data["episode_count"])
        db.session.add(season)

    db.session.commit()
    return element.id


def add_element_to_user(element_id, user_id, element_type):
    if element_type == ListType.SERIES:
        user_list = SeriesList(user_id=user_id,
                               series_id=element_id,
                               current_season=1,
                               last_episode_watched=1,
                               status=Status.WATCHING)

        data = SeriesEpisodeTimestamp(user_id=user_id,
                                      series_id=element_id,
                                      season=1,
                                      episode=1,
                                      timestamp=datetime.utcnow())

        app.logger.info('[{}] Added series with the ID {}'.format(user_id, element_id))

    elif element_type == ListType.ANIME:
        user_list = AnimeList(user_id=user_id,
                              anime_id=element_id,
                              current_season=1,
                              last_episode_watched=1,
                              status=Status.WATCHING)

        data = AnimeEpisodeTimestamp(user_id=user_id,
                                     anime_id=element_id,
                                     season=1,
                                     episode=1,
                                     timestamp=datetime.utcnow())

        app.logger.info('[{}] Added anime with the ID {}'.format(user_id, element_id))

    db.session.add(user_list)
    db.session.add(data)
    db.session.commit()


def get_list_data(list, list_type):
    all_list_data = []
    for category in list:
        category_series_data = []
        for element in category:
            current_element = {}
            # Cover of the element and its name
            if list_type == ListType.SERIES:
                element_data = Series.query.filter_by(id=element.series_id).first()
                cover_url = url_for('static', filename="series_covers/{}".format(element_data.image_cover))
            elif list_type == ListType.ANIME:
                element_data = Anime.query.filter_by(id=element.anime_id).first()
                cover_url = url_for('static', filename="anime_covers/{}".format(element_data.image_cover))

            current_element["cover_url"] = cover_url

            # Element meta data
            current_element["name"] = element_data.name
            current_element["original_name"] = element_data.original_name
            current_element["id"] = element_data.id
            current_element["first_air_date"] = element_data.first_air_date
            current_element["last_air_date"] = element_data.last_air_date
            current_element["homepage"] = element_data.homepage
            current_element["in_production"] = element_data.in_production
            current_element["created_by"] = element_data.created_by
            current_element["episode_duration"] = element_data.episode_duration
            current_element["total_seasons"] = element_data.total_seasons
            current_element["total_episodes"] = element_data.total_episodes
            current_element["origin_country"] = element_data.origin_country
            current_element["status"] = element_data.status
            current_element["synopsis"] = element_data.synopsis

            # Can update
            time_delta = datetime.utcnow() - element_data.last_update
            if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
                current_element["can_update"] = True
            else:
                current_element["can_update"] = False

            # Number of season and the number of ep of each season
            if list_type == ListType.SERIES:
                episodesperseason = SeriesEpisodesPerSeason.query.filter_by(series_id=element_data.id).order_by(SeriesEpisodesPerSeason.season.asc()).all()
            elif list_type == ListType.ANIME:
                episodesperseason = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_data.id).order_by(AnimeEpisodesPerSeason.season.asc()).all()
            tmp = []
            for season in episodesperseason:
                tmp.append(season.episodes)
            current_element["season_data"] = tmp

            current_element["current_season"] = element.current_season
            current_element["last_episode_watched"] = element.last_episode_watched

            category_series_data.append(current_element)
        category_series_data = sorted(category_series_data, key=lambda i: (i['name']))
        all_list_data.append(category_series_data)
    return all_list_data


def get_list_count(list_type):
    if list_type is ListType.SERIES:
        watching    = SeriesList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').count()
        completed   = SeriesList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').count()
        onhold      = SeriesList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').count()
        random      = SeriesList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').count()
        dropped     = SeriesList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').count()
        plantowatch = SeriesList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').count()
    elif list_type is ListType.ANIME:
        watching    = AnimeList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').count()
        completed   = AnimeList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').count()
        onhold      = AnimeList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').count()
        random      = AnimeList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').count()
        dropped     = AnimeList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').count()
        plantowatch = AnimeList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').count()
    else:
        print("TODO")

    statistics = [watching, completed, onhold, random, dropped, plantowatch]
    return statistics


def get_total_time_spent(user_id, list_type):
    if list_type == ListType.SERIES:
        list = SeriesList.query.filter(SeriesList.status != "PLAN_TO_WATCH").filter_by(user_id=user_id).all()
    elif list_type == ListType.ANIME:
        list = AnimeList.query.filter(AnimeList.status != "PLAN_TO_WATCH").filter_by(user_id=user_id).all()

    episodes_counter = 0
    time_spent_min = 0

    for element in list:
        if list_type == ListType.SERIES:
            episode_duration = Series.query.filter_by(id=element.series_id).first().episode_duration
        elif list_type == ListType.ANIME:
            episode_duration = Anime.query.filter_by(id=element.anime_id).first().episode_duration

        if episode_duration is None:
            continue

        current_season = element.current_season
        current_ep = element.last_episode_watched

        for i in range(1, current_season):
            if list_type == ListType.SERIES:
                ep = SeriesEpisodesPerSeason.query.filter_by(series_id=element.series_id, season=i).first().episodes
            elif list_type == ListType.ANIME:
                ep = AnimeEpisodesPerSeason.query.filter_by(anime_id=element.anime_id, season=i).first().episodes
            episodes_counter += ep
            time_spent_min += ep * episode_duration

        episodes_counter += current_ep
        time_spent_min += current_ep * episode_duration

    time_spent_hours = round(time_spent_min/60, 1)
    time_spent_days = round(time_spent_min/(60*24), 1)

    return [episodes_counter, time_spent_hours, time_spent_days]


def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    try:
        i = Image.open(form_picture)
    except:
        return "default.jpg"
    i = i.resize((300, 300), Image.ANTIALIAS)
    i.save(picture_path, quality=90)
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\emails\\password_reset.html")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/emails/password_reset.html")

    email_template = open(path, 'r').read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('reset_token', token=token, _external=True))

    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised when sending reset email to user with the ID {} : {}'.format(user.id, e))
        return False


def send_register_email(user):
    token = user.get_register_token()
    msg = Message(subject='MyLists Register Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\emails\\register.html")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/emails/register.html")

    email_template = open(path, 'r').read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('register_token', token=token, _external=True))

    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised when sending register email to user with the ID {} : {}'.format(user.id, e))
        return False


def send_email_update_email(user):
    token = user.get_email_update_token()
    msg = Message(subject='MySerieList Email Update Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\emails\\email_update.html")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/emails/email_update.html")

    email_template = open(path, 'r').read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('email_update_token', token=token, _external=True))

    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised when sending email update email to user with the ID {} : {}'.format(user.id, e))
        return False


def add_friend(friend_username):
    friend_to_add = User.query.filter_by(username=friend_username).first()
    if friend_to_add is None or friend_to_add.id == 1:
        app.logger.info('[{}] Attempt of adding user {} as friend'.format(current_user.get_id(), friend_username))
        return flash('Sorry, no user with this username', 'info')

    else:
        friends = Friend.query.filter_by(user_id=current_user.get_id()).all()

        for friend in friends:
            if friend_to_add.id == friend.friend_id:
                return flash('Username already in your friend list', 'info')

        add_user = Friend(user_id=current_user.get_id(), friend_id=friend_to_add.id, status="request")
        db.session.add(add_user)
        db.session.commit()

        add_user_2 = Friend(user_id=friend_to_add.id, friend_id=current_user.get_id(), status="pending")
        db.session.add(add_user_2)
        db.session.commit()

        app.logger.info('[{}] Friend request sent to user with ID {}'.format(current_user.get_id(), friend_to_add.id))
        flash("Your friend request has been sent.", 'success')


def refresh_element_data(element_id, element_type):
    if element_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
    elif element_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()

    element_data = get_element_data_from_api(element.themoviedb_id)

    if element_data is None:
        return flash("There was an error while refreshing. Please try again later.")

    name            = element_data["name"]
    original_name   = element_data["original_name"]
    first_air_date  = element_data["first_air_date"]
    last_air_date   = element_data["last_air_date"]
    homepage        = element_data["homepage"]
    in_production   = element_data["in_production"]
    total_seasons   = element_data["number_of_seasons"]
    total_episodes  = element_data["number_of_episodes"]
    status          = element_data["status"]
    vote_average    = element_data["vote_average"]
    vote_count      = element_data["vote_count"]
    synopsis        = element_data["overview"]
    popularity      = element_data["popularity"]
    element_poster  = element_data["poster_path"]

    if element_type == ListType.SERIES:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\series_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/series_covers/")
    elif element_type == ListType.ANIME:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\\anime_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/anime_covers/")

    try:
        urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{0}".format(element_poster),
                                   "{}{}".format(local_covers_path, element.image_cover))
    except:
        return flash("There was an error while refreshing. Please try again later.")

    img = Image.open(local_covers_path + element.image_cover)
    img = img.resize((300, 450), Image.ANTIALIAS)
    img.save(local_covers_path + element.image_cover, quality=90)

    try:
        created_by = ""
        for person in element_data["created_by"]:
            created_by = created_by + person["name"] + ", "
        if len(element_data["created_by"]) > 0:
            created_by = created_by[:-2]
        else:
            created_by = None
    except:
        created_by = None

    try:
        episode_duration = element_data["episode_run_time"][0]
    except:
        episode_duration = None

    try:
        origin_country = ""
        for country in element_data["origin_country"]:
            origin_country = origin_country + country + ", "
        if len(element_data["origin_country"]) > 0:
            origin_country = origin_country[:-2]
        else:
            origin_country = None
    except:
        origin_country = None

    # Check if there is a special season
    # We do not want to take it into account
    seasons_data = []
    if element_data["seasons"][0]["season_number"] == 0:  # Special season
        for i in range(len(element_data["seasons"])):
            try:
                seasons_data.append(element_data["seasons"][i + 1])
            except:
                pass
    else:
        for i in range(len(element_data["seasons"])):
            try:
                seasons_data.append(element_data["seasons"][i])
            except:
                pass

    # Genres
    genres_data = []
    for i in range(len(element_data["genres"])):
        genres_data.append(element_data["genres"][i])

    # Networks
    networks_data = []
    for i in range(len(element_data["networks"])):
        networks_data.append(element_data["networks"][i])

    # Update the element
    element.name                = name
    element.original_name       = original_name
    element.first_air_date      = first_air_date
    element.last_air_date       = last_air_date
    element.homepage            = homepage
    element.in_production       = in_production
    element.created_by          = created_by
    element.total_seasons       = total_seasons
    element.total_episodes      = total_episodes
    element.episode_duration    = episode_duration
    element.origin_country      = origin_country
    element.status              = status
    element.vote_average        = vote_average
    element.vote_count          = vote_count
    element.synopsis            = synopsis
    element.popularity          = popularity
    element.last_update         = datetime.utcnow()

    # Update the number of seasons and episodes
    for season_data in seasons_data:
        if element_type == ListType.SERIES:
            season = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id, season=season_data["season_number"]).first()
            if season is None:
                season = SeriesEpisodesPerSeason(series_id=element.id,
                                                 season=season_data["season_number"],
                                                 episodes=season_data["episode_count"])
                db.session.add(season)
            else:
                season.episodes = season_data["episode_count"]
        elif element_type == ListType.ANIME:
            season = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id,
                                                            season=season_data["season_number"]).first()
            if season is None:
                season = AnimeEpisodesPerSeason(anime_id=element.id,
                                                season=season_data["season_number"],
                                                episodes=season_data["episode_count"])
                db.session.add(season)
            else:
                season.episodes = season_data["episode_count"]

    # TODO : refresh Networks and Genres
    db.session.commit()
    app.logger.info("[{}] Refreshed the element with the ID {}".format(current_user.get_id(), element_id))


def auto_element_on_themoviedb(element_name):

    anime = Anime.query.









    try:
        response = requests.get("https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}"
                                .format(themoviedb_api_key, element_name))
    except:
        return None

    if response.status_code == 401:
        app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
        return None

    app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

    if response.headers["X-RateLimit-Remaining"] == "0":
        app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
        time.sleep(3)
    else:
        pass

    data = json.loads(response.text)

    if data["total_results"] == 0:
        return ["Sorry, No Results Found..."]

    else:
        i = 0
        results = []
        for i in range(6):
            try:
                tmp = {"id": "{0}".format(data['results'][i]['id']),
                       "value": "{0}".format(data["results"][i]["name"]),
                       "label": "<a class='list-group-item'><img src='http://image.tmdb.org/t/p/w300/{0}' alt='{1}' style='width: 30px; height: 50px;'> {2}</a>"
                           .format(data["results"][i]["poster_path"],
                                   data["results"][i]["name"],
                                   data["results"][i]["name"])}
                results.append(tmp)
            except:
                pass
    return results


###################################################### CRAWL TEST ######################################################


def crawl_tmdb():
    import time
    start_time = time.time()

    for i in range(1, 501):

        response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}".format(i, themoviedb_api_key))
        print(response.headers["X-RateLimit-Remaining"])

        if response.status_code == 200:
            series_data = json.loads(response.text)
            print("Serie ID {} : OK".format(i))
        else:
            print("Serie ID {} : NON OK".format(i))
            continue

        if series_data["poster_path"] is not None:
            cover_id = save_themoviedb_cover(series_data["poster_path"], ListType.SERIES)
            add_element_in_base(series_data, cover_id, ListType.SERIES)
        else:
            add_element_in_base(series_data, "default.jpg", ListType.SERIES)

    print("--- %s seconds ---" % (time.time() - start_time))


###################################################### BOOK TEST #######################################################


def add_book(book_name):
    if book_name == "":
        return redirect(url_for('mybookslist'))

    book = Book.query.filter_by(title=book_name).first()

    # If exact name, we know which one to add in the user's list
    if book is not None:
        # Check if the book is already in the current's user list
        if BookList.query.filter_by(user_id=current_user.get_id(), book_id=book.id).first() is not None:
            return flash("This book is already in your list", "warning")

        add_book_to_user(book.id, int(current_user.get_id()))

    # Otherwise we need to search online
    else:
        id_link = search_book_on_google_API(book_name)
        book_data = get_book_data_from_api(id_link)
        cover_link = book_data["volumeInfo"]["imageLinks"]["small"]
        cover_id = save_google_cover(cover_link)
        book_id = add_book_in_base(book_data, cover_id)
        add_book_to_user(book_id, int(current_user.get_id()))
        return redirect(url_for('mybookslist'))


def add_book_2(book_id):

    book = Book.query.filter_by(google_id=book_id).first()

    # If exact google_id, we know which one to add in the user's list
    if book is not None:
        # Check if the book is already in the current's user list
        if BookList.query.filter_by(user_id=current_user.get_id(), book_id=book.id).first() is not None:
            return flash("This book is already in your list", "warning")

        add_book_to_user(book.id, int(current_user.get_id()))

    # Otherwise we need to search online
    else:
        id_link = requests.get("https://www.googleapis.com/books/v1/volumes/{0}".format(book_id))
        book_data = json.loads(id_link.text)
        cover_link = book_data["volumeInfo"]["imageLinks"]["small"]
        cover_id = save_google_cover(cover_link)
        book_id = add_book_in_base(book_data, cover_id)
        add_book_to_user(book_id, int(current_user.get_id()))
        return redirect(url_for('mybookslist'))


def add_element_2(element_id, element_type):

    # Check if the exact ID exist in the database
    if element_type == ListType.SERIES:
        element = Series.query.filter_by(themoviedb_id=element_id).first()
    elif element_type == ListType.ANIME:
        element = Anime.query.filter_by(themoviedb_id=element_id).first()

    # If exact ID, we know which one to add in the user's list
    if element is not None:
        # Check if the element is already in the current's user list
        if element_type == ListType.SERIES:
            if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element.id).first() is not None:
                return flash("This series is already in your list", "warning")

        elif element_type == ListType.ANIME:
            if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element.id).first() is not None:
                return flash("This anime is already in your list", "warning")

        # Check if there is more than 30 min since the last update
        last_update = element.last_update
        time_delta = datetime.utcnow() - last_update
        if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
            refresh_element_data(element.id, element_type)
        else:
            pass

        add_element_to_user(element.id, int(current_user.get_id()), element_type)

    # Otherwise we need to search online
    else:
        if element_type == ListType.SERIES:
            series_data = get_element_data_from_api(element_id)
            if series_data is None:
                return flash("There was a problem while getting series' info. Please try again later.",
                             "warning")

            cover_id = save_themoviedb_cover(series_data["poster_path"], ListType.SERIES)
            if cover_id is None:
                return flash("There was a problem while getting series' poster. Please try again later.",
                             "warning")

            series_id = add_element_in_base(series_data, cover_id, ListType.SERIES)
            add_element_to_user(series_id, int(current_user.get_id()), element_type)
            return redirect(url_for('myserieslist'))

        elif element_type == ListType.ANIME:
            anime_data = get_element_data_from_api(element_id)
            if anime_data is None:
                return flash("There was a problem while getting series' info. Please try again later.",
                             "warning")

            cover_id = save_themoviedb_cover(anime_data["poster_path"], ListType.ANIME)
            if cover_id is None:
                return flash("There was a problem while getting series' poster. Please try again later.",
                             "warning")

            anime_id = add_element_in_base(anime_data, cover_id, element_type)
            add_element_to_user(anime_id, int(current_user.get_id()), element_type)
            return redirect(url_for('myanimelist'))


def add_book_to_user(book_id, user_id):
    user_list = BookList(user_id=user_id,
                         book_id=book_id,
                         commentary=None,
                         read_year=None,
                         status=Status_book.READING)

    app.logger.info('[{}] Added book with the ID {}'.format(user_id, book_id))
    db.session.add(user_list)
    db.session.commit()


def search_book_on_google_API(book_name):
    try:
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q={0}".format(book_name))
    except:
        return None

    if response.status_code == 401:
        app.logger.error('[SYSTEM] Error requesting google API :(')
        return None

    data = json.loads(response.text)
    return data["items"][0]["selfLink"]


def get_book_data_from_api(id_link):
    try:
        response = requests.get("{0}".format(id_link))
    except:
        return None

    if response.status_code == 401:
        app.logger.error('[SYSTEM] Error requesting google API :(')
        return None

    return json.loads(response.text)


def save_google_cover(cover_link):
    if cover_link is None:
        return "default.jpg"
    cover_id = "{}.jpg".format(secrets.token_hex(8))

    if platform.system() == "Windows":
        local_covers_path = os.path.join(app.root_path, "static\\books_covers\\")
    else:  # Linux & macOS
        local_covers_path = os.path.join(app.root_path, "static/books_covers/")

    try:
        urllib.request.urlretrieve("{0}".format(cover_link), "{0}{1}".format(local_covers_path, cover_id))
    except:
        return None

    img = Image.open("{0}{1}".format(local_covers_path, cover_id))
    img = img.resize((300, 450), Image.ANTIALIAS)
    img.save("{0}{1}".format(local_covers_path, cover_id), quality=90)
    return cover_id


def add_book_in_base(book_data, cover_id):
    book = Book.query.filter_by(google_id=book_data["id"]).first()

    if book is not None:
        return book.id

    title = book_data["volumeInfo"]["title"]
    authors = book_data["volumeInfo"]["authors"][0]
    published_date = book_data["volumeInfo"]["publishedDate"]
    try:
        published_date = published_date[0:4]
    except:
        pass
    description = book_data["volumeInfo"]["description"]
    try:
        description = description[0:100]
    except:
        pass
    page_count = book_data["volumeInfo"]["pageCount"]
    categories = book_data["volumeInfo"]["categories"][0]
    google_id = book_data["id"]

    # Add the element into the table
    add_book = Book(title=title,
                      authors=authors,
                      image_cover=cover_id,
                      published_date=published_date,
                      description=description,
                      page_count=page_count,
                      categories=categories,
                      google_id=google_id)

    db.session.add(add_book)
    db.session.commit()
    return add_book.id


def get_booklist_data(list):
    all_list_data = []
    for category in list:
        category_books_data = []
        for element in category:
            current_element = {}
            # Cover of the element and its name
            element_data = Book.query.filter_by(id=element.book_id).first()
            cover_url = url_for('static', filename="books_covers/{}".format(element_data.image_cover))

            current_element["cover_url"] = cover_url

            published_date = db.Column(db.String(150), nullable=False)
            description = db.Column(db.String(5000), nullable=False)
            page_count = db.Column(db.Integer, nullable=False)
            categories = db.Column(db.String(150), nullable=False)

            # Element meta data
            current_element["title"] = element_data.title
            current_element["authors"] = element_data.authors
            current_element["id"] = element_data.id
            current_element["published_date"] = element_data.published_date
            current_element["description"] = element_data.description
            current_element["page_count"] = element_data.page_count
            current_element["categories"] = element_data.categories

            category_books_data.append(current_element)
        category_books_data = sorted(category_books_data, key=lambda i: (i['title']))
        all_list_data.append(category_books_data)
    return all_list_data


def auto_book_on_google_API(book_name):
    try:
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q={0}".format(book_name))
    except:
        return None

    if response.status_code == 401:
        app.logger.error('[SYSTEM] Error requesting google API :(')
        return None

    data = json.loads(response.text)
    i = 0
    results = []
    for i in range(6):
        try:
            tmp = {"id": "{0}".format(data['items'][i]['id']),
                   "value": "{0}".format(data["items"][i]["volumeInfo"]['title']),
                   "label": "<a class='list-group-item'><img src='{0}' alt='{1}' style='width: 30px; height: 50px;'> {2}</a>"
                       .format(data["items"][i]["volumeInfo"]['imageLinks']['smallThumbnail'],
                               data["items"][i]["volumeInfo"]['title'],
                               data["items"][i]["volumeInfo"]['title'])}
            results.append(tmp)
        except:
            pass
    return results



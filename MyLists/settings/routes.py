from MyLists import db, app, bcrypt
from MyLists.models import HomePage, User
from flask_login import login_required, current_user
from flask import Blueprint, flash, request, render_template, redirect, url_for
from MyLists.settings.functions import send_email_update_email, save_profile_picture
from MyLists.settings.forms import UpdateAccountForm, ChangePasswordForm, UpdateAccountOauthForm


bp = Blueprint('settings', __name__)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.oauth_id:
        settings_form = UpdateAccountOauthForm()

        if settings_form.submit_account.data and settings_form.validate():
            if settings_form.picture.data:
                old_picture_file = current_user.image_file
                current_user.image_file = save_profile_picture(settings_form.picture.data, old_picture_file)
                app.logger.info('[{}] Settings updated: Old picture file = {}. New picture file = {}'
                                .format(current_user.id, old_picture_file, current_user.image_file))
            if settings_form.username.data != current_user.username:
                old_username = current_user.username
                current_user.username = settings_form.username.data
                app.logger.info('[{}] Settings updated: Old username = {}. New username = {}'
                                .format(current_user.id, old_username, current_user.username))
            if settings_form.isprivate.data != current_user.private:
                old_value = current_user.private
                current_user.private = settings_form.isprivate.data
                app.logger.info('[{}] Settings updated: Old private mode = {}. New private mode = {}'
                                .format(current_user.id, old_value, settings_form.isprivate.data))

            old_homepage = current_user.homepage
            current_user.homepage = HomePage(settings_form.homepage.data)
            app.logger.info('[{}] Settings updated: Old homepage = {}. New homepage = {}'
                            .format(current_user.id, old_homepage, HomePage(settings_form.homepage.data)))
            db.session.commit()
            flash("Your settings has been updated!", 'success')
        elif request.method == 'GET':
            settings_form.username.data = current_user.username
            settings_form.isprivate.data = current_user.private
            settings_form.homepage.data = current_user.homepage.value

        return render_template('settings.html',
                               title='Your settings',
                               settings_form=settings_form)
    else:
        settings_form = UpdateAccountForm()
        password_form = ChangePasswordForm()

        if settings_form.submit_account.data and settings_form.validate():
            if settings_form.picture.data:
                old_picture_file = current_user.image_file
                current_user.image_file = save_profile_picture(settings_form.picture.data, old_picture_file)
                app.logger.info('[{}] Settings updated: Old picture file = {}. New picture file = {}'
                                .format(current_user.id, old_picture_file, current_user.image_file))
            if settings_form.username.data != current_user.username:
                old_username = current_user.username
                current_user.username = settings_form.username.data
                app.logger.info('[{}] Settings updated: Old username = {}. New username = {}'
                                .format(current_user.id, old_username, current_user.username))
            if settings_form.isprivate.data != current_user.private:
                old_value = current_user.private
                current_user.private = settings_form.isprivate.data
                app.logger.info('[{}] Settings updated: Old private mode = {}. New private mode = {}'
                                .format(current_user.id, old_value, settings_form.isprivate.data))

            old_homepage = current_user.homepage
            current_user.homepage = HomePage(settings_form.homepage.data)
            app.logger.info('[{}] Settings updated: Old homepage = {}. New homepage = {}'
                            .format(current_user.id, old_homepage, HomePage(settings_form.homepage.data)))

            if settings_form.email.data != current_user.email:
                old_email = current_user.email
                current_user.transition_email = settings_form.email.data
                app.logger.info('[{}] Settings updated : Old email = {}. New email = {}'
                                .format(current_user.id, old_email, current_user.transition_email))
                try:
                    send_email_update_email(current_user)
                    flash("Your account has been updated! Please click on the link to validate your new email address.",
                          'success')
                except Exception as e:
                    flash("There was an error. Please contact an administrator.", 'danger')
                    app.logger.error('[SYSTEM] Error: {}. Sending the email update to {}'.format(e, current_user.email))
            else:
                flash("Your settings has been updated!", 'success')

            db.session.commit()
        elif request.method == 'GET':
            settings_form.username.data = current_user.username
            settings_form.email.data = current_user.email
            settings_form.isprivate.data = current_user.private
            settings_form.homepage.data = current_user.homepage.value

        if password_form.submit_password.data and password_form.validate():
            hashed_password = bcrypt.generate_password_hash(password_form.confirm_new_password.data).decode('utf-8')
            current_user.password = hashed_password

            db.session.commit()
            app.logger.info('[{}] Password updated'.format(current_user.id))
            flash('Your password has been successfully updated!', 'success')

    return render_template('settings.html',
                           title='Your settings',
                           settings_form=settings_form,
                           password_form=password_form)


@bp.route("/email_update/<token>", methods=['GET'])
@login_required
def email_update_token(token):
    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.home'))

    if user.id != current_user.id:
        return redirect(url_for('auth.home'))

    old_email = user.email
    user.email = user.transition_email
    user.transition_email = None

    db.session.commit()
    app.logger.info('[{}] Email successfully changed from {} to {}'.format(user.id, old_email, user.email))
    flash('Email successfully updated!', 'success')

    return redirect(url_for('auth.home'))

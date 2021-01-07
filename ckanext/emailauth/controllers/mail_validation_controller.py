import datetime
import json
import logging as logging
import re
import sys
import random
import string

import dateutil
from validate_email import validate_email

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic
import ckan.model as model
import ckanext.emailauth.helpers.tokens as tokens
import ckanext.emailauth.helpers.user_extra as ue_helpers
import ckanext.emailauth.logic.schema as user_reg_schema
import ckanext.emailauth.model as user_model
from ckanext.emailauth.controllers.mail import Mail
from ckanext.emailauth.settings import TEMPLATES
from ckan.common import _, c, request
from ckan.logic.validators import name_validator, name_match, PACKAGE_NAME_MAX_LENGTH
from ckanext.emailauth.authenticator import EmailAuthenticator
from ckanext.emailauth.settings import IS_FLASK_REQUEST, BASE_URL
import ckan.lib.mailer as mailer
from six import text_type

if sys.version_info[0] > 2:
    from urllib.parse import urljoin, quote
    from ckanext.emailauth.settings import UserController
    from flask import make_response
else:
    from urlparse import urljoin
    from urllib2 import quote
    from ckan.controllers.user import UserController
    from ckan.common import response

_validate = dictization_functions.validate
log = logging.getLogger(__name__)
render = base.render
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
abort = base.abort
check_access = logic.check_access
get_action = logic.get_action
NotFound = logic.NotFound
ValidationError = logic.ValidationError
DataError = dictization_functions.DataError
NotAuthorized = logic.NotAuthorized
unflatten = dictization_functions.unflatten

Invalid = df.Invalid


def name_validator_with_changed_msg(val, context):
    try:
        return name_validator(val, context)
    except Invalid as invalid:
        if val in ['new', 'edit', 'search']:
            raise Invalid(_('That name cannot be used'))

        if len(val) < 2:
            raise Invalid(_('Name must be at least %s characters long') % 2)
        if len(val) > PACKAGE_NAME_MAX_LENGTH:
            raise Invalid(_('Name must be a maximum of %i characters long') % \
                          PACKAGE_NAME_MAX_LENGTH)
        if not name_match.match(val):
            raise Invalid(_('Username should be lowercase letters and/or numbers and/or these symbols: -_'))

        raise invalid


class ValidationController(UserController):
    LoginFailedStatus = _('Login failed. Bad username or password.')
    NotAuthorizedStatus = json.dumps({'success': False, 'error': {'message': _('Unauthorized to create user')}})
    UserNotFoundStatus = json.dumps({'success': False, 'error': {'message': 'User not found'}})
    ExistingUsernameStatus = json.dumps({'success': False, 'error': {'message': 'Username is already used'}})
    ExistingEmailStatus = json.dumps({'success': False, 'error': {'message': 'Email is already in use'}})
    TokenNotFoundStatus = json.dumps({'success': False, 'error': {'message': 'Token not found'}})
    IntegrityErrorStatus = json.dumps({'success': False, 'error': {'message': 'Integrity Error'}})
    LoginErrorStatus = json.dumps({'success': False, 'error': {'message': LoginFailedStatus}})
    SuccessStatus = json.dumps({'success': True})
    ErrorStatus = json.dumps(
        {'success': False, 'error': {'message': _('Something went wrong. Please contact support.')}})
    ValidationErrorStatus = json.dumps(
        {'success': False, 'error': {'message': _('You have not yet validated your email.')}})
    ResetLinkErrorStatus = json.dumps({'success': False, 'error': {'message': _('Could not send reset link.')}})

    def upload_flow(self):
        pass
        # try:
        #     token = tokens.token_show(context, user_dict)
        # except NotFound, e:
        #     token = {'valid': True}  # Until we figure out what to do with existing users
        # except:
        #     abort(500, _('Something wrong'))
        # if not token['valid']:
        #     # force logout
        #     for item in p.PluginImplementations(p.IAuthenticator):
        #         item.logout()
        #     # redirect to validation page
        #     h.flash_error(_('You have not yet validated your email.'))
        #     h.redirect_to(self._get_repoze_handler('logout_handler_path'))

    def new_login(self, error=None, info_message=None, page_subtitle=None):
        template_data = {}
        if not c.user:
            template_data = ue_helpers.get_login(True, "")
        return render(TEMPLATES["home"], extra_vars=template_data)

    def message_dataset_success(self, error=None, info_message=None, page_subtitle=None):
        template_data = {}
        template_data = ue_helpers.get_dataset_success(True, "")
        return render(TEMPLATES["home"], extra_vars=template_data)

    def logged_in(self):
        came_from = request.params.get('came_from', '')
        if h.url_is_local(came_from):
            return h.redirect_to(str(came_from))

        if c.user:
            context = None
            data_dict = {'id': c.user}
            user_dict = get_action('user_show')(context, data_dict)

            if 'created' in user_dict:
                time_passed = datetime.datetime.now() - dateutil.parser.parse(user_dict['created'])
            else:
                time_passed = None
            if 'activity' in user_dict and (not user_dict['activity']) and time_passed and time_passed.days < 3:
                return h.redirect_to('dashboard.organizations')
            else:
                userobj = c.userobj if c.userobj else model.User.get(c.user)
                login_dict = {'display_name': userobj.display_name, 'email': userobj.email,
                              'email_hash': userobj.email_hash, 'login': userobj.name}

                max_age = int(14 * 24 * 3600)
                # TODO: Remove this, not required
                # response.set_cookie('platform_login', quote(json.dumps(login_dict)), max_age=max_age)
                if not c.user:
                    h.redirect_to(locale=None, controller='user', action='login', id=None)

                # TODO: Why trailing slash is required
                _ckan_site_url = "{}/".format(BASE_URL)
                _came_from = str(request.referrer or _ckan_site_url)

                excluded_paths = ['/user/validate/', 'user/logged_in?__logins', 'user/logged_out_redirect']
                if _ckan_site_url != _came_from and not any(path in _came_from for path in excluded_paths):
                    h.redirect_to(_came_from)

                h.flash_success(_("%s is now logged in") % user_dict['display_name'])
                h.redirect_to("/dashboard", locale=None)
        else:
            err = _('Login failed. Bad username or password.')

            template_data = ue_helpers.get_login(False)
            h.flash_error(err)
            log.error("Status code 401 : username or password incorrect")
            return render(TEMPLATES['home'], extra_vars=template_data)

    def logged_out_page(self):
        template_data = ue_helpers.get_logout(True, _('User logged out with success'))
        return render(TEMPLATES['home'], extra_vars=template_data)

    def _generate_name(self, full_name):
        random_string = ''.join(random.choice(string.ascii_lowercase
                                              + string.digits) for _ in range(5))
        possible_name_list = full_name.split(" ")
        first_name = possible_name_list[0]
        if len(first_name) < 4:
            for name in possible_name_list[1:]:
                if len(name) >= 4:
                    first_name = name
                    break
        final_name = first_name + "_" + random_string
        return final_name.lower()

    def register_email(self, data=None, errors=None, error_summary=None):

        if IS_FLASK_REQUEST:
            request_data = request.form
        else:
            request_data = request.params
        data_dict = logic.clean_dict(unflatten(logic.tuplize_dict(logic.parse_params(request_data))))

        # TODO: Add Captcha feature here

        temp_schema = user_reg_schema.register_user_schema()
        if 'name' in temp_schema:
            temp_schema['name'] = [name_validator_with_changed_msg if var == name_validator else var for var in
                                   temp_schema['name']]
        context = {'model': model, 'session': model.Session, 'user': c.user, 'auth_user_obj': c.userobj,
                   'schema': temp_schema, 'save': 'save' in request.params}

        if 'email' in data_dict:
            if 'name' not in data_dict or not data_dict['name']:
                data_dict['name'] = self._generate_name(data_dict['fullname'])
        context['message'] = data_dict.get('log_message', '')

        try:
            check_access('user_create', context, data_dict)
            check_access('user_can_register', context, data_dict)
        except NotAuthorized as e:
            if e.args and len(e.args):
                message, error_type = self._get_exc_msg_by_key(e, ['email', 'name', 'password', 'fullname'])
                return self.error_message(message, error_type)
            return self.NotAuthorizedStatus
        except ValidationError as e:
            if e and e.error_summary:
                error_summary = e.error_summary
            else:
                error_summary = ['Email address is not valid. Please contact our team.']
            return self.error_message(error_summary, type='email')

        # Assuming that user is not logged in
        save_user = c.user
        c.user = None
        try:

            user = get_action('user_create')(context, data_dict)
            token = get_action('token_create')(context, user)
            context['auth_user_obj'] = context['user_obj']
            user_extra = get_action('user_extra_create')(context, {'user_id': user['id'],
                                                                   'extras': ue_helpers.get_initial_extras()})
            # TODO: Mail Subscription
        except NotAuthorized:
            return self.NotAuthorizedStatus
        except NotFound as e:
            return self.TokenNotFoundStatus
        except DataError:
            return self.IntegrityErrorStatus
        except ValidationError as e:
            error_summary = e.error_summary
            return self.error_message(error_summary)
        except Exception as e:
            error_summary = str(e)
            return self.error_message(error_summary)

        if not c.user:
            # Send validation email
            reset_link = urljoin(BASE_URL, "/user/validate/" + token['token'])
            mail = Mail.new()
            mail.send(user['email'], "Please verify your account", {'token': reset_link})

        c.user = save_user

        identity = {
            u'login': data_dict['email'],
            u'password': data_dict['password']
        }
        auth = EmailAuthenticator()

        login_status = auth.authenticate(request.environ, identity)
        if login_status == data_dict['name']:
            # Very Sensitive function
            # Login only if Authenticator allows to do so
            if u'repoze.who.plugins' in request.environ:
                rememberer = request.environ[u'repoze.who.plugins'][u'friendlyform']
                identity = {u'repoze.who.userid': data_dict["name"]}
                user_token = rememberer.remember(request.environ, identity)
                if IS_FLASK_REQUEST:
                    resp = make_response((self.SuccessStatus, 200, {}))
                    resp.headers.extend(user_token)
                else:
                    response.headerlist += user_token
                    resp = self.SuccessStatus
                return resp
            return self.IntegrityErrorStatus
        else:
            return self.NotAuthorizedStatus

    def _get_exc_msg_by_key(self, e, key):
        for k in key:
            if e and e.args:
                for arg in e.args:
                    if k in arg:
                        return arg[k] + [k]
        return None

    def validate(self, token):
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author, 'auth_user_obj': c.userobj}
        data_dict = {'token': token,
                     'extras': [{'key': user_model.USER_VALIDATED_STATUS, 'new_value': 'True'}]}
        try:
            check_access('user_can_validate', context, data_dict)
            tokens.token_update(context, data_dict)
        except NotAuthorized:
            message = "User is already Validated"
            h.flash_error(_(message))
            h.redirect_to('/login')
        except ValidationError as e:
            message = e.error_summary
            h.flash_error(_(message))
            h.redirect_to('/login')

        h.flash_success(_('Your account is successfully validated'))
        h.redirect_to('/login')

    def register(self, data=None, errors=None, error_summary=None):
        context = {'model': model, 'session': model.Session, 'user': c.user}
        try:
            check_access('user_create', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to register as a user.'))
        if c.user:
            return render('user/logout_first.html')

        template_data = {}
        if not c.user:
            template_data = ue_helpers.get_register(True, "")
        return render(TEMPLATES["home"], extra_vars=template_data)

    def validation_resend(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': id,
                     'user_obj': c.userobj}

        try:
            user = get_action('user_show')(context, data_dict)
        except NotFound as e:
            abort(404, _('User not found'))
        except:
            abort(500, _('Error'))

        # Get token for user
        try:
            token = tokens.token_show(context, data_dict)
        except NotFound as e:
            abort(404, _('User not found'))
        except:
            abort(500, _('Error'))

        # TODO: send validation email

        post_register_url = h.url_for(
            controller='ckanext.emailauth.controllers.mail_validation_controller:ValidationController',
            action='post_register')
        redirect_url = '{0}?user={1}'
        h.redirect_to(redirect_url.format(
            post_register_url,
            user['id']))

    def error_message(self, error_summary, type=None):
        return json.dumps({'success': False, 'error': {'message': error_summary},
                           'type': type})

    def request_reset(self):
        """
        Email password reset instructions to user
        """
        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'auth_user_obj': c.userobj}
        try:
            check_access('request_reset', context)
        except NotAuthorized:
            base.abort(403, _('Unauthorized to request reset password.'))

        if request.method == 'POST':
            user_id = request.params.get('user').lower()

            context = {'model': model,
                       'user': c.user}

            user_obj = None
            try:
                is_valid = validate_email(user_id)

                # TODO: Move it with user_show, possibility
                if is_valid:
                    user_id = get_action('user_email_show')(context, {'id': user_id})
                data_dict = get_action('user_show')(context, {'id': user_id})
                user_obj = context['user_obj']
            except NotFound:
                return self.UserNotFoundStatus
            try:
                token = tokens.token_show(context, data_dict)
            except NotFound:
                token = {'valid': True}
            except Exception:
                return self.ErrorStatus

            # TODO: Send validation email
            if not token['valid']:
                if user_obj:
                    reset_link = urljoin(BASE_URL, "/user/validate/" + token['token'])
                    mail = Mail.new()
                    mail.send(user_obj.email, "Please verify your account", {'token': reset_link})
                    return self.SuccessStatus
                return self.ErrorStatus
            if user_obj:
                try:
                    get_action('send_reset_link')(context, {'id': data_dict.get('id')})
                    return self.SuccessStatus
                except:
                    return self.ResetLinkErrorStatus
        return render(TEMPLATES['home'])

    def _get_form_password(self):
        if IS_FLASK_REQUEST:
            request_data = request.form
        else:
            request_data = request.params
        data_dict = logic.clean_dict(unflatten(logic.tuplize_dict(logic.parse_params(request_data))))

        password1 = data_dict['password1']
        password2 = data_dict['password2']
        if password1 is not None and password1 != '':
            if not len(password1) >= 4:
                raise ValueError(_('Your password must be 4 '
                                   'characters or longer.'))
            elif not password1 == password2:
                raise ValueError(_('The passwords you entered'
                                   ' do not match.'))
            return password1
        raise ValueError(_('You must provide a password'))

    def perform_reset(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': id,
                   'keep_email': True}

        try:
            check_access('user_reset', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to reset password.'))

        try:
            data_dict = {'id': id}
            user_dict = get_action('user_show')(context, data_dict)

            user_obj = context['user_obj']
        except NotFound as e:
            abort(404, _('User not found'))

        c.reset_key = request.params.get('key')
        if not mailer.verify_reset_link(user_obj, c.reset_key):
            h.flash_error(_('Invalid reset key. Please try again.'))
            abort(403)

        if request.method == 'POST':
            try:
                context['reset_password'] = True
                user_state = user_dict['state']
                new_password = self._get_form_password()
                user_dict['password'] = new_password
                username = request.params.get('name')
                if username is not None and username != '':
                    user_dict['name'] = username
                user_dict['reset_key'] = c.reset_key
                user_dict['state'] = model.State.ACTIVE
                user = get_action('user_update')(context, user_dict)
                mailer.create_reset_key(user_obj)

                h.flash_error(_('Password successfully changed'))
                return self.SuccessStatus
            except NotAuthorized:
                return self.NotAuthorizedStatus
            except NotFound as e:
                return self.UserNotFoundStatus
            except DataError:
                return self.error_message("Data error")
            except ValidationError as e:
                return self.ValidationErrorStatus
            except ValueError as ve:
                return self.error_message("Incorrect Value")
            user_dict['state'] = user_state

            return self.error_message("Not Authorized")

        c.user_dict = user_dict
        template_data = ue_helpers.get_reset(True, "")
        return render(TEMPLATES['home'], extra_vars=template_data)

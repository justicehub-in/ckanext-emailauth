TEMPLATES = {
    "home": "home/index.html"
}

BLUEPRINT = {
    'controller': 'ckanext.emailauth.controllers.mail_validation_controller:ValidationController',
    'actions': [
        {'url': u'/user/register',
         'name': 'register',
         'type': [u'GET']},
        {'url': u'/user/register_email',
         'name': 'register_email',
         'type': [u'POST']},
        {'url': u'/user/validate/{token}',
         'name': 'validate',
         'type': [u'GET']},
        {'url': u'/user/validation_resend/{id}',
         'name': 'validation_resend',
         'type': [u'GET']},
        {'url': u'/user/logged_out_page',
         'name': 'logged_out_page',
         'type': [u'GET']},
        {'url': u'/user/reset',
         'name': 'request_reset',
         'type': [u'GET', u'POST']},
        {'url': u'/user/logged_out_redirect',
         'name': 'logged_out_page',
         'type': [u'GET']},
        {'url': u'/user/logged_in',
         'name': 'logged_in',
         'type': [u'GET', u'POST']},
        {'url': u'/login',
         'name': 'new_login',
         'type': [u'GET']}
    ]
}


# Temporary UserController
class UserController(object):
    pass
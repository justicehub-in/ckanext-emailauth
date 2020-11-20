======================
ckanext-emailauth
======================

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!

CKAN Authentication using Email as primary identifier including username

ckanext-emailauth allows you to:

1. Enable registration / login via email or username
2. Do email verification based on any SMTP server as per configuration you provide
3. Ability to store extra user information as key value pair in user_extra table
4. Reset password via email verification link with link expiry

------------
Requirements
------------

Tested with Python 2.7 with CKAN 2.8.4

------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-emailauth:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Clone repository and install the ckanext-emailauth requirements first by::

      pip install -r requirements.txt

3. Install extension into your virtual environment::

     python setup.py install

3. Add ``emailauth`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Follow configuration step below to add necessary details


5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


-------------
Configuration
-------------

ckanext-emailauth has few custom configuration which is required before running::

      ckan.mail.key=email_id@domain.com
      ckan.mail.secret=password
      ckan.mail.sent_from=email_id@domain.com
      # Optional
      password.reset_key.expiry_hours=4


----------------------------
Modifying Authenticator
----------------------------

In your ``who.ini`` (usually in ``/usr/lib/ckan/ckan-env/src/ckan/who.ini``) file add custom authenticator as::

      [authenticators]
      plugins =
          auth_tkt
          ckanext.emailauth.authenticator:EmailAuthenticator

This will enable EmailAuthenticator during all authenticator process, it allows you to do authentication both via username
and if username is not found, then it will search for email

------------------------
Development Installation
------------------------

To install ckanext-emailauth for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/justicehub-in/ckanext-emailauth.git
    cd ckanext-emailauth
    python setup.py develop


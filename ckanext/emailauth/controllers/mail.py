from abc import abstractmethod
from ckan.plugins import toolkit
from ckan.lib.mailer import MailerException
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ckan.lib.mailer as mailer
import logging
import smtplib
from ckan.common import _


log = logging.getLogger(__name__)


class Mail(object):
    def __init__(self):
        """
        Mail object as Interface
        """
        self.site_url = toolkit.config.get(u'ckan.site_url')
        self.user_key = toolkit.config.get(u'ckan.mail.key')
        self.user_secret = toolkit.config.get(u'ckan.mail.secret')
        self.sent_from = toolkit.config.get(u'ckan.mail.sent_from')
        self.sent_from = self.sent_from if self.sent_from else self.user_key

    @abstractmethod
    def send(self, to, subject, token):
        """
        Send mail to given email id
        : result: Dict
        """
        pass

    @classmethod
    def new(cls, *args, **kwargs):
        mail_type = toolkit.config.get(u'ckanext.mail.type')
        queries = {
            'google': GoogleMail
        }

        mail_class = queries.get(mail_type, GoogleMail)
        return mail_class(*args, **kwargs)


class GoogleMail(Mail):
    def __init__(self, *args, **kwargs):
        super(GoogleMail, self).__init__(*args, **kwargs)

    def send(self, to, subject, email_data, snippet='email/base.html', footer=True, logo=True):
        # TODO: Create constant and make logo path configurable
        email_data['logo'] = toolkit.config.get(u'ckan.site_url') + '/assets/jh_logo.png'
        email_data['footer'] = footer

        body_html = mailer.render_jinja2(snippet, email_data)
        msg = MIMEMultipart()
        subject = Header(subject.encode('utf-8'), 'utf-8')
        msg['Subject'] = subject

        # TODO: JusticeHub configurable
        msg['From'] = _(u"%s <%s>") % ('JusticeHub', self.sent_from)
        msg['To'] = Header(to, 'utf-8')
        part = MIMEText(body_html, 'html', 'utf-8')
        msg.attach(part)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.user_key, self.user_secret)
            server.sendmail(self.sent_from, to, msg.as_string())
            log.info("Sent mail successfully")
        except smtplib.SMTPException as e:
            msg = '%r' % e
            log.exception(msg)
            raise MailerException(msg)
        finally:
            server.close()

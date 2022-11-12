import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

from ..model.smtp_configuration import SmtpConfiguration, Message
from email.utils import make_msgid


class PostMan:

    def __init__(self, server: SmtpConfiguration):
        self.server = server

    def _connect(self) -> smtplib.SMTP:

        """Creating a session with SMTP protocol"""
        session = smtplib.SMTP(self.server.smtp, self.server.port, timeout=self.server.timeout)
        session.ehlo()
        session.starttls()

        """Entering login and password"""
        session.login(self.server.username, self.server.password)
        return session

    @staticmethod
    def _prepare_message(mail: Message) -> MIMEMultipart:

        """Create and configure message container """
        message_container = MIMEMultipart('alternative')
        message_container['From'] = mail.send_from
        message_container['To'] = mail.send_to
        message_container['Subject'] = mail.title
        message_container['Message-ID'] = make_msgid()
        message_container['Content-type'] = mail.message.type
        message_container.add_header('reply-to', mail.reply_to)

        if mail.message.type == 'text/html':
            message_container.attach(MIMEText(mail.message.content, 'html'))
        else:
            """Cleaning message.content from HTML tags using bs4 """
            body_message = BeautifulSoup(mail.message.content, "lxml").text
            message_container.attach(MIMEText(body_message, 'plain'))

        return message_container

    def send(self, message: Message):
        session = self._connect()
        body = self._prepare_message(message).as_string()
        session.sendmail(message.send_from, message.send_to, body)
        session.quit()

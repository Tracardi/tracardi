import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

from ..model.smtp_configuration import SmtpConfiguration, Message


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
    def _prepare_message(message: Message) -> MIMEMultipart:

        """Create and configure message container """
        message_container = MIMEMultipart('alternative')
        message_container['From'] = message.send_from
        message_container['To'] = message.send_to
        message_container['Subject'] = message.title
        message_container.add_header('reply-to', message.reply_to)

        """Cleaning self.message from HTML tags using bs4 """
        clear_message = BeautifulSoup(message.message, "lxml").text

        """Creating two parts of message one with HTML tags one without"""
        part1 = MIMEText(clear_message, 'plain')
        part2 = MIMEText(message.message, 'html')
        message_container.attach(part1)
        message_container.attach(part2)

        return message_container

    def send(self, message: Message):
        session = self._connect()
        session.sendmail(message.send_from, message.send_to, self._prepare_message(message).as_string())
        session.quit()

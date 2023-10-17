from typing import Union, List, Optional, Tuple


class SocialMedia:

    def __init__(self):
        self.social_media_list = [('//www.facebook.com', 'facebook'), ('//facebook.com', 'facebook'),
                                  ('//twitter.com', 'twitter'), ('//www.twitter.com', 'twitter'),
                                  ('//instagram.com', 'instagram'), ('//www.instagram.com', 'instagram'),
                                  ('//www.linkedin.com', 'linkedin'), ('//linkedin.com', 'linkedin'),
                                  ('pinterest', 'pinterest'),
                                  ('snapchat', 'snapchat'), ('youtube', 'youtube'), ('tiktok', 'tiktok'),
                                  ('//whatsapp.com', 'whatsapp'), ('//api.whatsapp.com', 'whatsapp'),
                                  ('//www.whatsapp.com', 'whatsapp'), ('messenger', 'messenger'), ('reddit', 'reddit'),
                                  ('tumblr', 'tumblr'), ('wechat', 'wechat'), ('line', 'line'), ('viber', 'viber'),
                                  ('telegram', 'telegram'), ('skype', 'skype'), ('vk', 'vk'), ('qq', 'qq'),
                                  ('sina weibo', 'sina weibo'), ('weibo', 'weibo'), ('baidu tieba', 'baidu tieba'),
                                  ('whatsapp business', 'whatsapp business'), ('flickr', 'flickr'),
                                  ('periscope', 'periscope'), ('vimeo', 'vimeo'), ('medium', 'medium'),
                                  ('quora', 'quora'), ('mixcloud', 'mixcloud'), ('meetup', 'meetup'),
                                  ('soundcloud', 'soundcloud'), ('twitch', 'twitch'), ('bandcamp', 'bandcamp'),
                                  ('deviantart', 'deviantart'), ('dribbble', 'dribbble'), ('behance', 'behance'),
                                  ('500px', '500px'), ('foursquare', 'foursquare'), ('steemit', 'steemit'),
                                  ('myspace', 'myspace'), ('renren', 'renren'), ('xing', 'xing'),
                                  ('mastodon', 'mastodon'), ('plurk', 'plurk'), ('ello', 'ello'),
                                  ('myspace', 'myspace'), ('yelp', 'yelp'), ('gab', 'gab'), ('parler', 'parler'),
                                  ('rumble', 'rumble'), ('odysee', 'odysee'), ('minds', 'minds'),
                                  ('friendster', 'friendster'), ('orkut', 'orkut'), ('hi5', 'hi5'), ('xanga', 'xanga'),
                                  ('bebo', 'bebo'), ('blackplanet', 'blackplanet'), ('tagged', 'tagged'),
                                  ('meetme', 'meetme'), ('livejournal', 'livejournal'), ('skyrock', 'skyrock'),
                                  ('stumbleupon', 'stumbleupon'), ('hi5', 'hi5'), ('xanga', 'xanga'), ('ning', 'ning'),
                                  ('badoo', 'badoo'), ('meetme', 'meetme'), ('taringa!', 'taringa'),
                                  ('goodreads', 'goodreads'), ('taringa!', 'taringa'), ('taringa!', 'taringa'),
                                  ('renren', 'renren'), ('renren', 'renren'), ('spreely', 'spreely'),
                                  ('cafemom', 'cafemom'), ('xiaonei', 'xiaonei'), ('vkontakte', 'vkontakte'),
                                  ('habbo', 'habbo'), ('classmates', 'classmates'), ('livejournal', 'livejournal'),
                                  ('odnoklassniki', 'odnoklassniki'), ('gaia online', 'gaia online'),
                                  ('mylife', 'mylife'), ('taringa!', 'taringa'), ('renren', 'renren'),
                                  ('renren', 'renren'), ('skyrock', 'skyrock'), ('ning', 'ning'), ('badoo', 'badoo'),
                                  ('taringa!', 'taringa'), ('renren', 'renren'), ('friendster', 'friendster'),
                                  ('badoo', 'badoo'), ('ning', 'ning'), ('gaia online', 'gaia online'),
                                  ('taringa!', 'taringa'), ('skyrock', 'skyrock'), ('renren', 'renren'),
                                  ('badoo', 'badoo'), ('ning', 'ning'), ('gaia online', 'gaia online'),
                                  ('taringa', 'taringa')]

    def _has_social_string(self, item):
        for social_string, name in self.social_media_list:
            if social_string in item.lower():
                return name
        return False

    def filter_social_urls(self, url_list) -> List:
        filtered_urls = set()
        for url in url_list:
            social_name = self._has_social_string(url)
            if social_name:
                filtered_urls.add((url, social_name))
        return list(filtered_urls)

    def has_social_media_string(self, data) -> Union[Optional[Tuple[str, str]], List[Tuple[str, str]]]:
        if isinstance(data, list):
            return self.filter_social_urls(data)
        elif isinstance(data, str):
            social_name = self._has_social_string(data)
            return (data, social_name) if social_name else None
        else:
            raise ValueError("Data can be either list or string.")

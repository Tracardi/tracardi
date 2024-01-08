from tracardi.service.utils.social_media import SocialMedia


def test_filter_social_urls_valid_urls():
    social_media = SocialMedia()
    url_list = ['https://www.facebook.com', 'https://www.twitter.com', 'https://www.instagram.com']
    l = social_media.filter_social_urls(url_list)
    assert ('https://www.facebook.com', 'facebook') in l
    assert ('https://www.twitter.com', 'twitter') in l
    assert ('https://www.instagram.com', 'instagram') in l


def test_has_social_media_string_valid_url_string():
    social_media = SocialMedia()
    url_string = 'https://www.facebook.com'
    expected_result = ('https://www.facebook.com', 'facebook')
    assert social_media.has_social_media_string(url_string) == expected_result


def test_filter_social_urls_empty_list():
    social_media = SocialMedia()
    url_list = []
    expected_result = []
    assert social_media.filter_social_urls(url_list) == expected_result


def test_has_social_media_string_empty_string():
    social_media = SocialMedia()
    url_string = ''
    expected_result = None
    assert social_media.has_social_media_string(url_string) == expected_result


def test_filter_social_urls_invalid_urls():
    social_media = SocialMedia()
    url_list = ['https://www.example.com', 'https://www.invalidurl.com']
    expected_result = []
    assert social_media.filter_social_urls(url_list) == expected_result

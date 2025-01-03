from tracardi.config import tracardi
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.profile_data import PREFIX_EMAIL_BUSINESS, PREFIX_EMAIL_MAIN, PREFIX_EMAIL_PRIVATE, \
    PREFIX_PHONE_BUSINESS, PREFIX_PHONE_MAIN, PREFIX_PHONE_MOBILE, \
    PREFIX_PHONE_WHATSUP
from tracardi.common.security.hashing.hasher import timestamped_hash_id

tracardi.auto_profile_merging = "abc"

def test_returns_string_with_length_40():
    value = "test"
    prefix = "emb"
    result = timestamped_hash_id(value, prefix)
    assert isinstance(result, str)
    assert len(result) <= 40
    assert result.startswith("emb-9bc648bc-afbc-f965-564f")


def test_hash_only_allowed():
    # Setup
    flat_profile = FlatProfile(dict(
        id='1',
        data=dict(
            contact=dict(
                email=dict(
                    business="business@example.com",
                    main="main@example.com",
                    private="private@example.com"
                )
            )
        )
    ))

    # Invoke method
    assert flat_profile.hash_all_allowed_pii_as_ids(allowed=['data.contact.email.business'])

    # Assertions
    assert flat_profile.has_hashed_email_id(PREFIX_EMAIL_BUSINESS) is True
    assert flat_profile.has_hashed_email_id(PREFIX_EMAIL_MAIN) is False
    assert flat_profile.has_hashed_email_id(PREFIX_EMAIL_PRIVATE) is False


def test_add_hashed_ids_with_existing_email_ids():
    # Setup
    flat_profile = FlatProfile(dict(
        id='1',
        data=dict(
            contact=dict(
                email=dict(
                    business="business@example.com",
                    main="main@example.com",
                    private="private@example.com"
                )
            )
        )
    ))

    assert flat_profile.has('data.contact.email.business')

    # Invoke method
    assert flat_profile.hash_all_allowed_pii_as_ids()

    # Assertions
    assert flat_profile.has_hashed_email_id(PREFIX_EMAIL_BUSINESS) is True
    assert flat_profile.has_hashed_email_id(PREFIX_EMAIL_MAIN) is True
    assert flat_profile.has_hashed_email_id(PREFIX_EMAIL_PRIVATE) is True


def test_add_hashed_ids_with_existing_phone_ids():
    # Setup
    profile = FlatProfile(dict(
        id='1',
        data=dict(
            contact=dict(
                phone=dict(
                    business="123456789",
                    main="987654321",
                    mobile="555555555",
                    whatsapp="999999999"
                )
            )
        )
    ))

    # Invoke method
    assert profile.hash_all_allowed_pii_as_ids()

    # Assertions
    assert profile.has_hashed_phone_id(PREFIX_PHONE_BUSINESS) is True
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MAIN) is True
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MOBILE) is True
    assert profile.has_hashed_phone_id(PREFIX_PHONE_WHATSUP) is True


def test_add_hashed_ids_with_no_existing_ids():
    # Setup
    profile = FlatProfile(dict(id='1'))

    # Invoke method
    assert not profile.hash_all_allowed_pii_as_ids()

    # Assertions
    assert profile.has_hashed_email_id(PREFIX_EMAIL_BUSINESS) is False
    assert profile.has_hashed_email_id(PREFIX_EMAIL_MAIN) is False
    assert profile.has_hashed_email_id(PREFIX_EMAIL_PRIVATE) is False
    assert profile.has_hashed_phone_id(PREFIX_PHONE_BUSINESS) is False
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MAIN) is False
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MOBILE) is False
    assert profile.has_hashed_phone_id(PREFIX_PHONE_WHATSUP) is False


def test_add_hashed_ids_with_empty_email_ids():
    # Setup
    profile = FlatProfile(dict(
        id='1',
        data=dict(
            contact=dict(
                email=dict(
                    business="",
                    main="",
                    private=""
                )
            )
        )
    ))

    # Invoke method
    assert not profile.hash_all_allowed_pii_as_ids()

    # Assertions
    assert profile.has_hashed_email_id(PREFIX_EMAIL_BUSINESS) is False
    assert profile.has_hashed_email_id(PREFIX_EMAIL_MAIN) is False
    assert profile.has_hashed_email_id(PREFIX_EMAIL_PRIVATE) is False


def test_add_hashed_ids_with_empty_phone_ids():
    # Setup
    profile = FlatProfile(dict(
        id="1",
        data=dict(
            contact=dict(
                phone=dict(
                    business="",
                    main="",
                    mobile="",
                    whatsapp=""
                )
            )
        )
    ))

    # Invoke method
    profile.hash_all_allowed_pii_as_ids()

    # Assertions
    assert profile.has_hashed_phone_id(PREFIX_PHONE_BUSINESS) is False
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MAIN) is False
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MOBILE) is False
    assert profile.has_hashed_phone_id(PREFIX_PHONE_WHATSUP) is False


def test_should_return_string():
    # Arrange
    value = "test"
    prefix = "prefix"

    # Act
    result = timestamped_hash_id(value, prefix)

    # Assert
    assert isinstance(result, str)

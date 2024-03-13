from tracardi.config import tracardi
from tracardi.domain.profile import Profile
from tracardi.domain.profile_data import ProfileData, PREFIX_EMAIL_BUSINESS, PREFIX_EMAIL_MAIN, PREFIX_EMAIL_PRIVATE, \
    ProfileContact, ProfileEmail, ProfilePhone, PREFIX_PHONE_BUSINESS, PREFIX_PHONE_MAIN, PREFIX_PHONE_MOBILE, \
    PREFIX_PHONE_WHATSUP
from tracardi.service.utils.hasher import timestamped_hash_id

tracardi.auto_profile_merging = "abc"

def test_returns_string_with_length_40():
    value = "test"
    prefix = "emb"
    result = timestamped_hash_id(value, prefix)
    assert isinstance(result, str)
    assert len(result) <= 40
    assert result.startswith("emb-9bc648bc-afbc-f965-564f")


def test_add_hashed_ids_with_existing_email_ids():
    # Setup
    profile = Profile(
        id='1',
        data=ProfileData(
            contact=ProfileContact(
                email=ProfileEmail(
                    business="business@example.com",
                    main="main@example.com",
                    private="private@example.com"
                )
            )
        )
    )

    # Invoke method
    profile.create_auto_merge_hashed_ids()

    # Assertions
    assert profile.has_hashed_email_id(PREFIX_EMAIL_BUSINESS) is True
    assert profile.has_hashed_email_id(PREFIX_EMAIL_MAIN) is True
    assert profile.has_hashed_email_id(PREFIX_EMAIL_PRIVATE) is True


def test_add_hashed_ids_with_existing_phone_ids():
    # Setup
    profile = Profile(
        id='1',
        data=ProfileData(
            contact=ProfileContact(
                phone=ProfilePhone(
                    business="123456789",
                    main="987654321",
                    mobile="555555555",
                    whatsapp="999999999"
                )
            )
        )
    )

    # Invoke method
    profile.create_auto_merge_hashed_ids()

    # Assertions
    assert profile.has_hashed_phone_id(PREFIX_PHONE_BUSINESS) is True
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MAIN) is True
    assert profile.has_hashed_phone_id(PREFIX_PHONE_MOBILE) is True
    assert profile.has_hashed_phone_id(PREFIX_PHONE_WHATSUP) is True


def test_add_hashed_ids_with_no_existing_ids():
    # Setup
    profile = Profile(id='1')

    # Invoke method
    profile.create_auto_merge_hashed_ids()

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
    profile = Profile(
        id='1',
        data=ProfileData(
            contact=ProfileContact(
                email=ProfileEmail(
                    business="",
                    main="",
                    private=""
                )
            )
        )
    )

    # Invoke method
    profile.create_auto_merge_hashed_ids()

    # Assertions
    assert profile.has_hashed_email_id(PREFIX_EMAIL_BUSINESS) is False
    assert profile.has_hashed_email_id(PREFIX_EMAIL_MAIN) is False
    assert profile.has_hashed_email_id(PREFIX_EMAIL_PRIVATE) is False


def test_add_hashed_ids_with_empty_phone_ids():
    # Setup
    profile = Profile(
        id="1",
        data=ProfileData(
            contact=ProfileContact(
                phone=ProfilePhone(
                    business="",
                    main="",
                    mobile="",
                    whatsapp=""
                )
            )
        )
    )

    # Invoke method
    profile.create_auto_merge_hashed_ids()

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

from tracardi.context import Context, ServerContext
from tracardi.domain.setting import Setting
from tracardi.service.storage.mysql.mapping.setting_mapping import map_to_setting, map_to_settings_table

from tracardi.service.storage.mysql.schema.table import SettingTable
from tracardi.service.utils.date import now_in_utc


def test_all_fields_mapped():
    # Arrange
    settings_table = SettingTable(
        id="123",
        timestamp=now_in_utc(),
        name="Test Setting",
        description="This is a test setting",
        type="setting",
        enabled=True,
        content={"key": "value"},
        config={"option": "true"}
    )

    expected_setting = Setting(
        id="123",
        timestamp=settings_table.timestamp,
        name="Test Setting",
        description="This is a test setting",
        type="setting",
        enabled=True,
        content={"key": "value"},
        config={"option": "true"}
    )

    # Act
    result = map_to_setting(settings_table)

    # Assert
    assert result == expected_setting


def test_same_fields_as_input_setting_object():
    with ServerContext(Context(production=True)):
        setting = Setting(
            id="123",
            name="Test Setting",
            timestamp=now_in_utc(),
            description="This is a test setting",
            type="setting-type",
            enabled=True,
            content={"key": "value"},
            config={"config_key": "config_value"}
        )

        settings_table = map_to_settings_table(setting)

        assert settings_table.id == "123"
        assert settings_table.production is True
        assert settings_table.name == "Test Setting"
        assert settings_table.timestamp == setting.timestamp
        assert settings_table.description == "This is a test setting"
        assert settings_table.type == "setting-type"
        assert settings_table.enabled is True
        assert settings_table.content == {"key": "value"}
        assert settings_table.config == {"config_key": "config_value"}

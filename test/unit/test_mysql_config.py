from tracardi.config import MysqlConfig


def test_initializes_with_default_values():
    env = {}
    config = MysqlConfig(env)

    assert config.env == env
    assert config.mysql_host == "localhost"
    assert config.mysql_username == "root"
    assert config.mysql_password == "root"
    assert config.mysql_schema == "mysql+aiomysql://"
    assert config.mysql_port == 3306
    assert config.mysql_database == "tracardi"
    assert config.mysql_echo == False
    assert config.mysql_database_uri == "mysql+aiomysql://root:root@localhost:3306"


def test_initializes_without_creds():
    env = {
        "MYSQL_USERNAME": "",
        "MYSQL_PASSWORD": ""
    }
    config = MysqlConfig(env)

    assert config.env == env
    assert config.mysql_host == "localhost"
    assert config.mysql_username == ""
    assert config.mysql_password == ""
    assert config.mysql_schema == "mysql+aiomysql://"
    assert config.mysql_port == 3306
    assert config.mysql_database == "tracardi"
    assert config.mysql_echo == False
    assert config.mysql_database_uri == "mysql+aiomysql://localhost:3306"
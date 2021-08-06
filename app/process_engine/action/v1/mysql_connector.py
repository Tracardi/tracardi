from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import MySQLdb

class MySQL(ActionRunner):

    def __init__(self, *args, **kwargs):
        self.config = kwargs
        self.user = kwargs['user'] if 'user' in kwargs else None
        self.password = kwargs['password'] if 'password' in kwargs else None
        self.host = kwargs['host'] if 'host' in kwargs else None
        self.database = kwargs['database'] if 'database' in kwargs else None
        self.engine = create_engine(f'mysql://'+self.user+":"+self.password+"@"+self.host+"/"+self.database, encoding='utf-8', echo=True)
        try:
            print(self.engine.connect())
            self.connection_status = True
        except:
            self.connection_status = False

    async def run(self, void):
        print("end input", void)
        return Result(port='session', value=self.connection_status)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='app.process_engine.action.v1.mysql_connector',
            className='MySQL',
            inputs=["void"],
            outputs=['session'],
            init={'host': None,
                  'user': None,
                  'password': None,
                  'database': 'jazda'},
            version='0.1',
            license="MIT",
            author="iLLu"

        ),
        metadata=MetaData(
            name='Connect MySQL',
            desc='Connect to MySQL Database.',
            type='flowNode',
            width=100,
            height=100,
            icon='start',
            group=["Mysql"]
        )
    )

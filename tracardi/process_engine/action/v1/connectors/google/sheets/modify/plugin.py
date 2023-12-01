import json
from typing import Union

from aiohttp import ClientConnectorError
from googleapiclient.errors import HttpError
from pydantic import BaseModel

from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from googleapiclient.discovery import build
from google.oauth2 import service_account

from tracardi.service.domain import resource as resource_db
from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class GoogleSheetsIntegratorAction(ActionRunner):

    service_account_credentials: Union[BaseModel, dict, None]
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.service_account_credentials = resource.credentials.get_credentials(self)

    async def run(self, payload: dict, in_edge=None) -> Result:

        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        sample_spreadsheet_id = self.config.spreadsheet_id
        sample_range_name = f"{self.config.sheet_name}!{self.config.range}"

        try:

            credentials = service_account.Credentials.from_service_account_info(self.service_account_credentials,
                                                                                scopes=scopes)
            if self.config.read is True and self.config.write is True:
                message = "You can't read and write data at the same time."
                self.console.error(message)
                return ValueError(message)

            if self.config.read is True:

                service = build('sheets', 'v4', credentials=credentials)
                read_result = service.spreadsheets().values().get(spreadsheetId=sample_spreadsheet_id,
                                                                  range=self.config.range).execute()
                values = read_result.get('values', [])

                if not values:
                    self.console.warning('No data found in the range defined in Google spreadsheet plugin.')
                    response = 'No data found.'
                else:
                    response = read_result

            elif self.config.write is True:
                if self.config.values is None:
                    message = "If you want to parse data, set values to parse"
                    self.console.warning(message)
                    raise ValueError(message)

                service = build('sheets', 'v4', credentials=credentials)
                values = json.loads(self.config.values)
                write_request = service.spreadsheets().values().update(spreadsheetId=sample_spreadsheet_id,
                                                                       range=sample_range_name,
                                                                       valueInputOption="USER_ENTERED",
                                                                       body={"values": values}).execute()

                response = write_request

            else:
                response = None

        except HttpError as e:
            message = "You do not have permissions to access this spreadsheet. Please go to Google SpreadSheets and " \
                      "click Share in the upper right corner and add the following address {}.".format(
                        self.service_account_credentials['client_email'])
            self.console.error(message)
            return Result(port="error", value=message)
        except ClientConnectorError as e:
            return Result(port="error", value=str(e))

        return Result(port="payload", value=response)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='GoogleSheetsIntegratorAction',
            inputs=["payload"],
            outputs=['payload', 'error'],
            version='0.6.1',
            license="MIT + CC",
            author="Marcin Gaca, Risto Kowaczewski",
            manual='google_spreadsheet',
            init={
                "source": {"id": None, "name": None},
                "spreadsheet_id": None,
                "sheet_name": None,
                "range": None,
                "read": False,
                "write": False,
                "values": "[[\"Name\", \"John\"]]",
            },
            form=Form(groups=[
                FormGroup(
                    name="Google Connection Settings",
                    fields=[
                        FormField(
                            id="source",
                            name="Google Cloud Service Account Resource",
                            description="Select GCP Account Service resource. Credentials set in this resource will be "
                                        "used to connect to Google spreadsheets",
                            component=FormComponent(
                                type="resource",
                                props={"label": "resource", "tag": "gcp-service-account"})
                        )
                    ]
                ),
                FormGroup(
                    name="Spreadsheet Configuration",
                    fields=[
                        FormField(
                            id="spreadsheet_id",
                            name="Spreadsheet Id",
                            description="Type spreadsheet id. Spreadsheet Id is in Spreadsheet URL. See documentation "
                                        "for details.",
                            component=FormComponent(type="text", props={"label": "Spreadsheet Id"})
                        ),
                        FormField(
                            id="sheet_name",
                            name="Sheet name",
                            description="Type sheet name.",
                            component=FormComponent(type="text", props={"label": "Sheet name"})
                        )
                    ]),
                FormGroup(
                    name="Data Configuration",
                    fields=[
                        FormField(
                            id="range",
                            name="Data Range",
                            description="Type data range you are operating on. E.g. \"A1:F4\"",
                            component=FormComponent(type="text", props={"label": "Data range"})
                        ),
                        FormField(
                            id="read",
                            name="Read data",
                            component=FormComponent(type="bool", props={"label": "I want to read data"})
                        ),
                        FormField(
                            id="write",
                            name="Write data",
                            component=FormComponent(type="bool", props={"label": "I want to write data"})
                        ),
                        FormField(
                            id="values",
                            name="Values",
                            description="Type values as a list of column value, e.g. [['Name', 'John'], ['Last Name', 'Doe']]",
                            component=FormComponent(type="json", props={"label": "Values"})
                        ),
                    ])
            ]),
        ),
        metadata=MetaData(
            name='Google Spreadsheet',
            desc='This plugin connects Tracardi to Google Sheets.',
            icon='google',
            group=["Google"]
        )
    )

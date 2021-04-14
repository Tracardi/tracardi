from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from ..errors.errors import NullResponseError, convert_exception_to_json
from ..globals.authentication import get_current_user
from ..globals.elastic_client import elastic_client

router = APIRouter(
    prefix="/action",
    # dependencies=[Depends(get_current_user)]
)

action_mapper = {
    # This one is working
    "unomi:CopyAllProperties": {
        "metadata": {
            "enabled": True,
            "description": "Copy all properties from event to profile properties.",
            "signature": "unomi:CopyAllProperties()",
            "parameters": []
        },
    },
    # This one works
    "unomi:CopyProperty": {
        "metadata": {
            "enabled": True,
            "description": "Copy selected property from event to profile property. " +
                           "This function requires 3 parameters an event property name, profile property name and " +
                           "type of assignment (default is equals).",

            "form": {
                "params": {
                    "eventProperty": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^(?!\.)[a-zA-Z0-9\._]+(?<!\.)$",
                            "error": "Field name must not start and end with dot and must contain only letters and numbers or underscore"
                        },
                        "props": {
                            "label": "event property field"
                        }
                    },
                    "profileProperty": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^(?!\.)[a-zA-Z0-9\._]+(?<!\.)$",
                            "error": "Field name must not start and end with dot and must contain only letters and numbers or underscore"
                        },
                        "props": {
                            "label": "profile property field"
                        }
                    }
                },
                "signature": "unomi:CopyProperty(\"${eventProperty}\", \"${profileProperty}\")",
                "steps": [
                    {
                        "template": "Create profile property if does not exist",
                    },
                    {
                        "template": "Make ${profileProperty} equal to ${eventProperty}",
                    }
                ]
            },
            "parameters": [
                {"name": "eventPropertyField", "defaultValue": None, "description": "Name of event property"},
                {"name": "profilePropertyField", "defaultValue": None, "description": "Name of profile property"}
            ]
        },
    },
    # This one works
    "unomi:SetProperty": {
        "metadata": {
            "enabled": True,
            "description": "Sets profile property to given value of type string, int, bool, list. " +
                           "This function requires 3 parameters a profile property name, event property name and " +
                           "type of assignment (default is equals).",
            "signature": "unomi:SetProperty(profilePropertyField, value, [, op=\"equals\"])"
        },
    },
    # This one works
    "AddToProfileListProperty": {
        "enabled": False,
        "metadata": {
            "description": "Add value to profile property. Property must be array and be of the same type as value. " +
                           "This function requires 2 parameters a profile property name and property value to add.",
            "signature": "AddToProfileProperty(profilePropertyName:string, propertyToAdd:any)"
        },
    },
    # This one not working
    "RemoveFromProfileProperty": {
        "enabled": False,
        "metadata": {
            "description": "Removes value from profile property. Property must be array and be of the same type as value. " +
                           "This function requires 2 parameters a profile property name and property value to remove.",
            "signature": "RemoveFromProfileProperty(profilePropertyName:string, propertyToRemove:any)"
        },
    },
    "ProfilePropertyEqualsEventProperty": {
        "metadata": {
            "enabled": True,
            "description": "Copy property from event to profile property. " +
                           "This function requires 2 parameters an profile property name, event property name.",
            "signature": "ProfilePropertyEqualsEventProperty(profilePropertyName:string, eventPropertyName:string)"
        },
    },
    "NewUserSince": {
        "enabled": True,
        "metadata": {
            "signature": "NewUserSince(numberOfDays:number)"
        },
    },
    # This one not working
    "_AddToProfilePropertyList": {
        "enabled": True,
        "metadata": {
            "signature": "AddToProfilePropertyList(listIdentifiers:array)"
        },
    }

}


def __search_actions(query):
    for function_name, data in action_mapper.items():
        query = query.lower()
        if ('description' in data['metadata'] and query in data['metadata']['description'].lower()) or \
                (query in function_name.lower()):
            if data['metadata']['enabled']:
                yield {
                    "function": function_name,
                    "metadata": data['metadata']
                }


@router.get("/search")
async def event_data(query: str = None):
    # try:
    if not query:
        return []
    return list(__search_actions(query))
# except Exception as e:
#     raise HTTPException(status_code=500, detail=convert_exception_to_json(e))

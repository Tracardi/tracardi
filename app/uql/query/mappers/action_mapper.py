from ...query.statement_templates.action_stmt_template import copy_events_to_profile_properties_stmt, \
    set_profile_property_from_event_stmt, profile_property_equals_event_property_stmt, \
    new_user_since, set_profile_property_stmt, _add_to_profile_property_list_stmt, add_to_profile_property_stmt, \
    remove_from_profile_property_stmt

action_mapper = {
    # This one is working
    "profile.CopyAll": {
        "metadata": {
            "enabled": True,
            'icon': "copy",
            "description": "Copy all properties from event to profile properties.",
            "parameters": [],
            "form": {
                "params": {},
                "signature": "profile.CopyAll()",
                "steps": [
                    {
                        "template": "Copy all event properties to profile",
                    }
                ]
            },
        },
        "exec": copy_events_to_profile_properties_stmt,
        "unomi": {
            "template": {
                "type": "allEventToProfilePropertiesAction",
                "parameterValues": {},

            }
        }
    },
    # This one works
    "profile.Copy": {
        "metadata": {
            "enabled": True,
            'icon': "copy",
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
                "signature": "profile.Copy(${eventProperty}, ${profileProperty})",
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
        "exec": set_profile_property_from_event_stmt,
        "unomi": {
            "template": {
                "type": "setPropertyAction",
                "parameterValues": {
                    "setPropertyName": "properties(%s)",  # first param
                    "setPropertyValue": "eventProperty::properties(%s)",  # second param
                    "setPropertyStrategy": "alwaysSet"
                }
            }
        }
    },
    # This one works
    "profile.SetString": {
        "metadata": {
            "enabled": True,
            'icon': "json",
            "description": "Sets profile property to given value of type string. " +
                           "This function requires 2 parameters a profile property name and string value",
            "parameters": [
                {"name": "profilePropertyField", "defaultValue": None, "description": "Name of profile property"},
                {"name": "value", "defaultValue": None, "description": "Value of profile property"}
            ],
            "form": {
                "signature": "profile.SetString(${profileProperty}, \"${value}\")",
                "params": {
                    "profileProperty": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^(?!\.)[a-zA-Z0-9\._]+(?<!\.)$",
                            "error": "Field name must not start and end with dot and must contain only letters and numbers or underscore"
                        },
                        "props": {
                            "label": "profile property field"
                        }
                    },
                    "value": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^[^\"]+$",
                            "error": "Field name must have quote character"
                        },
                        "props": {
                            "label": "value"
                        }
                    }
                },
                "steps": [
                    {
                        "template": "Create profile property if does not exist",
                    },
                    {
                        "template": "Make ${profileProperty} equal to ${value}",
                    }
                ]
            },

        },
        "exec": set_profile_property_stmt,
        "unomi": {
            "template": {
                "type": "setPropertyAction",
                "parameterValues": {
                    "setPropertyName": "properties(%s)",  # profile_property_name
                    "%s": "%s",  # set_property_value: property_value,
                    "setPropertyStrategy": "alwaysSet"
                }
            }
        }

    },
    "profile.SetInteger": {
        "metadata": {
            "enabled": True,
            'icon': "json",
            "description": "Sets profile property to given value of type integer. " +
                           "This function requires 2 parameters a profile property name and integer value",
            "parameters": [
                {"name": "profilePropertyField", "defaultValue": None, "description": "Name of profile property"},
                {"name": "value", "defaultValue": None, "description": "Value of profile property"}
            ],
            "form": {
                "signature": "profile.SetInteger(${profileProperty}, ${value})",
                "params": {
                    "profileProperty": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^(?!\.)[a-zA-Z0-9\._]+(?<!\.)$",
                            "error": "Field name must not start and end with dot and must contain only letters and numbers or underscore"
                        },
                        "props": {
                            "label": "profile property field"
                        }
                    },
                    "value": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^\d+$",
                            "error": "Field name be integer"
                        },
                        "props": {
                            "label": "value"
                        }
                    }
                },
                "steps": [
                    {
                        "template": "Create profile property if does not exist",
                    },
                    {
                        "template": "Make ${profileProperty} equal to ${value}",
                    }
                ]
            },

        },
        "exec": set_profile_property_stmt,
        "unomi": {
            "template": {
                "type": "setPropertyAction",
                "parameterValues": {
                    "setPropertyName": "properties(%s)",  # profile_property_name
                    "%s": "%s",  # set_property_value: property_value,
                    "setPropertyStrategy": "alwaysSet"
                }
            }
        }

    },
    # This one works
    "profile.AddStringToList": {
        "metadata": {
            "enabled": True,
            'icon': "addToList",
            "description": "Add value to profile property. Property must be array and be of the same type as value. " +
                           "This function requires 2 parameters a profile property name and property value to add.",

            "parameters": [
                {"name": "profilePropertyField", "defaultValue": None, "description": "Name of profile property"},
                {"name": "value", "defaultValue": None, "description": "Value to add"}
            ],
            "form": {
                "signature": "profile.AddStringToList(${profileProperty}, \"${value}\")",
                "params": {
                    "profileProperty": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^(?!\.)[a-zA-Z0-9\._]+(?<!\.)$",
                            "error": "Field name must not start and end with dot and must contain only letters and numbers or underscore"
                        },
                        "props": {
                            "label": "profile property field"
                        }
                    },
                    "value": {
                        "type": "input",
                        "validate": {
                            "regexp": r"^[^\"]+$",
                            "error": "Field name be not empty string"
                        },
                        "props": {
                            "label": "value to add to list"
                        }
                    }
                },
                "steps": [
                    {
                        "template": "Create profile property if does not exist",
                    },
                    {
                        "template": "Add string ${value} to list ${profileProperty}",
                    }
                ]
            }
        },
        "exec": add_to_profile_property_stmt,
        "unomi": {
            "template": {
                "type": "setPropertyAction",
                "parameterValues": {
                    "setPropertyName": "%s",  # profile_property_name
                    "%s": "%s",  # set_property_value: property_value,
                    "setPropertyStrategy": 'addValue'
                }
            }
        }
    },
    # This one not working
    "profile.Remove": {

        "metadata": {
            "enabled": False,
            'icon': "removeFromList",
            "description": "Removes value from profile property. Property must be array and be of the same type as value. " +
                           "This function requires 2 parameters a profile property name and property value to remove.",
            "signature": "profile.Remove(profilePropertyName:string, propertyToRemove:any)"
        },
        "exec": remove_from_profile_property_stmt
    },
    # "ProfilePropertyEqualsEventProperty": {
    #     "enabled": False,
    #     "metadata": {
    #         "description": "Copy property from event to profile property. " +
    #                        "This function requires 2 parameters an profile property name, event property name.",
    #         "signature": "ProfilePropertyEqualsEventProperty(profilePropertyName:string, eventPropertyName:string)"
    #     },
    #     'exec': profile_property_equals_event_property_stmt
    # },
    # "NewUserSince": {
    #     "enabled": False,
    #     "metadata": {
    #         "signature": "NewUserSince(numberOfDays:number)"
    #     },
    #     'exec': new_user_since
    # },
    # # This one not working
    # "_AddToProfilePropertyList": {
    #     "enabled": False,
    #     "metadata": {
    #         "signature": "AddToProfilePropertyList(listIdentifiers:array)"
    #     },
    #     'exec': _add_to_profile_property_list_stmt
    # }

}

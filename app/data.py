_plugins = [
    {
        "data": {
            "metadata": {
                "name": "Start",
                "type": "flowNode",
                "desc": "Get payload",
                "width": 100,
                "height": 100,
                "icon": "payload"
            },
            "spec": {
                "module": "app.process_engine.action.payload_action",
                "className": "PayloadAction",
                "inputs": [],
                "outputs": [
                    "payload"
                ],
                "config": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Raise event",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "event"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "IF Condition",
                "type": "flowNode",
                "desc": "if type=\"dasdas\" asa \"assa.sdsd.asdas.sadsa\" exists",
                "width": 200,
                "height": 100,
                "icon": "if"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "condition"
                ],
                "outputs": [
                    "true",
                    "false"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Copy properties",
                "type": "flowNode",
                "desc": "Copies properties from payload to profile",
                "width": 200,
                "height": 100,
                "icon": "copy"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "outputs": [
                    "object"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Store data",
                "type": "flowNode",
                "desc": "Save payload",
                "width": 200,
                "height": 100,
                "icon": "store"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Split flow",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "split"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "input"
                ],
                "outputs": [
                    "output-1",
                    "output-2",
                    "output-3"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Join flow",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "join"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "outputs": [
                    "output"
                ],
                "inputs": [
                    "input-1",
                    "input-2",
                    "input-3"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Log",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "debug"
            },
            "spec": {
                "className": "log",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "outputs": []
            }
        }
    },
{
        "data": {
            "metadata": {
                "name": "Start",
                "type": "flowNode",
                "desc": "Get payload",
                "width": 100,
                "height": 100,
                "icon": "payload"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [],
                "outputs": [
                    "payload"
                ],
                "config": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Raise event",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "event"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "IF Condition",
                "type": "flowNode",
                "desc": "if type=\"dasdas\" asa \"assa.sdsd.asdas.sadsa\" exists",
                "width": 200,
                "height": 100,
                "icon": "if"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "condition"
                ],
                "outputs": [
                    "true",
                    "false"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Copy properties",
                "type": "flowNode",
                "desc": "Copies properties from payload to profile",
                "width": 200,
                "height": 100,
                "icon": "copy"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "outputs": [
                    "object"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Store data",
                "type": "flowNode",
                "desc": "Save payload",
                "width": 200,
                "height": 100,
                "icon": "store"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Split flow",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "split"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "input"
                ],
                "outputs": [
                    "output-1",
                    "output-2",
                    "output-3"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Join flow",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "join"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "outputs": [
                    "output"
                ],
                "inputs": [
                    "input-1",
                    "input-2",
                    "input-3"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Log",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "debug"
            },
            "spec": {
                "className": "log",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "outputs": []
            }
        }
    },
{
        "data": {
            "metadata": {
                "name": "Start",
                "type": "flowNode",
                "desc": "Get payload",
                "width": 100,
                "height": 100,
                "icon": "payload"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [],
                "outputs": [
                    "payload"
                ],
                "config": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Raise event",
                "type": "flowNode",
                "width": 200,
                "height": 100,
                "icon": "event"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "IF Condition",
                "type": "flowNode",
                "desc": "if type=\"dasdas\" asa \"assa.sdsd.asdas.sadsa\" exists",
                "width": 200,
                "height": 100,
                "icon": "if"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "condition"
                ],
                "outputs": [
                    "true",
                    "false"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Copy properties",
                "type": "flowNode",
                "desc": "Copies properties from payload to profile",
                "width": 200,
                "height": 100,
                "icon": "copy"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "outputs": [
                    "object"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },
    {
        "data": {
            "metadata": {
                "name": "Store data",
                "type": "flowNode",
                "desc": "Save payload",
                "width": 200,
                "height": 100,
                "icon": "store"
            },
            "spec": {
                "className": "func",
                "module": "module",
                "inputs": [
                    "payload"
                ],
                "init": {
                    "event": "GET_DATA_FROM_MYSQL"
                }
            }
        }
    },

]

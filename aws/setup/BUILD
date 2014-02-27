[
{ "py_library": {
    "name": "base",
    "py_sources": [ "base.py" ]
} },
{ "py_library": {
    "name": "queue",
    "py_sources": [ "queue.py" ],
    "system_dependencies": [ "boto" ]
} },
{ "py_library": {
    "name": "spot",
    "py_sources": [ "spot.py" ],
    "dependencies": [ "//aws/config:spot" ],
    "system_dependencies": [ "boto" ]
} },
{ "py_library": {
    "name": "autoscale",
    "py_sources": [ "autoscale.py" ],
    "dependencies": [ ":base",
                      "//aws/config:workqueue"
    ],
    "system_dependencies": [ "boto" ]
} },
{ "py_library": {
    "name": "alarm",
    "py_sources": [ "alarm.py" ],
    "dependencies": [ ":base" ],
    "system_dependencies": [ "boto" ]
} },
{ "py_library": {
    "name": "client",
    "py_sources": [ "client.py" ],
    "dependencies": [ ":alarm", 
                      ":autoscale",
                      ":queue",
                      "//aws/config:workqueue" ],
    "system_dependencies": [ "boto" ]
} },
{ "py_binary": {
    "name": "test",
    "py_sources": [ "test.py" ],
    "dependencies": [ ":client",
                      "//common/base:py_flags",
                      "//aws/config:workqueue" ]
} }
]
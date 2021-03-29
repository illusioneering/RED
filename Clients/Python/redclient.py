"""
Python client library for RED.

TODO:
  - Finish adding endpoint functions
  - Make error handling more robust
"""

import requests
import json

# This is the current version of RED
# All functions will default to this version when 
# creating the server URL
cur_version = "v1.0"

class REDServerError(Exception):
    def __init__(self, message):
        self.message = message

class REDClientError(Exception):
    def __init__(self, message):
        self.message = message

class REDConnectionError(Exception):
    def __init__(self, message):
        self.message = message


###############################################################################
#                                                               Admin Functions
###############################################################################

def create_experiment(server, experiment_id, tables, version=cur_version):
    """
    Calls the admin/create-experiment endpoint.

    Arguments:
        - server:string
        - experiment_id:string
        - tables:dictionary
        - version:string (optional, will default to cur_version if not provided)

    Returns:
        - key:string
    """

    server = "%s/red-api/%s/admin/create-experiment" %(server, version)
    json_object = {"tables": list(tables.keys())}
    json_object["experiment_id"] = experiment_id

    response = requests.post(server, json=json_object)

    data = response.json()
    
    if "key" in data:
        return data["key"]
    elif "error" in data:
        raise REDServerError(data["error"])

def get_number_participants(server, experiment_id, key, version=cur_version):
    """
    Calls the admin/get-number-participants endpoint.
    
        Arguments:
            - server:string
            - experiment_id:string
            - key:string
            - version:string (optional, will default to cur_version if not provided)
    
        Returns:
            - n_participants:int
    """
    
    server = "%s/red-api/%s/admin/get-number-participants/%s" %(server, version, experiment_id)
    json_object = {"key": key}

    response = requests.get(server, json=json_object)

    data = response.json()

    if "n_participants" in data:
        return int(data["n_participants"])
    elif "error" in data:
        raise REDServerError(data["error"])
    
def get_participants(server, experiment_id, key, version=cur_version):
    """
    Calls the admin/get-participants endpoint.
    
        Arguments:
            - server:string
            - experiment_id:string
            - key:string
            - version:string (optional, will default to cur_version if not provided)
    
        Returns:
            - participants:list
    """

    server = "%s/red-api/%s/admin/get-participants/%s" %(server, version, experiment_id)
    json_object = {"key": key}

    response = requests.get(server, json=json_object)

    data = response.json()

    if "participants" in data:
        return data["participants"]
    elif "error" in data:
        raise REDServerError(data["error"])

def get_tables(server, experiment_id, key, version=cur_version):
    """
    Calls the admin/get-tables endpoint.
    
        Arguments:
            - server:string
            - experiment_id:string
            - key:string
            - version:string (optional, will default to cur_version if not provided)
    
        Returns:
            - tables:list
    """

    server = "%s/red-api/%s/admin/get-tables/%s" %(server, version, experiment_id)
    json_object = {"key": key}

    response = requests.get(server, json=json_object)

    data = response.json()

    if "tables" in data:
        return data["tables"]
    elif "error" in data:
        raise REDServerError(data["error"])

def get_data(server, experiment_id, participant_id, key, table=None, fmt="JSON", version=cur_version):
    """
    Calls the admin/get-data endpoint.
    
        Arguments:
            - server:string
            - experiment_id:string
            - participant_id:string
            - key:string
            - table:string (optional, will return all tables if not provided)
            - fmt:string (optional, will default to JSON if not provided)
            - version:string (optional, will default to cur_version if not provided)
    
        Returns:
            - data:string
    """
    if table:
        server = "%s/red-api/%s/admin/get-data/%s/%s/%s" %(server, version, experiment_id, participant_id, table)
    else:
        server = "%s/red-api/%s/admin/get-data/%s/%s" %(server, version, experiment_id, participant_id)
    json_object = {"key": key, "format": fmt}

    response = requests.get(server, json=json_object)

    data = response.json()

    if "error" in data:
        raise REDServerError(data["error"])

    if fmt.upper() == "JSON":
        return json.dumps(data, indent="    ")

###############################################################################
#                                                         Participant Functions
###############################################################################

def register_participant(server, experiment_id, version="v1.0", prefix=None, attributes=None):
    """

    """

    server = "%s/red-api/%s/register-participant/%s" %(server, version, experiment_id)
    json_object = {}
    if prefix:
        json_object["prefix"] = prefix
    if attributes:
        json_object["attributes"] = attributes

    response = requests.post(server, json=json_object)

    data = response.json()

    if "participant_id" in data:
        return data["participant_id"]
    elif "error" in data:
        raise REDServerError(data["error"])

def finish_participant(server, experiment_id, participant_id, version="v1.0"):
    """

    """

    server = "%s/red-api/%s/finish-participant/%s/participant_id" %(server, version, experiment_id, participant_id)

    response = request.put(server)

    data = response.json()

    if "error" in data:
        raise REDServerError(data["error"])

def add_data(server, experiment_id, participant_id, table, data, version="v1.0"):
    """

    """

    server = "%s/red-api/%s/add-data/%s/%s/%s" %(server, version, experiment_id, participant_id, table)

    json_object = {"data": data}

    response = requests.put(server, json=json_object)

    if "error" in data:
            raise REDServerError(data["error"])
    

if __name__ == '__main__':
    server = "http://localhost:5000"
    experiment_id = "experiment1"
    tables = {"table1": ["col1", "col2"], "table2": ["col1", "col2"]}
    key = "dcaa6909-fb33-4065-8768-eafe4810eea5"

    #key = create_experiment(server, experiment_id, tables)
    #print(key)

    #print(register_participant(server, experiment_id))
    #n = get_number_participants(server, experiment_id, key)
    #print(n)
    import time
    for _ in range(10):
        add_data(server, experiment_id, "2", "table1", [{"col1": "1", "col2": "2"}])
        #time.sleep(0.001)    

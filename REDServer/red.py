#!/usr/bin/env python3

"""
File: red.py
Author: Jerald Thomas, 2020

Creates endpoints to accomplish remote datalogging tasks for VR experiments.
"""

try:
    from flask import Flask, jsonify, request, abort, make_response, redirect, url_for, render_template, current_app
    from flask_cors import CORS
    import shelve
    import uuid
    import copy
    import time
    import json
    import os
    import re
    import config
except ImportError as error:
    print("Error: %s")
    print("Install dependancies by executing 'pip install -r requirements.txt'")

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    #about Red
    return render_template('REDHome.html')
    

@app.route('/admin')
def admin():
    #show admin control page
    return render_template('REDAdmin.html')


def get_msg_dict(request):
    return dict("")
###############################################################################
#                                                                  Admin Routes
###############################################################################
@app.route('/red-api/v1.0/admin/create-experiment', methods=['POST'])
def create_experiment():
    """
    This endpoint should be called to initialize an experiment database and
    should contain the following fields:
      - experiment_id
      - tables (list)
    """

    #Check to make sure JSON request is made
    json.loads(request.data.decode(request.charset))
    if not request.json:
        return jsonify({"error": "No JSON"}), 400

    if not 'experiment_id' in request.json:
        return jsonify({"error": "No experiment_id"}), 400
    if not "tables" in request.json:
        return jsonify({"error": "No tables"}), 400
    if not type(request.json.get("tables")) == type([]):
        return jsonify({"error": "Tables must be a list"}), 400


    # Check to make sure that config.data_path exists
    if not os.path.isdir(config.data_path):
        os.makedirs(config.data_path) # Create config.data_path
        
    # Check to make sure database does not exist with experiment_id
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, request.json.get('experiment_id')), flag='r')
        db.close()
        return jsonify({"error": "Experiment ID already registered in the system"}), 400
    except:
        pass

    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, request.json.get('experiment_id')), flag='c')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400


    key = str(uuid.uuid4())
    t = time.time()
    db["key"] = key
    db["timestamp_created"] = t
    db["timestamp_modified"] = t
    db["last_participant_id"] = 0
    db["tables"] = request.json.get("tables")
    db["participants"] = {}
    db.close()
    
    return jsonify({"key": key}), 201


@app.route("/red-api/v1.0/admin/remove-experiment/<experiment_id>", methods=["DELETE"])
def remove_experiment(experiment_id):
    """
    Call this endpoint to delete experiment data. Should contain the following
    fields:
      - key
    """
    #Check to make sure JSON request is made
    json.loads(request.data.decode(request.charset))
    if not request.json:
        return jsonify({"error": "No JSON"}), 404
    if not "key" in request.json:
        return jsonify({"error": "No key"}), 400

    pathname = "%s/%s/%s.dat" %(os.getcwd(), config.data_path, experiment_id)


    #Try to delete experiment file
    try:
        os.remove(pathname)
    except OSError as error:
        return jsonify({"error": "Experiment ID not registered in the system"}), 400

    return jsonify({"message": "Deleted experiment %s" %experiment_id}), 200

@app.route("/red-api/v1.0/admin/get-number-participants/<experiment_id>", methods=["GET","POST"])
def get_number_participants(experiment_id):
    """
    Call this endpoint to the number of  experiment participants for the 
    specified experiment. Should contain the following fields:
      - key
    """
    #Check to make sure JSON request is made
    json.loads(request.data.decode(request.charset))
    if not request.json:
        return jsonify({"error": "No JSON"}), 404
    if not "key" in request.json:
        return jsonify({"error": "No key"}), 400

    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, experiment_id), flag='r')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400

    if not request.json.get("key") == db["key"]:
        return jsonify({"error": "Invalid key"}), 403

    return jsonify({"n_participants": len(db["participants"].keys())}), 200

    db.close()
    

@app.route("/red-api/v1.0/admin/get-participants/<experiment_id>", methods=["GET","POST"])
def get_participants(experiment_id):
    """
    Call this endpoint to view a list of experiment participants for the 
    specified experiment. Should contain the following fields:
      - key
    """
    #Check to make sure JSON request is made
    json.loads(request.data.decode(request.charset))
    if not request.json:
        return jsonify({"error": "No JSON"}), 400
    if not "key" in request.json:
        return jsonify({"error": "No key"}), 400

    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, experiment_id), flag='r')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400

    if not request.json.get("key") == db["key"]:
        return jsonify({"error": "Invalid key"}), 403

    #Add participants to table_stats to retrieve each participants data
    participants = []
    for p in db["participants"].keys():
        table_stats = []
        for table in db["participants"][p]["tables"]:
            table_stats.append({"table": table, "n_entries": len(db["participants"][p]["tables"][table])})

        attributes = []

        a = db["participants"][p]["attributes"]
        key = db["key"]

        attributes.append({"key": key, "value": a})

        start_time = db["participants"][p]["start_time"]
        finish_time = db["participants"][p]["finish_time"]

        participants.append({"participant_id": p,
                             "table_stats": table_stats, 
                             "attributes": attributes, 
                             "start_time": start_time,
                             "finish_time": finish_time})
    db.close()        

    return jsonify({"participants": participants}), 200

@app.route("/red-api/v1.0/admin/get-tables/<experiment_id>", methods=["GET", "POST"])
def get_tables(experiment_id):
    """
    Call this endpoint to view a list of experiment data tables for the 
    specified experiment. Should contain the following fields:
      - key
    """
    #Check to make sure JSON request is made
    json.loads(request.data.decode(request.charset))
    if not request.json:
        return jsonify({"error": "No JSON"}), 400
    if not "key" in request.json:
        return jsonify({"error": "No key"}), 400

    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, experiment_id), flag='r')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400

    if not request.json.get("key") == db["key"]:
        return jsonify({"error": "Invalid key"}), 403

    return jsonify({"tables": [t for t in db["tables"]]}), 200

    db.close()
        

@app.route("/red-api/v1.0/admin/get-data/<experiment_id>/<participant_id>/<table>", methods=["GET","POST"])
@app.route("/red-api/v1.0/admin/get-data/<experiment_id>/<participant_id>", methods=["GET","POST"])
def get_data(experiment_id, participant_id, table=None):
    """
    Call this endpoint to view experiment data for the specified experiment,
    participant, and table. Should contain the following fields:
      - key
      - format (optional) [JSON (default), CSV]
    """
    #Check to make sure JSON request is made
    json.loads(request.data.decode(request.charset))
    if not request.json:
        return jsonify({"error": "No JSON"}), 400
    if not "key" in request.json:
        return jsonify({"error": "No key"}), 400

    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, experiment_id), flag='r')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400

    if not request.json.get("key") == db["key"]:
        return jsonify({"error": "Invalid key"}), 403

    if not participant_id in db["participants"]:
        return jsonify({"error": "participant_id not found in list of participants"}), 400

    if table:
        if not table in db["participants"][participant_id]["tables"]:
            return jsonify({"error": "table not associated with experiment_id"}), 400

        tab = db["participants"][participant_id]["tables"][table]

        response = jsonify({table: tab})

    else:
        d = {}
        for table in db["tables"]:
            d[table] = db["participants"][participant_id]["tables"][table]

        response = jsonify(d)

    db.close()
    
    return response, 200

###############################################################################
#                                                            Participant Routes
###############################################################################
 
@app.route('/red-api/v1.0/register-participant/<experiment_id>', methods=['POST'])
def register_participant(experiment_id):
    """
    This endpoint should be called at the beginning of an experiment and
    can contain the following fields:
      - prefix (optional)
      - attributes (optional)

    Will return a unique participant ID. If a prefix is given, the participant
    ID will have that prefix. 
    """
    json.loads(request.data.decode(request.charset))    
    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, experiment_id), flag='c')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400
    
    prefix = None
    if request.json and "prefix" in request.json:
        prefix = request.json.get("prefix")
            
    # Populate participant_id and update participant_id in db
    if prefix:
        if "last_participant_id_%s" %prefix in db:
            participant_id = db["last_participant_id_%s" %prefix] + 1
            db["last_participant_id_%s" %prefix] = participant_id
            participant_id = "%s_%i" %(prefix, participant_id)
        else:
            db["last_participant_id_%s" %prefix] = 1
            participant_id = "%s_1" %prefix
    else:
        participant_id = db["last_participant_id"] + 1
        db["last_participant_id"] = participant_id

    # Create participant data tables
    participant = {"tables": {}}
    for table in db["tables"]:
        participant["tables"][table] = []

    if "attributes" in request.json:
        attr = request.json.get("attributes")      
    else:
        attr = {}
        
    participant["attributes"] = attr
    participant["start_time"] = time.time()
    participant["finish_time"] = 0
    
    participants = db["participants"]        
    participants[str(participant_id)] = copy.deepcopy(participant)
    db["participants"] = participants

    db.close()    
    return jsonify({'participant_id': participant_id}), 201

@app.route('/red-api/v1.0/finish-participant/<experiment_id>/<participant_id>', methods=['PUT'])
def finish_participant(experiment_id, participant_id):
    """
    Call this endpoint to write the finish time of a participants
    experiment to their data file. Should contain the following fields:

    - experiment_id
    - participant_id

    This endpoint should be called at the end of an experiment and returns an empty string

    """
    json.loads(request.data.decode(request.charset))    
    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, experiment_id), flag='w')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400

    if not participant_id in db["participants"]:
        return jsonify({"error": "participant_id not found in list of participants"}), 400

    participants = db["participants"]
    participants[participant_id]["finish_time"] = time.time()
    db["participants"] = participants
    db.close()
    return ' ', 204

@app.route('/red-api/v1.0/add-data/<experiment_id>/<participant_id>/<table>', methods=['PUT'])
def add_data(experiment_id, participant_id, table):
    """
    Call this endpoint to add data to a participants experiment file. Should contain
    the following field:
    - data(list)

    """
    json.loads(request.data.decode(request.charset))
    if not request.json:
        return jsonify({"error": "No JSON"}), 400
    if not "data" in request.json:
        return jsonify({"error": "No data"}), 400
    if not type(request.json.get("data")) == type([]):
        return jsonify({"error": "Data must be a list"}), 400
    
    # Try to open the experiment's data file
    try:
        db = shelve.open('%s/%s.dat' %(config.data_path, experiment_id), flag='w')
    except:
        return jsonify({"error": "Could not open experiment data file"}), 400



    if not participant_id in db["participants"]:
        return jsonify({"error": "participant_id not found in list of participants"}), 400
    
    if not table in db["participants"][participant_id]["tables"]:
        return jsonify({"error": "table not associated with experiment_id"}), 400

    participants = db["participants"] 

    for data in request.json.get("data"):
        participants[participant_id]["tables"][table].append(data)

    db["participants"] = participants

    db.close()

    return '', 204



if __name__ == '__main__':
    app.run(debug=True)

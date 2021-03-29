# RED Server
A REST server implemented with Python and Flask for remote datalogging of experiment data.

**Requirements**:
 - Python 3 (tested with Python 3.8.3)
 - Flask 1+ (tested with Flask 1.1.2) (`pip3 install flask`)
 
**Known major issues**:
 - No spooling is implemented. This currently translates to database access errors when the server gets a lot of very frequent requests (such as adding data from the Unity client on a per-frame basis, which drops about 1 in 5 requests from my observations). The solution would be to add a spooler. This would take requests and add them to a job queue, where a single thread takes the jobs and does them.

## Admin Routes
Admin routes are designed to be called only by machines controlled directly by the experimenter (or colleagues). The main difference is the presence of the experiment key in the JSON body.

### /red-api/v1.0/admin/create-experiment
Initializes an experiment database. Returns an experiment key on success, which will be needed to access all other admin routes for the created experiment.
>**Methods:**  
> -`POST`  
>**Required JSON Elements:**   
> -`string:experiment_id`  
> -`list<string>:tables`  
>**Returned JSON Elements:**  
>-`string:key`  
> *or*  
>-`string:error`  

### /red-api/v1.0/admin/remove-experiment/{{experiment_id}}
Deletes the specified experiment database on success.
>**Methods:**  
> -`DELETE`  
>**Required JSON Elements:**   
> -`string:key`  

### /red-api/v1.0/admin/get-number-participants/{{experiment_id}}
Returns the number of registered participants on success.
>**Methods:**  
> -`POST`, `GET`  
>**Required JSON Elements:**  
> -`string:key`  
>**Returned JSON Elements:**  
>-`int:n_participants`  
> *or*  
>-`string:error`  

### /red-api/v1.0/admin/get-participants/{{experiment_id}}
Returns a list of registered participants on success.
>**Methods:**  
> -`POST`  
>**Required JSON Elements:**   
> -`string:key`  
>**Returned JSON Elements:**  
>-`list<string>:participants`  
> *or*  
>-`string:error`  

### /red-api/v1.0/admin/get-tables/{{experiment_id}}
Returns the experiment tables on success.
>**Methods:**  
> -`POST`, `GET`  
>**Required JSON Elements:**  
> -`string:key`  
>**Returned JSON Elements:**  
>-`list<string>:tables`  
> *or*  
>-`string:error`  

### /red-api/v1.0/admin/get-data/{{experiment_id}}/{{participant_id}}/{{table}} 
Returns the data in the specified table for the specified participant.
>**Methods:**  
> -`POST`, `GET`  
>**Required JSON Elements:**   
> -`string:key`  
>**Optional JSON Elements:**   
> -`string:format -> [JSON, CSV]`  
>**Returned JSON Elements:**  
>-`JSON:[{{table name}}`  
> *or*  
>-`string:error`  

### /red-api/v1.0/admin/get-data/{{experiment_id}}/{{participant_id}}
Returns the data in all tables for the specified participant.
>**Methods:**  
> -`POST`, `GET`  
>**Required JSON Elements:**   
> -`string:key`  
>**Optional JSON Elements:**   
> -`string:format -> [JSON, CSV]`  
>**Returned JSON Elements:**  
>-`JSON:{{table name}}` for all tables  
> *or*  
>-`string:error`  

---

## Participant Routes
Participant routes are designed to be called by machines controlled by the participants. There is **no** experiment key in the JSON body. This way, even if a malicious participant were to determine the server, port, and admin endpoints, they would not have the key and hence would not be able to access the experiment data.

### /red-api/v1.0/register-participant/{{experiment_id}}
Registers the participant with the specified experiment and returns a unique participant ID on success. If prefix is provied, then the participant ID will begin with the provided prefix. If attributes are provided, they will be stored.
>**Methods:**  
> -`POST`  
>**Optional JSON Elements:**  
> -`string:prefix`  
> -`JSON:attributes`  
>**Returned JSON Elements:**  
>-`string:participant_id`  
> *or*  
>-`string:error`  

### /red-api/v1.0/add-data/{{experiment_id}}/{{participant_id}}/{{table}}
Stores the provided data in the specified table, for the specified participant, in the specified experiment's database. The data should be a one or more full rows of the table, with JSON keys being the table column (string), and the JSON values being the data point (string).
>**Methods:**  
> -`PUT`  
>**Required JSON Elements:**   
> -`JSON:data`  
>**Returned JSON Elements:**  
>-Nothing  
> *or*  
>-`string:error`  

### /red-api/v1.0/finish-participant/{{experiment_id}}/{{participant_id}}
Adds a timestamp to the "finish_time" field of the participant's entry.
>**Methods:**  
> -`PUT`  
>**Returned JSON Elements:**  
>-Nothing  
> *or*  
>-`string:error` 

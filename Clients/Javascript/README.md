# Javascript RED Client
A Javascript client for interacting with the RED server from a browser, or to be embedded into web-based game engines.

**Known major issues**:
- Since our initial HTML is loaded over an HTTPS connection, but over an HTTP connection on the Quest, the user recieves a Mixed Content error. We are in the process of fixing this issue by transitioning the entire application to HTTPS.

## Participant Routes
Participant endpoints are designed to be called by machines con-trolled by the participants.

### Definition of Arguments:
> - server: URL of server (i.e. "http://red.cse.umn.edu")
> - participant_id: The ID of the registered participant
> - experiment_id: Unique experiment ID
> - version (optional): RED API version
> - prefix (optional): Participant ID prefix
> - attributes (optional): Attributes for participant

### register_participant()
Creates a particpant record for a given experiment.

>**Required Parameters:**   
> -`string:server`    
> -`string:experiment_id`     
> -`string:version`

>**Optional Parameters:**   
> -`string:prefix`   
> -`JSON:attributes`

>**Returned:**
> - `string:participant_id`

### finish_participant()
Generates a timestamp for the "finish_time" field of a participants entry.

>**Required Parameters:**   
> -`string:server`  
> -`string:experiment_id`   
> -`string:participant_id`

>**Optional Parameters:**   
> -`string:version`

>**Returned:**   
> -Nothing  
> *or*  
> -`string:error` 

### add_data()
Saves given data for participant's experiement in a specified table.


>**Required Parameters:**   
> -`string:server`   
> -`string:experiment_id`    
> -`string:participant_id`   
> -`string:table`    
> -`json:data`

>**Optional Parameters:**   
> -`string:version`

>**Returned:**   
> -Nothing  
> *or*  
> -`string:error` 

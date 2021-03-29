//////////////////////
////Client Routes////
////////////////////


//Register a participant for an experiment
function register_participant(server, experiment_id, version = "v1.0", prefix = "", attributes = "")
{
//Build URL based on parameters
const url = server + "/red-api/" + version + "/register-participant/" + experiment_id

//Make Fetch request to register participant for experiment   
fetch(url, {
    method:'POST',
    headers: 
    {
        'Content-Type': 'application/json'
    }
    ,
    //Sends Json request to create-experiment in proper format
    body: JSON.stringify({
        prefix:prefix,
        attributes:attributes,
    })
})
    //Return string ID of registered participant
    .then(response => { 
        return response.json();
    })
}

//Document the participants experiment end time
function finish_participant(server, experiment_id, participant_id, version = "v1.0",)
{
//Build URL based on parameters
const url = server + "/red-api/" + version + "/finish-participant/" + experiment_id + '/' + participant_id

//Make Fetch request to end participant experiment  
fetch(url, {
    method:'PUT',
    headers: 
    {
        'Content-Type': 'application/json'
    }
    ,
    //Sends Json request to create-experiment in proper format
    body: JSON.stringify({
      experiment_id:experiment_id,
      participant_id:participant_id
    })
})
    //Return N/A or error
    .then(response => { 
        return response.text()
    })
 }

 //Add data to a table in an experiment for a specific participant
function add_data(server, experiment_id, participant_id, table, data, version = "v1.0", )
{
//Create array to store data    
var dataArray = []
 dataArray.push(data)

 //Build URL based on parameters
const url = server + "/red-api/" + version + "/add-data/" + experiment_id + '/' + participant_id + '/' + table

//Make Fetch request to get data
fetch(url, {
    method:'PUT',
    headers: 
    {
        'Content-Type': 'application/json'
    }
    ,
    //Sends Json request to create-experiment in proper format
    body: JSON.stringify({
      data:dataArray
    })
})
    //Return N/A or error
    .then(response => { 
        return response.text()
    })
}

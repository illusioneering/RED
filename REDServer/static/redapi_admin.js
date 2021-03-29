//////////////////////
////Admin Routes////
////////////////////

var tableCounter = 1;
var tableArray = [];

serverVersion = 'v1.0';
server = 'http://' + window.location.host + '/red-api/' + serverVersion ;


function create_experiment()
  {
    //Put user table input into array
    var tablesOuterContainer = document.getElementById("tables");
    var tableInnerContainer = tablesOuterContainer.getElementsByTagName("input")

    for (var i = 0; i<tableCounter-1; i++)
    {
      tableArray.push(tableInnerContainer[i].value)
      
    }
    //Get experiment_id from user input
    experiment_id = document.getElementById('expID').value;

    //Make Fetch request to create an experiment
    const url = server + '/admin/create-experiment'
    fetch(url, {
    method:'POST',
    headers: 
    {
        'Content-Type': 'application/json'
    }
    ,
    //Sends Json request to create-experiment in proper format
    body: JSON.stringify({
        experiment_id: experiment_id,
        tables: tableArray,
    })
})
    //Return JSON elements
    .then(response => { 
        return response.json();
    })
    .then(data => {
      // If error exists in data, there was an server side error 
      if (data["error"]) 
      {
        // Set error div to data["error"]
        throw Error("RED Server Error: " + data["error"]);
      }
     //Display experiment_id, experiment_key and experiment_tables on html page if JSON request is successful 
      document.getElementById('experimentId').innerHTML = "Experiment ID: " + document.getElementById('expID').value
      document.getElementById('experimentKey').innerHTML = "Experiment Key: " + data["key"];
      document.getElementById('experimentTables').innerHTML = "Experiment Tables: " + tableArray.toString();
      
      //Reset HTML page
      tableCounter = 1;
      tableArray = [];
      document.querySelector('form').reset();
      tablesOuterContainer.innerHTML = "";
    })
    .catch(error => {
      //If there is an error, clear experiment_id and experiment_key on html page
      if(error){
        document.getElementById('experimentID').innerHTML = "Experiment ID: ";
        document.getElementById('experimentKey').innerHTML = "Experiment Key: ";
        document.getElementById('experimentTables').innerHTML = "Experiment Tables: ";

        //Reset HTML page 
        tableCounter = 1;
        tableArray = [];
        document.querySelector('form').reset();
        tablesOuterContainer.innerHTML = "";
      }
    });
  }

  //Add table when creating experiment
  function add_to_table()
{ 
  //Get user input number of tables
  var numTables = document.getElementById("tblID").value;

  if(numTables > 0)
  {
    for (i = 0; i < numTables; i++)
    {
      //Create input fields for tables
      var newLabel = document.createElement("p");
      newLabel.innerHTML = "Table " + tableCounter;
      var newDiv = document.createElement('input');
      newDiv.setAttribute("id", "tblID" + tableCounter)
      
      //append elements to "tables" div
      document.getElementById("tables").appendChild(newLabel);
      document.getElementById("tables").appendChild(newDiv);

      //increment table counter
      tableCounter += 1;
    }
  }
}

//Delete an experiment from the database
function remove_experiment()
{
  //Get experiment_id from user input
  experiment_id = document.getElementById('removeID').value;

  //Make Fetch request to remove experiment
  const url = server + '/admin/remove-experiment/' + experiment_id;
  fetch(url, {
  method:'DELETE',
  headers: {
    'Content-Type': 'application/json'
  },
  //Sends Json request to remove-experiment in proper format
  body: JSON.stringify({
    key: document.getElementById('removeKey').value
    })
})
//Return JSON elements
.then(response => { 
  return response.json();
})
  .then(data => {
    // If error exists in data, there was an server side error
    if (data["error"]) 
      {
        throw Error("RED Server Error: " + data["error"]);
      }
    // Set error div to data["error"]
    else
    {
      //Display success message on html page
      document.getElementById('deleteExperiment').innerHTML = data["message"];
    }
  })
  //If there is an error, display error message on html page
  .catch(error => {
      document.getElementById('deleteExperiment').innerHTML = "Error: Experiment not deleted."
  })
}


//Get number of participants in an experiment
function get_number_participants()
{
//Get experiment_id, key from user input
experiment_id = document.getElementById('participantID').value;
key = document.getElementById('participantKey').value;

//Make Fetch request to get number participants
const url = server + '/admin/get-number-participants/' + experiment_id;
fetch(url, {
  method:'POST',
  headers: 
  {
      'Content-Type': 'application/json'
  }
  ,
  //Sends Json request to get-number-participants in proper format
  body: JSON.stringify({
    key: key,
  })
})
  //Return JSON elements
  .then(response => { 
      return response.json();
  })
    .then(data => {
      // If error exists in data, there was an server side error
      if (data["error"]) 
      {
        throw Error("RED Server Error: " + data["error"]);
      }
      //Display number of participants on html page
      document.getElementById('numberOfParticipants').innerHTML = "# of Participants: " + data["n_participants"];
    })
    //If there is an error, display error message on html page
    .catch(error => {
      if(error)
      {
        document.getElementById('numberOfParticipants').innerHTML = "# of Participants: ";
      }
  });
}

//Get participants in an experiment
function get_participants()
{
  //Get experiment_id, key from user input
  experiment_id = document.getElementById('getParticipantsID').value;
  key = document.getElementById('getParticipantsKey').value;
    
  //Make Fetch request to get participants
  const url = server + '/admin/get-participants/' + experiment_id;
  fetch(url, {
    method:'POST',
    headers: 
    {
        'Content-Type': 'application/json'
    }
    ,
    //Sends Json request to get-participants in proper format
    body: JSON.stringify({      
      key:key,
    })
})
  //Return JSON elements
  .then(response => { 
      return response.json();
  })
    .then(data => {
      // If error exists in data, there was an server side error
      if (data["error"]) 
      {
        throw Error("RED Server Error: " + data["error"]);
      }
    
      //Create array of participant names
      participantArray = data["participants"]
      nameArray = []

      //Display participants on html page
      participantName = participantArray.forEach((name) =>{
        nameArray.push("<br>" + name["participant_id"])
      })
      document.getElementById('getParticipants').innerHTML = "Experiment "  + experiment_id + " Participants: " +  nameArray
      })
      //If there is an error, display error message on html page
      .catch(error => {
        if(error)
        {
          document.getElementById('getParticipants').innerHTML = error;
        }
    });
}


//Get tables in an experiment
function get_tables()
{
  //Get experiment_id, key from user input
  experiment_id = document.getElementById('getTablesID').value;
  key = document.getElementById('getTablesKey').value;

  //Make Fetch request to get tables
    const url = server + '/admin/get-tables/' + experiment_id;
    fetch(url, {
      method:'POST',
      headers: 
      {
          'Content-Type': 'application/json'
      }
      ,
      //Sends Json request to get-tables in proper format
      body: JSON.stringify({
        key: document.getElementById('getTablesKey').value,
      })
  })
    //Return JSON elements
    .then(response => { 
        return response.json();
    })
      .then(data => {
        // If error exists in data, there was an server side error
        if (data["error"]) 
        {
          throw Error("RED Server Error: " + data["error"]);
        }
        //Display tables on html page
        document.getElementById('getTables').innerHTML = "Experiment " + "'" + experiment_id + "'" + " Tables: " + data["tables"];
      })
      //If there is an error, display error message on html page
      .catch(error => {
          if(error)
          {
            document.getElementById('getTables').innerHTML = "Experiment " + "'" + experiment_id + "'" + " Tables: ";
          }
      });  
}


//Get participant data from experiment
function get_data()
{
  //Get experiment_id, participant_id, table, key from user input
  experiment_id = document.getElementById('getDataID').value;
  participant_id = document.getElementById('getDataParticipant').value;
  table = document.getElementById('getDataTable').value;
  key = document.getElementById('getDataKey').value;
  //fmt = 'JSON';

  //Make Fetch request to get data
  const url = server + '/admin/get-data/' + experiment_id + "/" + participant_id + "/" + table;
  fetch(url, {
    method:'POST',
    headers: 
    {
        'Content-Type': 'application/json'
    }
    ,
    //Sends Json request to create-experiment in proper format
    body: JSON.stringify({
      key:key,
      //fmt: fmt,
    })
})
    .then(response => { 
        return response.json();
    })
      .then(data => {
        // If error exists in data, there was an server side error
        if (data["error"]) 
        {
          throw Error("RED Server Error: " + data["error"]);
        }      
        
        //Download data as json file to computer
        var json = data[document.getElementById("getDataTable").value]
        json = [json]
        var blob  = new Blob(json, {type:"text/plain;charset=utf-8" })

        //Check the Browser.
        var isIE = false || !!document.documentMode;
        if (isIE) {
            window.navigator.msSaveBlob(blob, table + ".txt");
        } else {
            var url = window.URL || window.webkitURL;
            link = url.createObjectURL(blob);
            var newlink = document.createElement("a");
            newlink.download = table + ".txt";
            newlink.href = link;
            document.body.appendChild(newlink);
            newlink.click();
            document.body.removeChild(newlink);
          }
          //Display success message after download
          document.getElementById('getData').innerHTML = "The data file containing Table: " + table  + " in Experiment: " + experiment_id + " has downloaded.";
        })
        //If there is an error, display error message on html page
        .catch(error => {
            if(error)
            {
              document.getElementById('getData').innerHTML = "Error downloading the data file.";
            }
        });
}
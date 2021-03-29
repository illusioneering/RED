using System.Collections;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using System.Net.Http;
using System.Threading;
using System.IO;
using UnityEngine;

[System.Serializable]
public class REDResponseMessage
{
    public string error;
    public string key;
    public string participant_id;
    public List<REDParticipant> participants;
    public int n_participants;

    public static REDResponseMessage FromJSON(string jsonString)
    {
        return JsonUtility.FromJson<REDResponseMessage>(jsonString);
    }
}

[System.Serializable]
public class REDTable
{
    public string name;
    public List<string> columns = new List<string>();
}

[System.Serializable]
public class REDParticipant
{
    public string participant_id;
    public int start_time;
    public int finish_time;
    public List<REDParticipantAttribute> attributes;
    public List<REDParticipantTableStats> table_stats;
}

[System.Serializable]
public class REDParticipantAttribute
{
    public string key;
    public string value;
}

[System.Serializable]
public class REDParticipantTableStats
{
    public string table;
    public int n_entries;
}

public class REDManager : MonoBehaviour
{
    [SerializeField][Tooltip("RED server URL")]
    private string host = "127.0.0.1";
    [SerializeField][Tooltip("RED server port")]
    private int port = 5000;
    [SerializeField][Tooltip("Experiment ID")]
    private string experiment_id = "my_experiment";
    [SerializeField][Tooltip("List of tables/columns for data collection")]
    private List<REDTable> tables = new List<REDTable>();
    [SerializeField][Tooltip("List of registerd participants")]
    private List<REDParticipant> participants = new List<REDParticipant>();
    [SerializeField][Tooltip("Experiment key. Can copy/paste to access experiment data with other clients")]
    private string key = "";
    // will make available to edit when another version is released.
    private string api_version = "v1.0";
    // For use in updating participants list
    [SerializeField]
    private int n_participants = 0;

    [SerializeField][Tooltip("Prefix to add to participant IDs")]
    private string prefix = "";
    [SerializeField][Tooltip("Current participant ID (for debugging)")]
    private string participant_id;
    [SerializeField][Tooltip("Current participant hardware ID (for debugging)")]
    private string participant_hardware_id;

    [SerializeField][Tooltip("Path to store acquired data")]
    private string data_path = "Data/";
    [SerializeField]
    private enum DataFormat{JSON, CSV};
    [SerializeField][Tooltip("Format of acquired data (Not yet implimented)")]
    private DataFormat data_format = DataFormat.JSON;
    [SerializeField][Tooltip("Set to true to remove existing data at [data_path]")]
    private bool remove_existing_data = true;
    [SerializeField][Tooltip("Set to true to have data compressed (Not yet implimented)")]
    private bool zip_data = false;

    // Threading objects for asynchronous sending of data
    private Thread send_thread;
    private readonly object queue_lock = new object();
    private volatile Queue<KeyValuePair<string, Dictionary<string, string>>> send_queue = new Queue<KeyValuePair<string, Dictionary<string, string>>>();
    private volatile bool send_thread_running = true;
    
    async Task Awake()
    {
        // Get hardware ID
        participant_hardware_id = SystemInfo.deviceUniqueIdentifier;

        // Create and start send thread
        send_thread = new Thread(new ThreadStart(ThreadJob));
        send_thread.Start();

        // Register the participant
        await RegisterParticipant();
    }

    void OnApplicationQuit()
    {
        // Stop the send thread on application quit
        lock (queue_lock)
        {
            send_thread_running = false;
        }
    }

    public void EnqueueData(string table, Dictionary<string, string> data)
    {
        lock (queue_lock)
        {
            send_queue.Enqueue(new KeyValuePair<string, Dictionary<string, string>>(table, data));
        }
    }

    void ThreadJob()
    {
        // Wait for valid participant ID
        while (participant_id == "");

        // Ends thread execution when application quits
        // (assuming the application quits gracefully and flag is set)
        while (send_thread_running)
        {
            // Putting this here ensures that the queue is emptied before the 
            // thread terminates.
            while (send_queue.Count > 0)
            {
                lock (queue_lock)
                {
                    var to_send = send_queue.Dequeue();
                    SendData(to_send.Key, to_send.Value).ConfigureAwait(false);
                }
            }
        }
    }

    public async Task CreateExperiment()
    {
        // Make sure necessary variables are present
        if (experiment_id == "")
        {
            Debug.LogError("RED: Experiment ID must not be empty.");
            return;
        }
        if (tables.Count == 0)
        {
            Debug.LogError("RED: Experiment settings must have at least one table.");
            return;
        }

        // Create list of tables
        StringBuilder builder = new StringBuilder();
        foreach (REDTable t in tables)
        {
            builder.Append("\"").Append(t.name).Append("\",");
        }

        // Create JSON message
        string msg = string.Format("{{\"experiment_id\": \"{0}\", \"tables\": [{1}]}}", experiment_id, builder.ToString().TrimEnd(','));

        // Call RED endpoint
        using (var client = new HttpClient())
        {
            var response = await client.PostAsync(
                string.Format("http://{0}:{1}/red-api/{2}/admin/create-experiment", host, port, api_version),
                new StringContent(msg, Encoding.UTF8, "application/json"));

            string content = await response.Content.ReadAsStringAsync();

            REDResponseMessage redResponse = REDResponseMessage.FromJSON(content);
            if (response.IsSuccessStatusCode)
            {
                if (redResponse.key != null)
                {
                    key = redResponse.key;
                }
            }
            else
            {
                if (redResponse.error != null)
                {
                    Debug.LogError(string.Format("RED: Response Error ({0})", redResponse.error));
                }
            }
        }

    }

    public async Task GetNumberOfParticipants()
    {
        // Make sure necessary variables are present
        if (key == "")
            return;

        // Create JSON message
        string msg = string.Format("{{\"key\": \"{0}\"}}", key);

        // Call RED endpoint
        using (var client = new HttpClient())
        {
            var response = await client.PostAsync(
                string.Format("http://{0}:{1}/red-api/{2}/admin/get-number-participants/{3}", host, port, api_version, experiment_id),
                new StringContent(msg, Encoding.UTF8, "application/json"));

            string content = await response.Content.ReadAsStringAsync();

            REDResponseMessage redResponse = REDResponseMessage.FromJSON(content);
            if (response.IsSuccessStatusCode)
            {
                if (redResponse.n_participants != 0)
                {
                    n_participants = redResponse.n_participants;
                }
            }
            else
            {
                if (redResponse.error != null)
                {
                    Debug.LogError(string.Format("RED: Response Error ({0})", redResponse.error));
                }
            }
        }
    }

    public async Task GetParticipants()
    {
        // Make sure necessary variables are present
        if (key == "")
            return;

        // Create JSON message
        string msg = string.Format("{{\"key\": \"{0}\"}}", key);

        // Call RED endpoint
        using (var client = new HttpClient())
        {
            var response = await client.PostAsync(
                string.Format("http://{0}:{1}/red-api/{2}/admin/get-participants/{3}", host, port, api_version, experiment_id),
                new StringContent(msg, Encoding.UTF8, "application/json"));

            string content = await response.Content.ReadAsStringAsync();
            Debug.Log(content);

            REDResponseMessage redResponse = REDResponseMessage.FromJSON(content);
            if (response.IsSuccessStatusCode)
            {
                if (redResponse.participants != null)
                {
                    participants.Clear();
                    foreach (REDParticipant p in redResponse.participants)
                    {
                        participants.Add(p);
                    }
                }
            }
            else
            {
                if (redResponse.error != null)
                {
                    Debug.LogError(string.Format("RED: Response Error ({0})", redResponse.error));
                }
            }
        }
    }

    public async Task AcquireData()
    {
        // Make sure necessary variables are present
        if (key == "")
            return;

        // Update list of participants
        await GetParticipants();
            
        string line;

        // Create JSON message
        string msg = string.Format("{{\"key\": \"{0}\"}}", key);
        
        // These are mainly just here to stop the "unused variable" warning...
        if (zip_data)
        {
            Debug.LogWarning("RED: Zip data not yet implemented.");
        }
        if (data_format == DataFormat.CSV)
        {
            Debug.LogWarning("RED: CSV data format not yet implemented, defaulting to JSON.");
        }
        
        // Will use temp path when zip functionality is added
        //string tmp_path = Application.temporaryCachePath + "/RED";
        string tmp_path = data_path;

        // Remove existing data directory if told to
        if (remove_existing_data && Directory.Exists(tmp_path))
        {
            Directory.Delete(tmp_path, true);
        }

        // Create data directory
        DirectoryInfo tmp_dir = Directory.CreateDirectory(tmp_path);
        // Create participants subdirectory
        Directory.CreateDirectory(tmp_path + "/participants");

        // Creat and populate table subdirectories
        foreach (REDTable t in tables)
        {
            Directory.CreateDirectory(tmp_path + "/" + t.name);
            // Within each table subdirectory, create a file for each participant
            foreach (REDParticipant p in participants)
            {
                // Get the data for the specified participant and table and write the file
                using (var client = new HttpClient())
                {
                    var response = await client.PostAsync(
                        string.Format("http://{0}:{1}/red-api/{2}/admin/get-data/{3}/{4}/{5}", host, port, api_version, experiment_id, p.participant_id, t.name),
                        new StringContent(msg, Encoding.UTF8, "application/json"));


                    if (response.IsSuccessStatusCode)
                    {
                        Stream stream = await response.Content.ReadAsStreamAsync();
                        StreamReader reader = new StreamReader(stream);
                        using (StreamWriter writer = new StreamWriter(string.Format("{0}/{1}/{2}.json", tmp_path, t.name, p.participant_id)))
                        {
                            while ((line = reader.ReadLine()) != null)
                            {
                                writer.WriteLine(line);
                            }
                        }
                    }
                    else
                    {
                        string content = await response.Content.ReadAsStringAsync();
                        REDResponseMessage redResponse = REDResponseMessage.FromJSON(content);
                        if (redResponse.error != null)
                        {
                            Debug.LogError(string.Format("RED: Response Error ({0})", redResponse.error));
                        }
                    }
                }
            }
        }

        //System.IO.Compression.FileSystem.ZipFile.CreateFromDirectory(tmp_path, data_path + "REDData.zip");
        Debug.Log("Finished acquiring data, located in [" + tmp_path + "].");
    }

    public async Task RegisterParticipant()
    {
        // Make sure necessary variables are present
        if (key == "")
        {
            Debug.LogError("RED: Experiment does not have a valid key.");
            return;
        }
        if (experiment_id == "")
        {
            Debug.LogError("RED: Experiment ID must not be empty.");
            return;
        }

        // Create JSON message
        string msg = "";
        if (prefix == "")
        {
            msg = string.Format("{{\"experiment_id\": \"{0}\", \"attributes\": {{\"hardware_id\": \"{1}\"}}}}", experiment_id, participant_hardware_id);
        }
        else
        {
            msg = string.Format("{{\"experiment_id\": \"{0}\", \"prefix\": \"{1}\", \"attributes\": {{\"hardware_id\": \"{2}\"}}}}", experiment_id, prefix, participant_hardware_id);
        }

        // Call RED endpoint
        using (var client = new HttpClient())
        {
            var response = await client.PostAsync(
                string.Format("http://{0}:{1}/red-api/{2}/register-participant/{3}", host, port, api_version, experiment_id),
                new StringContent(msg, Encoding.UTF8, "application/json"));

            string content = await response.Content.ReadAsStringAsync();

            REDResponseMessage redResponse = REDResponseMessage.FromJSON(content);
            if (response.IsSuccessStatusCode)
            {
                if (redResponse.participant_id != null)
                {
                    participant_id = redResponse.participant_id;
                }
            }
            else
            {
                if (redResponse.error != null)
                {
                    Debug.LogError(string.Format("RED: Response Error ({0})", redResponse.error));
                }
            }
        }
    }

    public async Task FinishParticipant()
    {
        // Call RED endpoint
        using (var client = new HttpClient())
        {
            var response = await client.PutAsync(
                string.Format("http://{0}:{1}/red-api/{2}/finish-participant/{3}/{4}", host, port, api_version, experiment_id, participant_id),
                new StringContent("{}", Encoding.UTF8, "application/json"));

            string content = await response.Content.ReadAsStringAsync();

            REDResponseMessage redResponse = REDResponseMessage.FromJSON(content);
            if (!response.IsSuccessStatusCode)
            {
                if (redResponse.error != null)
                {
                    Debug.LogError(string.Format("RED: Response Error ({0})", redResponse.error));
                }
            }
        }
    }

    public async Task SendData(string table, Dictionary<string, string> data)
    {
        // Create JSON message
        StringBuilder builder = new StringBuilder();
        foreach (KeyValuePair<string, string> pair in data)
        {
            builder.Append('\"').Append(pair.Key).Append("\":\"").Append(pair.Value).Append("\",");
        }
        string msg = string.Format("{{\"data\": [{{{0}}}]}}", builder.ToString().TrimEnd(','));

        // Call RED endpoint
        using (var client = new HttpClient())
        {
            var response = await client.PutAsync(
                string.Format("http://{0}:{1}/red-api/{2}/add-data/{3}/{4}/{5}", host, port, api_version, experiment_id, participant_id, table),
                new StringContent(msg, Encoding.UTF8, "application/json"));

            string content = await response.Content.ReadAsStringAsync();

            REDResponseMessage redResponse = REDResponseMessage.FromJSON(content);
            if (!response.IsSuccessStatusCode)
            {
                if (redResponse.error != null)
                {
                    Debug.LogError(string.Format("RED: Response Error ({0})", redResponse.error));
                }
            }
        }
    }
}

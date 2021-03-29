using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Transform : MonoBehaviour
{
    public REDManager redManager;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        redManager.EnqueueData("transform", CreateDataEntry());
    }

    Dictionary<string, string> CreateDataEntry()
    {
        Vector3 pos = transform.position;

        Dictionary<string, string> d = new Dictionary<string, string>();
        d.Add("timestamp", Time.time.ToString());
        d.Add("x", pos.x.ToString());
        d.Add("y", pos.y.ToString());
        d.Add("z", pos.z.ToString());

        return d;
    }
}

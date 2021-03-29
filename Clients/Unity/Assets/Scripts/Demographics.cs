using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Demographics : MonoBehaviour
{
    public REDManager redManager;

    public int age;
    public string gender;

    // Start is called before the first frame update
    void Start()
    {
       redManager.EnqueueData("demographics", new Dictionary<string, string>(){{"age", age.ToString()}, {"gender", gender}});
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}

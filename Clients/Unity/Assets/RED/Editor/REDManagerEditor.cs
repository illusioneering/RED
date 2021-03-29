using UnityEngine;
using UnityEditor;
using System.Collections;
using System.Collections.Generic;


[CustomEditor(typeof(REDManager))]
public class REDManagerEditor : Editor
{
    // Reference to the REDManager script
    REDManager redManager;

    // Grab all of the script properties
    SerializedProperty host;
    SerializedProperty port;
    SerializedProperty experiment_id;
    SerializedProperty tables;
    SerializedProperty participants;
    SerializedProperty n_participants;
    SerializedProperty key;

    SerializedProperty prefix;
    SerializedProperty attribute_keys;
    SerializedProperty attribute_values;

    SerializedProperty data_path;
    SerializedProperty data_format;
    SerializedProperty remove_existing_data;
    SerializedProperty zip_data;

    SerializedProperty participant_id;
    SerializedProperty participant_hardware_id;
    
    void OnEnable()
    {
        // Populate redManager reference
        redManager = (REDManager) target;

        // Populate REDManager properties
        host = serializedObject.FindProperty("host");
        port = serializedObject.FindProperty("port");
        experiment_id = serializedObject.FindProperty("experiment_id");
        tables = serializedObject.FindProperty("tables");

        prefix = serializedObject.FindProperty("prefix");
        attribute_keys = serializedObject.FindProperty("attribute_keys");
        attribute_values = serializedObject.FindProperty("attribute_values");

        data_path = serializedObject.FindProperty("data_path");
        data_format = serializedObject.FindProperty("data_format");
        remove_existing_data = serializedObject.FindProperty("remove_existing_data");
        zip_data = serializedObject.FindProperty("zip_data");

        key = serializedObject.FindProperty("key");

        participants = serializedObject.FindProperty("participants");
        n_participants = serializedObject.FindProperty("n_participants");

        participant_id = serializedObject.FindProperty("participant_id");
        participant_hardware_id = serializedObject.FindProperty("participant_hardware_id");

    }

    public override void OnInspectorGUI()
    {
        serializedObject.Update();

          // This bit will update the participant list automatically
          // But it does it quite frequently
          // I have it commentented out for debugging...
       // redManager.GetNumberOfParticipants();
       // if (n_participants.intValue != participants.arraySize)
       // {
       //     redManager.GetParticipants();
       // }
        
        using (new EditorGUI.DisabledScope(key.stringValue != ""))
        {
            GUILayout.Label("Server Settings", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(host);
            EditorGUILayout.PropertyField(port);

            EditorGUILayout.Space();
            GUILayout.Label("Experiment Settings", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(experiment_id, new GUIContent("Experiment ID"));
            EditorGUILayout.PropertyField(tables, new GUIContent(string.Format("Tables ({0})", tables.arraySize)));

            
        }

        if (key.stringValue == "")
        {
            EditorGUILayout.Space();
            if (GUILayout.Button("Create RED Experiment"))
            {
                redManager.CreateExperiment();
            }
        }

        else
        {
            using (new EditorGUI.DisabledScope(true))
            {
                EditorGUILayout.PropertyField(participants, new GUIContent(string.Format("Participants ({0})", participants.arraySize)));
                EditorGUILayout.PropertyField(key);
                
            }

            EditorGUILayout.Space();
            GUILayout.Label("Particpant Settings", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(prefix);
            using (new EditorGUI.DisabledScope(true))
            {
                EditorGUILayout.PropertyField(participant_id, new GUIContent("Participant ID"));
                EditorGUILayout.PropertyField(participant_hardware_id, new GUIContent("Hardware ID"));
            }

            EditorGUILayout.Space();
            GUILayout.Label("Data Acquisition", EditorStyles.boldLabel);
            EditorGUILayout.PropertyField(data_path, new GUIContent("Data Path"));
            using (new EditorGUI.DisabledScope(true)){EditorGUILayout.PropertyField(data_format, new GUIContent("Data Format"));}
            EditorGUILayout.PropertyField(remove_existing_data, new GUIContent("Remove Existing Data?"));
            using (new EditorGUI.DisabledScope(true)){EditorGUILayout.PropertyField(zip_data, new GUIContent("Zip Data?"));}
            if (GUILayout.Button("Acquire Data"))
            {
                redManager.AcquireData();
            }
        }

        serializedObject.ApplyModifiedProperties();
    }
}

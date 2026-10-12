using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

[InitializeOnLoad]
public static class CapacityCollisionProbe
{
    static string Root => Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
    static string Pending => Path.Combine(Root, "probe-pending.txt");
    static CapacityCollisionProbe() { EditorApplication.playModeStateChanged += OnPlayMode; }
    public static void Run()
    {
        File.WriteAllText(Pending, DateTime.UtcNow.ToString("o"));
        EditorApplication.EnterPlaymode();
    }
    static void OnPlayMode(PlayModeStateChange state)
    {
        if (state != PlayModeStateChange.EnteredPlayMode || !File.Exists(Pending)) return;
        try
        {
            var report = Execute();
            File.WriteAllText(Path.Combine(Root, "probe-results.json"), JsonUtility.ToJson(report, true));
            File.Delete(Pending);
            Debug.Log("CAPACITY_PHYSICS_PROBE_COMPLETED: " + Path.Combine(Root, "probe-results.json"));
            EditorApplication.Exit(0);
        }
        catch (Exception error)
        {
            File.WriteAllText(Path.Combine(Root, "probe-error.txt"), error.ToString());
            Debug.LogException(error);
            EditorApplication.Exit(2);
        }
    }
    [Serializable] public class Report
    {
        public string generatedAt, unityVersion, method;
        public bool isPlaying, fullClientRun = false, capacity5000Validated = false;
        public float radius = .38f, height = 1.8f, stepOffset = .35f, skinWidth = .057f, gravityPerMove = 20f, dt = .02f;
        public Vector3 remoteCubeScale = Vector3.one;
        public string remoteCubeRoot = "feet position at world y=0; default Cube extends from -0.5 to +0.5 y";
        public bool defaultLayerCollides;
        public List<Case> cases = new List<Case>();
        public OverlapCase directTransform;
    }
    [Serializable] public class Case
    {
        public string id;
        public bool obstacleEnabled, anySideCollision, crossedObstaclePlane, traversedBeyondObstacle, remoteHasBoxCollider;
        public Vector3 start, finish, intendedFinish, remoteBoxSize, remoteBoundsSize;
        public float maxFeetHeight, minRootDistance;
        public int blockedFrames;
        public List<Vector3> samples = new List<Vector3>();
    }
    [Serializable] public class OverlapCase
    {
        public Vector3 localBefore, remoteBefore, localAfterTransform, remoteAfterTransform, localAfterSimulate, remoteAfterSimulate, localAfterZeroMove;
        public bool boundsOverlapAfterSync, boundsOverlapAfterSimulate;
        public float centerDistanceAfterSync;
    }
    static readonly List<GameObject> Owned = new List<GameObject>();
    static GameObject Add(GameObject go) { Owned.Add(go); return go; }
    static void Clear()
    {
        foreach (var go in Owned) if (go != null) UnityEngine.Object.DestroyImmediate(go);
        Owned.Clear();
        Physics.SyncTransforms();
    }
    static void Ground()
    {
        var floor = Add(GameObject.CreatePrimitive(PrimitiveType.Cube));
        floor.name = "Probe floor";
        floor.transform.position = new Vector3(0, -.5f, 0);
        floor.transform.localScale = new Vector3(40, 1, 40);
    }
    static CharacterController Local(Vector3 feet)
    {
        var go = Add(GameObject.CreatePrimitive(PrimitiveType.Cube));
        go.name = "Local player source-equivalent controller";
        foreach (var collider in go.GetComponents<Collider>())
        {
            collider.enabled = false;
            UnityEngine.Object.DestroyImmediate(collider);
        }
        var c = go.AddComponent<CharacterController>();
        c.height = 1.8f; c.radius = .38f; c.center = Vector3.up * .9f;
        c.stepOffset = .35f; c.slopeLimit = 45f; c.skinWidth = .057f; c.minMoveDistance = 0;
        c.enabled = false; go.transform.position = feet; c.enabled = true;
        foreach (var mesh in go.GetComponentsInChildren<MeshRenderer>(true)) mesh.enabled = false;
        return c;
    }
    static GameObject Remote(Vector3 feet, bool enabled)
    {
        var go = Add(GameObject.CreatePrimitive(PrimitiveType.Cube));
        go.name = "Remote player source-equivalent default cube";
        go.transform.position = feet;
        foreach (var mesh in go.GetComponentsInChildren<MeshRenderer>(true)) mesh.enabled = false;
        go.GetComponent<BoxCollider>().enabled = enabled;
        return go;
    }
    static Case Walk(string id, Vector3 start, Vector3 velocity, bool obstacle)
    {
        Clear(); Ground();
        var local = Local(start);
        var remote = Remote(Vector3.zero, obstacle);
        Physics.SyncTransforms();
        var box = remote.GetComponent<BoxCollider>();
        var result = new Case { id = id, obstacleEnabled = obstacle, start = start, intendedFinish = start + velocity * .02f * 120,
            remoteHasBoxCollider = box != null, remoteBoxSize = box.size, remoteBoundsSize = box.bounds.size, minRootDistance = float.MaxValue };
        Vector3 forward = velocity.normalized;
        for (int i = 0; i < 120; i++)
        {
            var before = local.transform.position;
            var flags = local.Move(velocity * .02f + Vector3.down * (20f * .02f));
            Physics.SyncTransforms();
            Physics.Simulate(.02f);
            var now = local.transform.position;
            if ((flags & CollisionFlags.Sides) != 0) result.anySideCollision = true;
            if (Vector3.Dot(now - before, forward) < velocity.magnitude * .02f * .25f) result.blockedFrames++;
            result.maxFeetHeight = Mathf.Max(result.maxFeetHeight, now.y);
            result.minRootDistance = Mathf.Min(result.minRootDistance, new Vector2(now.x, now.z).magnitude);
            if (Vector3.Dot(now, forward) > 0) result.crossedObstaclePlane = true;
            if (Vector3.Dot(now, forward) > 1.0f) result.traversedBeyondObstacle = true;
            if (i % 10 == 0 || i == 119) result.samples.Add(now);
        }
        result.finish = local.transform.position;
        return result;
    }
    static OverlapCase TransformOverlap()
    {
        Clear(); Ground();
        var local = Local(Vector3.zero);
        var remote = Remote(new Vector3(3, 0, 0), true);
        Physics.SyncTransforms();
        var box = remote.GetComponent<BoxCollider>();
        var result = new OverlapCase { localBefore = local.transform.position, remoteBefore = remote.transform.position };
        remote.transform.position = local.transform.position; // same type of direct-transform write as remote interpolation
        Physics.SyncTransforms();
        result.localAfterTransform = local.transform.position;
        result.remoteAfterTransform = remote.transform.position;
        result.centerDistanceAfterSync = Vector3.Distance(local.transform.position, remote.transform.position);
        result.boundsOverlapAfterSync = local.bounds.Intersects(box.bounds);
        Physics.Simulate(.02f);
        result.localAfterSimulate = local.transform.position;
        result.remoteAfterSimulate = remote.transform.position;
        result.boundsOverlapAfterSimulate = local.bounds.Intersects(box.bounds);
        local.Move(Vector3.zero);
        result.localAfterZeroMove = local.transform.position;
        return result;
    }
    static Report Execute()
    {
        Physics.simulationMode = SimulationMode.Script;
        Physics.autoSyncTransforms = false;
        var report = new Report { generatedAt = DateTime.UtcNow.ToString("o"), unityVersion = Application.unityVersion,
            isPlaying = Application.isPlaying, defaultLayerCollides = !Physics.GetIgnoreLayerCollision(0,0),
            method = "Independent minimal Unity PlayMode, source-equivalent local controller settings and remote primitive construction. No game scene, art, navmesh, networking or 5000 actors." };
        report.cases.Add(Walk("control_no_remote_collider", new Vector3(-3,0,0), new Vector3(3,0,0), false));
        report.cases.Add(Walk("approach_west", new Vector3(-3,0,0), new Vector3(3,0,0), true));
        report.cases.Add(Walk("approach_east", new Vector3(3,0,0), new Vector3(-3,0,0), true));
        report.cases.Add(Walk("approach_south", new Vector3(0,0,-3), new Vector3(0,0,3), true));
        report.cases.Add(Walk("approach_north", new Vector3(0,0,3), new Vector3(0,0,-3), true));
        report.cases.Add(Walk("offset_graze", new Vector3(-3,0,.65f), new Vector3(3,0,0), true));
        report.cases.Add(Walk("diagonal_corner", new Vector3(-2.2f,0,-2.2f), new Vector3(3,0,3).normalized*3, true));
        report.directTransform = TransformOverlap();
        Clear();
        return report;
    }
}


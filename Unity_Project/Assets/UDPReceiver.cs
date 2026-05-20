using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

[System.Serializable]
public class ArucoData
{
    public int id;
    public float tx;
    public float ty;
    public float tz;
    public float rx;
    public float ry;
    public float rz;
}

public class UDPReceiver : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 5050;

    private ArucoData latestData = new ArucoData();
    private bool isDataNew = false;
    private bool isRunning = true;

    private readonly object dataLock = new object();

    void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        Debug.Log("UDP Start, Port : " + port);
    }

    private void ReceiveData()
    {
        try
        {
            client = new UdpClient(port);
            while (isRunning)
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);

                byte[] data = client.Receive(ref anyIP);

                if(data != null && data.Length > 0)
                {
                    string text = Encoding.UTF8.GetString(data);
                    ArucoData parsedData = JsonUtility.FromJson<ArucoData>(text);

                    lock(dataLock)
                    {
                        latestData = parsedData;
                        isDataNew = true;
                    }
                }
            }
        }
        catch (SocketException)
        {
            Debug.Log("UDP inconneted");
        }
        catch (System.Exception e)
        {
            Debug.LogWarning("EEROR" + e.ToString());
        }
    }

    void Update()
    {
        ArucoData dataToUse = null;
        bool hasNewData = false;

        lock (dataLock)
        {
            if(isDataNew)
            {
                dataToUse = latestData;
                isDataNew = false;
                hasNewData = true;
            }
        }

        if(hasNewData && dataToUse != null)
        {
            float unityX = dataToUse.tx;
            float unityY = -dataToUse.ty;
            float unityZ = dataToUse.tz;

            transform.position = new Vector3(unityX, unityY, unityZ);
        }
    }

    void OnDestroy()
    {
        isRunning = false;

        if (client != null)
        {
            client.Close();
        }

        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Join(100);
        }

        Debug.Log("UDP closed");
    }

}




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

    void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        Debug.Log("UDP Start, Port : " + port);
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while(true)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);

                ArucoData parsedData = JsonUtility.FromJson<ArucoData>(text);
                latestData = parsedData;
                isDataNew = true;
            }
            catch (System.Exception e)
            {
                Debug.Log(e.ToString());
            }
        }
    }

    void Update()
    {
        if (isDataNew)
        {
            float unityX = latestData.tx;
            float unityY = -latestData.ty;
            float unityZ = latestData.tz;

            transform.position = new Vector3(unityX, unityY, unityZ);
            isDataNew = false;
        }
    }

    void OnApplicationQiut()
    {
        if (receiveThread != null) receiveThread.Abort();
        if (client != null) client.Close();
    }

}




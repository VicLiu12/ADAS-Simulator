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
    public int port = 5052;

    private ArucoData latestData = new ArucoData();
    private bool isDataNew = false;
    private bool isRunning = true;

    //避免兩端資料使用同一個變數
    private readonly object dataLock = new object();

    void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true; //若關閉編輯器，主程式會一起關閉
        receiveThread.Start();
        Debug.Log("UDP Start, Port : " + port);
    }

    //接收port傳過來的資料
    private void ReceiveData()
    {
        try
        {
            client = new UdpClient(port);
            while (isRunning)
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                //等待接收資料，並以byte形式存進data
                byte[] data = client.Receive(ref anyIP);

                if(data != null && data.Length > 0)
                {
                    string text = Encoding.UTF8.GetString(data);  //依照UTF8翻譯成看得懂的JSON字串
                    ArucoData parsedData = JsonUtility.FromJson<ArucoData>(text);  //把JSON字串自動套用到ArucoData類別中

                    //確保傳進來的資料不會被其他程式更改
                    lock(dataLock)
                    {
                        latestData = parsedData;
                        isDataNew = true;
                    }
                }
            }
        }
        catch (SocketException e)
        {
            Debug.LogWarning("UDP SocketException : " + e.Message);
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
                dataToUse = latestData;  //latestData一直接收新資料，避免在讀取時發生錯誤
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

    //關閉主迴圈並釋放資源
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




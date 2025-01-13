package src;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;


public class CidianServer {
    private Map<String,String> engToChinese = new HashMap<>();

    public CidianServer()//初始化词典库
    {
        engToChinese.put("hello","你好");
        engToChinese.put("你好","hello");
    }

    public String transWord(String TobeTranslated)
    {
        return engToChinese.getOrDefault(TobeTranslated,"找不到翻译");
    }

    public void startServer() {
        try {
            // 启动服务
            ServerSocket serverSocket = new ServerSocket(1234);
            System.out.println("服务器启动成功");
            while (true) {
                // 监听客户端的连接
                Socket socket = serverSocket.accept();
                new SocketThread(socket).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
            System.out.println("服务器启动失败");
        }
    }

    class SocketThread extends Thread {
        boolean mark = true;
        DataInputStream dataInputStream;
        Socket socket;

        public SocketThread(Socket socket) throws IOException {
            this.socket = socket;
            dataInputStream = new DataInputStream(socket.getInputStream());
        }

        public void run() {
            // 一直死循环，监听客户端发送的消息
            while (mark) {
                try {
                    String message = dataInputStream.readUTF();  
                    message = transWord(message);     
                    DataOutputStream clientDataOutputStream = new DataOutputStream(socket.getOutputStream());
                    clientDataOutputStream.writeUTF(message);
                    
            }   catch (IOException e) {
                    e.printStackTrace();
                    mark = false;
                }
            }
        }

    }

}

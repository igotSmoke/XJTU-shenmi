package src;  
  
import java.io.*;  
import java.net.*;  
  
public class jcServer {  
    public static void main(String[] args) {  
        int port = 1130; // 服务器监听的端口号  
  
        try (ServerSocket serverSocket = new ServerSocket(port)) 
        {  
            System.out.println("Server is listening on port " + port);  
  
            while (true) 
            {  
                Socket clientSocket = serverSocket.accept(); 
                System.out.println("New client connected");  
  
                try (  
                    BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));  
                    PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);  
                ) 
                {  
                    String inputLine = in.readLine(); 
                    if (inputLine != null) {  
                        int x = Integer.parseInt(inputLine);  
                        int result = cal(x); 
                        out.println(result);  
                    }  
                } catch (IOException | NumberFormatException e) 
                { 
                    e.printStackTrace();  
                }  
            }  
        } catch (IOException e) 
        {  
            e.printStackTrace();  
        }  
    }  
  
  
    public static int cal(int x) 
    {  
        return x * x - x + 1;  
    }  
}

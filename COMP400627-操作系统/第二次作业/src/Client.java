package src;  
  
import java.io.*;  
import java.net.*;  
  
public class Client {  
    public static void main(String[] args) {  
        String serverAddress = "localhost";  
        int port = 1130;  
        int x = 6; // 示例输入  
  
        long startTime, endTime, elapsedTime;  
        startTime = System.nanoTime();   
        try (  
            Socket socket = new Socket(serverAddress, port);  
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));  
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);  
        ) {  
            
            out.println(x);  
  
            String result = in.readLine();  
            endTime = System.nanoTime(); 
  
            elapsedTime = endTime - startTime;   
  
            System.out.println("Result from server: " + result);  
            System.out.println("Time taken: " + elapsedTime + " nanoseconds");  
        } catch (IOException e) {  
            e.printStackTrace();  
        }  
    }  
}
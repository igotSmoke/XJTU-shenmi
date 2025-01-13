package src;  
  
import java.io.*;  
import java.net.*;  
  
public class Server implements Runnable {  
    private ServerSocket serverSocket;  
  
    public Server(int port) throws IOException {  
        serverSocket = new ServerSocket(port);  
    }  
  
    @Override  
    public void run() {  
        try {  
            while (true) {  
                Socket socket = serverSocket.accept();  
                new Thread(() -> {  
                    try (  
                        BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));  
                        PrintWriter out = new PrintWriter(socket.getOutputStream(), true);  
                    ) {  
                        String input = in.readLine();  
                        if (input != null) {  
                            int x = Integer.parseInt(input);  
                            int result = calculate(x);  
                            out.println(result);  
                        }  
                    } catch (IOException e) {  
                        e.printStackTrace();  
                    }  
                }).start(); 
            }  
        } catch (IOException e) {  
            e.printStackTrace();  
        } finally {  
            try {  
                serverSocket.close();  
            } catch (IOException e) {  
                e.printStackTrace();  
            }  
        }  
    }  
  
    private int calculate(int x) {  
        return x * x - x + 1;  
    }  
  
    public static void main(String[] args) {  
        try {  
            int port = 1130; // 示例端口  
            Server server = new Server(port);  
            new Thread(server).start();  
            System.out.println("Server started on port " + port);  
        } catch (IOException e) {  
            e.printStackTrace();  
        }  
    }  
}
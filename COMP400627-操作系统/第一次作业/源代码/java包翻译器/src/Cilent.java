package src;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.util.Scanner;




public class Cilent 
{
    public Cilent(Socket socket) throws IOException {
        new ClientShootThread(socket).start();
        new ClientThread(socket).start(); 
    }

    class ClientShootThread extends Thread {
        boolean mark = true;
        DataOutputStream dataOutputStream;

        public ClientShootThread(Socket socket) throws IOException {
            dataOutputStream = new DataOutputStream(socket.getOutputStream());
        }

        @Override
        public void run() {
            while (mark) {
                try {
                        Scanner scanner = new Scanner(System.in); // 创建Scanner对象，用于接收键盘输入    
                        String inputString = scanner.nextLine();  
                        dataOutputStream.writeUTF(inputString);

                } catch (IOException e) {
                    e.printStackTrace();
                    mark = false;
                }
            }
        }
    }



    class ClientThread extends Thread {
        boolean mark = true;
        DataInputStream dataInputStream;
        DataOutputStream dataOutputStream;

        public ClientThread(Socket socket) throws IOException {
            dataInputStream = new DataInputStream(socket.getInputStream());
            dataOutputStream = new DataOutputStream(socket.getOutputStream());
        }

        @Override
        public void run() {
            while (mark) {
                try {
                        String msg = dataInputStream.readUTF();
                        // 显示聊天内容，追加 保留之前的内容
                        System.out.println(msg);
                } catch (IOException e) {
                    e.printStackTrace();
                    mark = false;
                }
            }
        }
    }
}

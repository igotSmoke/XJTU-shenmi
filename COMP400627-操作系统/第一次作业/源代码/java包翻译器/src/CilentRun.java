package src;

import java.io.IOException;
import java.net.Socket;

public class CilentRun {
    public static void main(String[] args) {
        try {
            Socket socket = new Socket("127.0.0.1", 1234);
            new Cilent(socket);
        } catch (IOException ioException) {
            ioException.printStackTrace();
        }
    }
}

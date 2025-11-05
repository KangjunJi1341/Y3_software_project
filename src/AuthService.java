import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class AuthService {

    // TODO: 换成你自己的 apiKey
    private static final String API_KEY = "AIzaSyCFgslM9FY0UmUWq9Jzqhq46XnFvmIpzP0";

    private FirebaseUser currentUser;   // ← 新增

    // 登录
    public FirebaseUser signIn(String email, String password) throws IOException {
        String endpoint = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + API_KEY;
        String body = "{"
                + "\"email\":\"" + email + "\","
                + "\"password\":\"" + password + "\","
                + "\"returnSecureToken\":true"
                + "}";
        String resp = postJson(endpoint, body);
        // 先从登录里拿到 idToken
        FirebaseUser user = FirebaseUser.fromLoginResponse(resp);

        // 关键：登录完马上再查一次最新资料
        if (user.idToken != null) {
            FirebaseUser refreshed = refreshUser(user.idToken);
            // refreshUser 里已经把 currentUser 赋值了
            // 但是我们这里最好还是返回最新的
            // 保留旧的 idToken，因为 lookup 不会给新的
            currentUser = new FirebaseUser(
                    refreshed.email,
                    user.idToken,
                    refreshed.emailVerified
            );
        } else {
            currentUser = user;
        }

        return currentUser;
    }

    // 注册
    public FirebaseUser signUp(String email, String password) throws IOException {
        String endpoint = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + API_KEY;
        String body = "{"
                + "\"email\":\"" + email + "\","
                + "\"password\":\"" + password + "\","
                + "\"returnSecureToken\":true"
                + "}";
        String resp = postJson(endpoint, body);
        FirebaseUser user = FirebaseUser.fromLoginResponse(resp);
        currentUser = user;             // ← 记住
        return user;
    }

    public FirebaseUser getCurrentUser() {
        return currentUser;
    }

    // 发送重置密码邮件
    public void sendPasswordReset(String email) throws IOException {
        String endpoint = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=" + API_KEY;
        String body = "{"
                + "\"requestType\":\"PASSWORD_RESET\","
                + "\"email\":\"" + email + "\""
                + "}";
        postJson(endpoint, body);
    }

    // 发送验证邮箱
    public void sendEmailVerification(String idToken) throws IOException {
        String endpoint = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=" + API_KEY;
        String body = "{"
                + "\"requestType\":\"VERIFY_EMAIL\","
                + "\"idToken\":\"" + idToken + "\""
                + "}";
        postJson(endpoint, body);
    }

    private String postJson(String endpoint, String json) throws IOException {
        URL url = new URL(endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            os.write(json.getBytes());
        }

        int code = conn.getResponseCode();
        InputStream is = (code >= 200 && code < 300) ? conn.getInputStream() : conn.getErrorStream();

        try (BufferedReader br = new BufferedReader(new InputStreamReader(is))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ( (line = br.readLine()) != null ) {
                sb.append(line);
            }
            String res = sb.toString();
            if (code >= 200 && code < 300) {
                return res;
            } else {
                throw new IOException(res);
            }
        }
    }

    public FirebaseUser refreshUser(String idToken) throws IOException {
        String endpoint = "https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=" + API_KEY;
        String body = "{"
                + "\"idToken\":\"" + idToken + "\""
                + "}";

        String resp = postJson(endpoint, body);

        // 返回的结构大概是
        // { "users": [ { "email": "...", "emailVerified": true, ... } ] }
        FirebaseUser user = FirebaseUser.fromLookupResponse(resp);
        currentUser = user;
        return user;
    }
}

public class FirebaseUser {
    public final String email;
    public final String idToken;
    public final boolean emailVerified;

    public FirebaseUser(String email, String idToken, boolean emailVerified) {
        this.email = email;
        this.idToken = idToken;
        this.emailVerified = emailVerified;
    }

    public static FirebaseUser fromLoginResponse(String json) {
        // 这两个一定要取到
        String email = pickStringValue(json, "email");
        String idToken = pickStringValue(json, "idToken");
        // 这个字段在你返回里就是  "emailVerified": false  这种形式
        boolean emailVerified = json.contains("\"emailVerified\": true")
                || json.contains("\"emailVerified\":true");

        return new FirebaseUser(email, idToken, emailVerified);
    }

    // accounts:lookup 返回的是 { "users": [ { ... } ] }
    public static FirebaseUser fromLookupResponse(String json) {
        // 先定位到 users[0]
        int usersIdx = json.indexOf("\"users\"");
        if (usersIdx == -1) {
            return new FirebaseUser(null, null, false);
        }
        int firstBrace = json.indexOf("{", usersIdx);
        int endBrace = json.indexOf("}", firstBrace);
        String userObj = json.substring(firstBrace, endBrace + 1);

        String email = pickStringValue(userObj, "email");
        // lookup 里没有新的 idToken，就把 idToken 置空即可（外面会继续用旧的）
        boolean emailVerified = userObj.contains("\"emailVerified\": true")
                || userObj.contains("\"emailVerified\":true");
        return new FirebaseUser(email, null, emailVerified);
    }

    private static String pickStringValue(String json, String key) {
        // 找到 "key"
        String pattern = "\"" + key + "\"";
        int keyPos = json.indexOf(pattern);
        if (keyPos == -1) return null;

        // 找冒号
        int colonPos = json.indexOf(":", keyPos);
        if (colonPos == -1) return null;

        // 找第一个引号（跳过空格）
        int firstQuote = json.indexOf("\"", colonPos);
        if (firstQuote == -1) return null;

        int secondQuote = json.indexOf("\"", firstQuote + 1);
        if (secondQuote == -1) return null;

        return json.substring(firstQuote + 1, secondQuote);
    }
}

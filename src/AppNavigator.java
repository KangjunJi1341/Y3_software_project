import javafx.scene.Scene;
import javafx.stage.Stage;

public class AppNavigator {

    private final Stage stage;
    private final AuthService authService = new AuthService();  // 所有界面公用一份

    public AppNavigator(Stage stage) {
        this.stage = stage;
    }

    public void showLogin() {
        LoginView v = new LoginView(this);
        stage.setScene(new Scene(v, 1200, 760));
    }

    public void showRegister() {
        RegisterView v = new RegisterView(this);
        stage.setScene(new Scene(v, 1200, 760));
    }

    public void showForgotPassword() {
        ForgotPasswordView v = new ForgotPasswordView(this);
        stage.setScene(new Scene(v, 1200, 760));
    }

    public void showDashboard(String email, boolean verified, String idToken) {
        DashboardView v = new DashboardView(this, email, verified, idToken);
        stage.setScene(new Scene(v, 1200, 760));
    }

    public AuthService getAuthService() {
        return authService;
    }
}

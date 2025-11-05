import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;

public class RegisterView extends VBox {

    public RegisterView(AppNavigator nav) {
        setSpacing(10);
        setPadding(new Insets(20));

        Label title = new Label("Create account");
        TextField emailField = new TextField();
        emailField.setPromptText("Email");
        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("Password (min 6)");
        Label errorLabel = new Label();
        errorLabel.setStyle("-fx-text-fill: crimson;");

        Button registerBtn = new Button("Register");
        Button backBtn = new Button("Back to login");

        registerBtn.setOnAction(e -> {
            errorLabel.setText("");
            String email = emailField.getText();
            String pass = passwordField.getText();
            try {
                FirebaseUser u = nav.getAuthService().signUp(email, pass);
                nav.showDashboard(u.email, u.emailVerified, u.idToken);
            } catch (Exception ex) {
                errorLabel.setText(ex.getMessage());
            }
        });

        backBtn.setOnAction(e -> nav.showLogin());

        getChildren().addAll(title, emailField, passwordField, registerBtn, errorLabel, backBtn);
    }
}

import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;

public class ForgotPasswordView extends VBox {

    public ForgotPasswordView(AppNavigator nav) {
        setSpacing(10);
        setPadding(new Insets(20));

        Label title = new Label("Forgot password");
        TextField emailField = new TextField();
        emailField.setPromptText("Your email");
        Label statusLabel = new Label();
        Label errorLabel = new Label();
        statusLabel.setStyle("-fx-text-fill: green;");
        errorLabel.setStyle("-fx-text-fill: crimson;");

        Button sendBtn = new Button("Send reset email");
        Button backBtn = new Button("Back to login");

        sendBtn.setOnAction(e -> {
            statusLabel.setText("");
            errorLabel.setText("");
            try {
                nav.getAuthService().sendPasswordReset(emailField.getText());
                statusLabel.setText("Password reset email sent.");
            } catch (Exception ex) {
                errorLabel.setText(ex.getMessage());
            }
        });

        backBtn.setOnAction(e -> nav.showLogin());

        getChildren().addAll(title, emailField, sendBtn, statusLabel, errorLabel, backBtn);
    }
}

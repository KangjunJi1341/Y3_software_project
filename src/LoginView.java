import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.Region;

public class LoginView extends VBox {

    public LoginView(AppNavigator nav) {
        // 整个面板占满窗口，高度够的话内容能居中
        setAlignment(Pos.CENTER);              // 垂直水平都居中
        setSpacing(12);
        setPadding(new Insets(0));
        setPrefSize(1200, 760);                // 跟你窗口差不多大
        setStyle("-fx-background-color: linear-gradient(to bottom, #e2e8f0, #ffffff);");

        // 中间这块是真正的表单
        VBox form = new VBox(10);
        form.setAlignment(Pos.CENTER);
        form.setPadding(new Insets(24));
        form.setMaxWidth(380);
        form.setStyle("-fx-background-color: white; -fx-background-radius: 16; -fx-effect: dropshadow(gaussian, rgba(15,23,42,0.12), 18, 0, 0, 4);");

        Label title = new Label("Welcome!");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        Label subtitle = new Label("Sign in to your account");
        subtitle.setStyle("-fx-text-fill: #6b7280; -fx-font-size: 12px;");



        TextField emailField = new TextField();
        emailField.setPromptText("Email");
        emailField.setMaxWidth(Double.MAX_VALUE);

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("Password");
        passwordField.setMaxWidth(Double.MAX_VALUE);

        emailField.setStyle(
                "-fx-background-radius: 10;" +
                        "-fx-border-radius: 10;" +
                        "-fx-border-color: #e5e7eb;" +
                        "-fx-padding: 8 10;"
        );
        passwordField.setStyle(
                "-fx-background-radius: 10;" +
                        "-fx-border-radius: 10;" +
                        "-fx-border-color: #e5e7eb;" +
                        "-fx-padding: 8 10;"
        );


        Label errorLabel = new Label();
        errorLabel.setStyle("-fx-text-fill: crimson;");

        Button loginBtn = new Button("Login");
        loginBtn.setMaxWidth(Double.MAX_VALUE);

        loginBtn.setStyle(
                "-fx-background-color: #2563eb;" +
                        "-fx-text-fill: white;" +
                        "-fx-background-radius: 10;" +
                        "-fx-font-weight: 600;"
        );


        Button gotoRegister = new Button("Create account");
        Button gotoForgot = new Button("Forgot password?");

        gotoRegister.setStyle("-fx-background-color: transparent; -fx-text-fill: #2563eb;");
        gotoForgot.setStyle("-fx-background-color: transparent; -fx-text-fill: #2563eb;");


        loginBtn.setOnAction(e -> {
            errorLabel.setText("");
            String email = emailField.getText();
            String pass = passwordField.getText();
            try {
                FirebaseUser u = nav.getAuthService().signIn(email, pass);
                nav.showDashboard(u.email, u.emailVerified, u.idToken);
            } catch (Exception ex) {
                errorLabel.setText(ex.getMessage());
            }
        });

        gotoRegister.setOnAction(e -> nav.showRegister());
        gotoForgot.setOnAction(e -> nav.showForgotPassword());

        form.getChildren().addAll(
                title,
                subtitle,
                emailField,
                passwordField,
                loginBtn,
                errorLabel,
                gotoRegister,
                gotoForgot
        );

// ① 新建一个能叠放东西的容器
        StackPane center = new StackPane();
        center.setPrefSize(1200, 760);

// ② 做两个装饰气泡
        Region bubble1 = new Region();
        bubble1.setPrefSize(180, 180);
        bubble1.setStyle(
                "-fx-background-color: rgba(37,99,235,0.14);" +
                        "-fx-background-radius: 999;"
        );
        StackPane.setAlignment(bubble1, Pos.TOP_RIGHT);
        StackPane.setMargin(bubble1, new Insets(60, 160, 0, 0));

        Region bubble2 = new Region();
        bubble2.setPrefSize(240, 240);
        bubble2.setStyle(
                "-fx-background-color: rgba(255,255,255,0.55);" +
                        "-fx-background-radius: 999;"
        );
        StackPane.setAlignment(bubble2, Pos.BOTTOM_LEFT);
        StackPane.setMargin(bubble2, new Insets(0, 0, 80, 120));

// ③ 把表单放到最上面
        StackPane.setAlignment(form, Pos.CENTER);

// ④ 先加气泡，再加表单
        center.getChildren().addAll(bubble1, bubble2, form);

// ⑤ 最后把这个 center 加到 LoginView 里
        getChildren().add(center);

    }
}

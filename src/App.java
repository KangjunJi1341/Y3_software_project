import javafx.application.Application;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class App extends Application {

    @Override
    public void start(Stage stage) {
        // 稍后我们会写一个 LoginView，这里先占位
        LoginView loginView = new LoginView(new AppNavigator(stage));
        Scene scene = new Scene(loginView, 1200, 760);
        stage.setTitle("Voice-Enabled AI Assistant");
        stage.setScene(scene);
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}

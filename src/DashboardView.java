import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.*;

public class DashboardView extends BorderPane {

    public DashboardView(AppNavigator nav, String email, boolean verified, String idToken) {

        // 拿最新用户
        FirebaseUser cu = nav.getAuthService().getCurrentUser();
        if (cu != null) {
            if (email == null) email = cu.email;
            if (idToken == null) idToken = cu.idToken;
            if (!verified) verified = cu.emailVerified;
        }

        // 背景
        setStyle("-fx-background-color: #e5e7eb;");

        /* ========== 左侧栏 ========== */
        VBox leftBar = new VBox();
        leftBar.setPrefWidth(210);
        leftBar.setStyle(
                "-fx-background-color: #0f172a;" +   // 深色侧边栏
                        "-fx-border-color: #0f172a;" +
                        "-fx-border-width: 0 1 0 0;"
        );
        leftBar.setMinHeight(0);

        // 1) 顶部：标题 + 新建对话
        VBox leftTop = new VBox(10);
        leftTop.setPadding(new Insets(2, 14, 10, 14));

        Label appTitle = new Label("");

        Button newChatBtn = new Button("+ New chat");
        newChatBtn.setMaxWidth(Double.MAX_VALUE);
        newChatBtn.setStyle("-fx-background-color: #e2e8f0; -fx-background-radius: 8;");

        leftTop.getChildren().addAll(appTitle, newChatBtn);

        // 2) 中间：聊天记录列表（假的）
        VBox chatList = new VBox(6);
        chatList.setPadding(new Insets(0, 14, 0, 14));

        chatList.getChildren().add(makeChatItem("Welcome chat"));
        chatList.getChildren().add(makeChatItem("Project Q&A"));
        chatList.getChildren().add(makeChatItem("Report draft"));
        chatList.getChildren().add(makeChatItem("Backend API ideas"));

        ScrollPane chatListScroll = new ScrollPane(chatList);
        chatListScroll.setFitToWidth(true);
        chatListScroll.setStyle("-fx-background-color: transparent;");
        chatListScroll.setVbarPolicy(ScrollPane.ScrollBarPolicy.AS_NEEDED);
        VBox.setVgrow(chatListScroll, Priority.ALWAYS);

        // 3) 底部：账号信息 + 验证 + 退出
        VBox leftBottom = new VBox(6);
        leftBottom.setPadding(new Insets(10, 14, 14, 14));
        leftBottom.setStyle("-fx-background-color: #ffffff; -fx-border-color: #d1d5db; -fx-border-width: 1 0 0 0;");

        Label accountLabel = new Label(email != null ? email : "-");
        accountLabel.setWrapText(true);
        accountLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #000000;");

        Label verifiedLabel = new Label(verified ? "Verified" : "Not verified");
        verifiedLabel.setStyle(verified
                ? "-fx-text-fill: #22c55e; -fx-font-size: 11px;"
                : "-fx-text-fill: #f97316; -fx-font-size: 11px;");

        Button verifyBtn = new Button("Verify email");
        verifyBtn.setDisable(verified);
        verifyBtn.setMaxWidth(Double.MAX_VALUE);
        final String tokenForBtn = idToken;
        verifyBtn.setOnAction(e -> {
            try {
                nav.getAuthService().sendEmailVerification(tokenForBtn);
            } catch (Exception ex) {
                new Alert(Alert.AlertType.ERROR, ex.getMessage()).showAndWait();
            }
        });

        Button logoutBtn = new Button("Logout");
        makeSecondary(logoutBtn);
        logoutBtn.setMaxWidth(Double.MAX_VALUE);
        logoutBtn.setOnAction(e -> nav.showLogin());

        leftBottom.getChildren().addAll(
                new Separator(),
                new Label("Account"),
                accountLabel,
                verifiedLabel,
                verifyBtn,
                logoutBtn
        );

        leftBar.getChildren().addAll(leftTop, chatListScroll, leftBottom);

        /* ========== 顶部栏 ========== */
        HBox topBar = new HBox();
        topBar.setPadding(new Insets(10, 18, 10, 18));
        topBar.setStyle("-fx-background-color: #ffffff; -fx-border-color: #d1d5db; -fx-border-width: 0 0 1 0;");
        topBar.setAlignment(Pos.CENTER_LEFT);

        Label title = new Label("Chat with AI");
        title.setStyle("-fx-font-size: 16px; -fx-font-weight: 600;");
        Region topSpacer = new Region();
        HBox.setHgrow(topSpacer, Priority.ALWAYS);
        Label avatar = new Label("•");
        avatar.setStyle("-fx-background-color: #2563eb; -fx-text-fill: white; -fx-padding: 4 8; -fx-background-radius: 999;");
        topBar.getChildren().addAll(title, topSpacer, avatar);

        /* ========== 中间聊天区（居中列） ========== */
        StackPane centerPane = new StackPane();
        centerPane.setPadding(new Insets(20));

        // 装饰气泡 1（右上角）
        Region bubble1 = new Region();
        bubble1.setPrefSize(180, 180);
        bubble1.setStyle(
                "-fx-background-color: rgba(37,99,235,0.12);" +  // 蓝色透明
                        "-fx-background-radius: 999;"                   // 圆形
        );
        StackPane.setAlignment(bubble1, Pos.TOP_RIGHT);
        StackPane.setMargin(bubble1, new Insets(0, 80, 0, 0)); // 往里缩一点

// 装饰气泡 2（左下角）
        Region bubble2 = new Region();
        bubble2.setPrefSize(220, 220);
        bubble2.setStyle(
                "-fx-background-color: rgba(255,255,255,0.35);" +
                        "-fx-background-radius: 999;"
        );
        StackPane.setAlignment(bubble2, Pos.BOTTOM_LEFT);
        StackPane.setMargin(bubble2, new Insets(0, 0, 40, 40));


        VBox chatWrapper = new VBox(10);
        chatWrapper.setMaxWidth(760);
        chatWrapper.setStyle(
                "-fx-background-color: white;" +
                        "-fx-background-radius: 16;" +
                        "-fx-effect: dropshadow(gaussian, rgba(15,23,42,0.04), 14, 0, 0, 4);"
        );
        chatWrapper.setPadding(new Insets(12, 12, 12, 12));

        VBox chatColumn = new VBox(10);
        chatColumn.setFillWidth(true);
        chatColumn.setMaxWidth(760);
        chatColumn.setPrefWidth(760);

        // 消息列表
        VBox messagesBox = new VBox(12);
        messagesBox.setFillWidth(true);
        messagesBox.getChildren().add(botMsg("Hi " + (email != null ? email : ""), "I'm your AI assistant in JavaFX."));
        messagesBox.getChildren().add(userMsg("Can you summarise today's tasks?"));
        messagesBox.getChildren().add(botMsg("Sure.", "1) Finish UI\n2) Hook backend later\n3) Write report."));

        ScrollPane scrollPane = new ScrollPane(messagesBox);
        scrollPane.setFitToWidth(true);
        scrollPane.setStyle("-fx-background-color: transparent;");
        scrollPane.setVbarPolicy(ScrollPane.ScrollBarPolicy.AS_NEEDED);
        VBox.setVgrow(scrollPane, Priority.ALWAYS);

        // 输入栏
        HBox inputBar = new HBox(10);
        inputBar.setPadding(new Insets(10, 0, 0, 0));
        inputBar.setAlignment(Pos.CENTER_LEFT);

        TextField inputField = new TextField();
        inputField.setPromptText("Message ChatGPT…");
        inputField.setStyle("-fx-background-color: #ffffff; -fx-background-radius: 999; -fx-padding: 8 12;");
        HBox.setHgrow(inputField, Priority.ALWAYS);
        Button voiceBtn = new Button("🎤");
        voiceBtn.setStyle(
                "-fx-background-color: #ffffff;" +
                        "-fx-background-radius: 999;" +
                        "-fx-border-color: #d1d5db;" +
                        "-fx-border-radius: 999;" +
                        "-fx-padding: 4 10;"
        );
        // 这里先放个占位逻辑，之后你队友换成真正录音
        voiceBtn.setOnAction(e -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION, "TODO: start recording...");
            alert.setHeaderText(null);
            alert.showAndWait();
        });



        Button sendBtn = new Button("Send");
        sendBtn.setStyle("-fx-background-color: #2563eb; -fx-text-fill: white; -fx-background-radius: 999; -fx-padding: 6 16;");

        inputBar.getChildren().addAll(inputField, voiceBtn,sendBtn);

        chatColumn.getChildren().addAll(scrollPane, inputBar);
        centerPane.getChildren().addAll(bubble1, bubble2);
        centerPane.getChildren().add(chatColumn);
        StackPane.setAlignment(chatColumn, Pos.TOP_CENTER);

        // 塞到主布局
        setLeft(leftBar);
        setTop(topBar);
        setCenter(centerPane);
    }

    // 左侧聊天记录条目
    private HBox makeChatItem(String text) {
        Label l = new Label(text);
        l.setWrapText(true);
        l.setStyle("-fx-text-fill: #000000; -fx-font-size: 12px;");
        HBox box = new HBox(l);
        box.setAlignment(Pos.CENTER_LEFT);
        box.setPadding(new Insets(6, 8, 6, 8));
        box.setStyle("-fx-background-radius: 6;");
        box.setOnMouseEntered(e -> box.setStyle("-fx-background-color: rgba(255,255,255,0.08); -fx-background-radius: 6;"));
        box.setOnMouseExited(e -> box.setStyle("-fx-background-radius: 6;"));
        return box;
    }

    // 机器人卡片
    private VBox botMsg(String title, String body) {
        VBox card = new VBox(6);
        card.setStyle(
                "-fx-background-color: #ffffff;" +
                        "-fx-background-radius: 14;" +
                        "-fx-padding: 10 14 10 14;"
        );
        Label t = new Label(title);
        t.setStyle("-fx-font-weight: 600; -fx-text-fill: #0f172a;");
        Label b = new Label(body);
        b.setWrapText(true);
        b.setStyle("-fx-text-fill: #1f2937; -fx-font-size: 12.5px;");
        card.getChildren().addAll(t, b);

        VBox outer = new VBox(card);
        outer.setAlignment(Pos.CENTER_LEFT);
        return outer;
    }

    private HBox userMsg(String text) {
        Label l = new Label(text);
        l.setWrapText(true);
        l.setStyle(
                "-fx-background-color: #2563eb;" +
                        "-fx-text-fill: white;" +
                        "-fx-padding: 8 14;" +
                        "-fx-background-radius: 14;" +
                        "-fx-font-size: 12.5px;"
        );
        HBox box = new HBox(l);
        box.setAlignment(Pos.CENTER_RIGHT);
        return box;
    }

    private void makePrimary(Button b) {
        b.setStyle("-fx-background-color: #2563eb; -fx-text-fill: white; -fx-background-radius: 999;");
    }

    private void makeSecondary(Button b) {
        b.setStyle("-fx-background-color: rgba(255,255,255,0.12); -fx-text-fill: #e2e8f0; -fx-background-radius: 6;");
    }

}

<?php
session_start();
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $account = $_POST['account'];
    $password = $_POST['password'];

    $conn = new mysqli('localhost', 'root', '', 'db_project');
    if ($conn->connect_error) die("連線失敗：" . $conn->connect_error);

    $stmt = $conn->prepare("SELECT * FROM admin WHERE account=? AND password=?");
    $stmt->bind_param("ss", $account, $password);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows === 1) {
        $_SESSION['admin'] = $account;
        header("Location: dashboard.php");
        exit();
    } else {
        $error = "帳號或密碼錯誤";
    }
}
?>
<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"><title>管理員登入</title></head>
<body>
<h2>管理員登入</h2>
<form method="post">
    帳號：<input type="text" name="account" required><br>
    密碼：<input type="password" name="password" required><br>
    <button type="submit">登入</button>
</form>
<?php if (!empty($error)) echo "<p style='color:red;'>$error</p>"; ?>
</body>
</html>

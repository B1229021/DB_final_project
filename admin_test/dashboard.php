<?php
session_start();
if (!isset($_SESSION['admin'])) {
    header("Location: login.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"><title>後台管理</title></head>
<body>
<h2>歡迎，<?php echo $_SESSION['admin']; ?>！</h2>
<ul>
    <li><a href="categories.php">管理分類（categories）</a></li>
    <li><a href="event.php">管理活動（event）</a></li>
    <li><a href="logout.php">登出</a></li>
</ul>
</body>
</html>

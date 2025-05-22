<?php
session_start();
if (!isset($_SESSION['admin'])) exit("未授權存取");

$conn = new mysqli('localhost', 'root', '', 'db_project');
if ($conn->connect_error) die("連線錯誤：" . $conn->connect_error);

// 新增分類
if (isset($_POST['add'])) {
    $stmt = $conn->prepare("INSERT INTO categories (content) VALUES (?)");
    $stmt->bind_param("s", $_POST['content']);
    $stmt->execute();
}

// 刪除分類
if (isset($_GET['delete'])) {
    $id = intval($_GET['delete']);
    $conn->query("DELETE FROM categories WHERE categories_id=$id");
}

// 更新分類
if (isset($_POST['edit'])) {
    $stmt = $conn->prepare("UPDATE categories SET content=? WHERE categories_id=?");
    $stmt->bind_param("si", $_POST['content'], $_POST['id']);
    $stmt->execute();
}

$result = $conn->query("SELECT * FROM categories");
?>
<h2>分類管理</h2>
<form method="post">
    新增分類：<input type="text" name="content" required>
    <button type="submit" name="add">新增</button>
</form>

<table border="1">
    <tr><th>ID</th><th>內容</th><th>動作</th></tr>
    <?php while ($row = $result->fetch_assoc()): ?>
    <tr>
        <form method="post">
            <td><?= $row['categories_id'] ?></td>
            <td>
                <input type="text" name="content" value="<?= $row['content'] ?>">
                <input type="hidden" name="id" value="<?= $row['categories_id'] ?>">
            </td>
            <td>
                <button type="submit" name="edit">修改</button>
                <a href="?delete=<?= $row['categories_id'] ?>" onclick="return confirm('確定刪除？')">刪除</a>
            </td>
        </form>
    </tr>
    <?php endwhile; ?>
</table>
<a href="dashboard.php">← 返回後台首頁</a>

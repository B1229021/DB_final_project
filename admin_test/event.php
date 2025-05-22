<?php
session_start();
if (!isset($_SESSION['admin'])) exit("未授權存取");

$conn = new mysqli('localhost', 'root', '', 'db_project');
if ($conn->connect_error) die("連線錯誤：" . $conn->connect_error);

// 新增活動
if (isset($_POST['add'])) {
    $stmt = $conn->prepare("INSERT INTO event (categories_id, content) VALUES (?, ?)");
    $stmt->bind_param("is", $_POST['categories_id'], $_POST['content']);
    $stmt->execute();
}

// 刪除活動
if (isset($_GET['delete'])) {
    $id = intval($_GET['delete']);
    $conn->query("DELETE FROM event WHERE event_id=$id");
}

// 修改活動
if (isset($_POST['edit'])) {
    $stmt = $conn->prepare("UPDATE event SET categories_id=?, content=? WHERE event_id=?");
    $stmt->bind_param("isi", $_POST['categories_id'], $_POST['content'], $_POST['event_id']);
    $stmt->execute();
}

$events = $conn->query("SELECT * FROM event");
$categories = $conn->query("SELECT * FROM categories");
$cat_options = [];
while ($c = $categories->fetch_assoc()) {
    $cat_options[$c['categories_id']] = $c['content'];
}
?>
<h2>活動管理</h2>
<form method="post">
    分類：
    <select name="categories_id" required>
        <?php foreach ($cat_options as $id => $label): ?>
            <option value="<?= $id ?>"><?= $label ?></option>
        <?php endforeach; ?>
    </select>
    活動名稱：<input type="text" name="content" required>
    <button type="submit" name="add">新增</button>
</form>

<table border="1">
    <tr><th>ID</th><th>分類</th><th>內容</th><th>動作</th></tr>
    <?php while ($row = $events->fetch_assoc()): ?>
    <tr>
        <form method="post">
            <td><?= $row['event_id'] ?></td>
            <td>
                <select name="categories_id">
                    <?php foreach ($cat_options as $id => $label): ?>
                        <option value="<?= $id ?>" <?= $id == $row['categories_id'] ? 'selected' : '' ?>><?= $label ?></option>
                    <?php endforeach; ?>
                </select>
            </td>
            <td>
                <input type="text" name="content" value="<?= $row['content'] ?>">
                <input type="hidden" name="event_id" value="<?= $row['event_id'] ?>">
            </td>
            <td>
                <button type="submit" name="edit">修改</button>
                <a href="?delete=<?= $row['event_id'] ?>" onclick="return confirm('確定刪除？')">刪除</a>
            </td>
        </form>
    </tr>
    <?php endwhile; ?>
</table>
<a href="dashboard.php">← 返回後台首頁</a>

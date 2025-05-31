<?php
// session_start();
// $uid = $_GET['uid'] ?? null;

// 資料庫連線
$conn = new mysqli("localhost", "root", "12345678", "db_project");
if ($conn->connect_error) {
    die("連線失敗: " . $conn->connect_error);
}

// 管理員判斷
// function isAdmin($uid, $conn) {
//     $stmt = $conn->prepare("SELECT isadmin FROM user WHERE uid = ?");
//     $stmt->bind_param("s", $uid);
//     $stmt->execute();
//     $result = $stmt->get_result();
//     if ($row = $result->fetch_assoc()) {
//         return $row['isadmin'] == 1;
//     }
//     return false;
// }

// if (!$uid || !isAdmin($uid, $conn)) {
//     die("❌ 沒有管理權限，請先登入管理員帳號。");
// }

$username = '';
// if ($uid) {
    $stmt = $conn->prepare("SELECT username FROM user WHERE uid = ?");
    $stmt->bind_param("s", $uid);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $username = $row['username'];
    }
// }


$categories = [];
$result = $conn->query("SELECT * FROM categories");
while ($row = $result->fetch_assoc()) {
    $categories[$row['categories_id']] = $row['content'];
}


// 新增活動類別
if (isset($_POST['new_category_name'])) {
    $name = $conn->real_escape_string($_POST['new_category_name']);
    $stmt = $conn->prepare("INSERT INTO categories (content) VALUES (?)");
    $stmt->bind_param("s", $name);
    $stmt->execute();

    // 重定向，避免重複新增
    header("Location: " . $_SERVER['PHP_SELF']);
    exit();
}


// 新增活動
if (isset($_POST['new_event_name']) && isset($_POST['new_event_category'])) {
    $eid = intval($_POST['new_event_category']);
    $name = $_POST['new_event_name'];

    $stmt = $conn->prepare("INSERT INTO event (categories_id, content) VALUES (?, ?)");
    $stmt->bind_param("is", $eid, $name);
    $stmt->execute();

    // 重定向，避免重複新增
    header("Location: " . $_SERVER['PHP_SELF']);
    exit();
}



// 編輯活動類別
if (isset($_POST['edit_category_id']) && isset($_POST['edit_category_name'])) {
    $id = intval($_POST['edit_category_id']);
    $name = trim($_POST['edit_category_name']);
    if ($name !== '') {
        $stmt = $conn->prepare("UPDATE categories SET content = ? WHERE categories_id = ?");
        $stmt->bind_param("si", $name, $id);
        $stmt->execute();
    }
}

// 刪除活動類別
if (isset($_POST['delete_category_id'])) {
    $id = intval($_POST['delete_category_id']);
    $stmt = $conn->prepare("DELETE FROM categories WHERE categories_id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
}

// 編輯活動
if (isset($_POST['edit_event_id']) && isset($_POST['edit_event_name']) && isset($_POST['edit_event_category'])) {
    $id = intval($_POST['edit_event_id']);
    $name = trim($_POST['edit_event_name']);
    $cat = intval($_POST['edit_event_category']);
    if ($name !== '') {
        $stmt = $conn->prepare("UPDATE event SET content = ?, categories_id = ? WHERE event_id = ?");
        $stmt->bind_param("sii", $name, $cat, $id);
        $stmt->execute();
    }
}

// 刪除活動
if (isset($_POST['delete_event_id'])) {
    $id = intval($_POST['delete_event_id']);
    $stmt = $conn->prepare("DELETE FROM event WHERE event_id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
}

//刪除使用者
if (isset($_POST['delete_user_id'])) {
    $uidToDelete = $conn->real_escape_string($_POST['delete_user_id']);
    $stmt = $conn->prepare("DELETE FROM user WHERE uid = ?");
    $stmt->bind_param("s", $uidToDelete);
    $stmt->execute();
}


?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>管理員後台</title>
    <link rel="stylesheet" href="admin.css">
    <style>

    </style>
</head>
<body>
<div class="wrapper">
    <div class="sidebar">
        <h2>管理後台</h2>
        <a href="#category">📂 類別管理</a>
        <a href="#event">🎉 活動管理</a>
        <a href="#order">📦 訂單管理</a>
        <a href="#eval">📝 評價管理</a>
        <a href="#user">👤 使用者管理</a>
        <hr>
        <a href="../index/index.php">👤 回首頁</a>
        <a href="logout.php">🚪 登出</a>
    </div>

    <div class="main-content">
        <h1>🎛 管理員後台</h1>
        <!-- <p>目前登入帳號：<strong><//?= htmlspecialchars($username ?: $uid) ?></strong></p> -->


        <!-- 顯示所有類別 -->
        <h2 id="category">
            📂 活動類別 
            <button onclick="toggleCategoryEdit()">✏️ 編輯</button>
        </h2>

        <table>
            <tr>
                <th>ID</th>
                <th>內容</th>
                <th class="category-action-header" style="display: none;">操作</th>
            </tr>
            <?php
            $result = $conn->query("SELECT * FROM categories");
            while ($row = $result->fetch_assoc()) {
                echo "<tr>
                    <td>{$row['categories_id']}</td>
                    <td>{$row['content']}</td>
                    <td class='category-action-cell' style='display: none;'>
                        <form method='POST' style='display:inline-block;'>
                            <input type='hidden' name='delete_category_id' value='{$row['categories_id']}'>
                            <button type='submit'>🗑</button>
                        </form>
                        <form method='POST' style='display:inline-block;'>
                            <input type='hidden' name='edit_category_id' value='{$row['categories_id']}'>
                            <input type='text' name='edit_category_name' value='{$row['content']}'>
                            <button type='submit'>✏️</button>
                        </form>
                    </td>
                </tr>";
            }
            ?>
        </table>


        <!-- 新增活動類別表單 -->
        <div id="category-form" style="display: none;">
            <h4>➕ 新增活動類別</h4>
            <form method="POST">
                <input type="text" name="new_category_name" required placeholder="類別名稱">
                <button type="submit">新增</button>
            </form>
        </div>





        <!-- 顯示活動 -->
        <h2 id="event">
            🎉 活動 
            <button id="toggleEventBtn" onclick="toggleEventEdit()">✏️ 編輯</button>
        </h2>

        <table>
            <tr>
                <th>ID</th>
                <th>類別ID</th>
                <th>內容</th>
                <th class="event-action-header" style="display: none;">操作</th>
            </tr>
            <?php
            $res = $conn->query("SELECT * FROM event");
            while ($row = $res->fetch_assoc()) {
                $categoryName = $categories[$row['categories_id']] ?? '未知類別';
                echo "<tr>
                    <td>{$row['event_id']}</td>
                    <td>" . htmlspecialchars($categoryName) . "</td>
                    <td>{$row['content']}</td>
                    <td class='event-action-cell' style='display: none;'>
                        <form method='POST' style='display:inline-block;'>
                            <input type='hidden' name='delete_event_id' value='{$row['event_id']}'>
                            <button type='submit'>🗑</button>
                        </form>
                        <form method='POST' style='display:inline-block;'>
                            <input type='hidden' name='edit_event_id' value='{$row['event_id']}'>
                            <select name='edit_event_category'>";
                                foreach ($categories as $id => $name) {
                                    $selected = $row['categories_id'] == $id ? 'selected' : '';
                                    echo "<option value='$id' $selected>$name</option>";
                                }
                echo "</select>
                            <input type='text' name='edit_event_name' value='{$row['content']}'>
                            <button type='submit'>✏️</button>
                        </form>
                    </td>
                </tr>";
            }
            ?>
        </table>


        <!-- 新增活動表單 -->
        <div id="event-form" style="display: none;">
            <h4>➕ 新增活動</h4>
            <form method="POST">
                <select name="new_event_category" required>
                    <option value="">選擇類別</option>
                    <?php foreach ($categories as $id => $name): ?>
                        <option value="<?= $id ?>"><?= htmlspecialchars($name) ?></option>
                    <?php endforeach; ?>

                </select>
                <input type="text" name="new_event_name" required placeholder="活動名稱">
                <button type="submit">新增</button>
            </form>
        </div>


        <!-- 顯示訂單 -->
        <h2 id="order">📅 訂單</h2>
        <table>
            <tr><th>ID</th><th>發起人</th><th>地點</th><th>活動ID</th><th>狀態</th></tr>
            <?php
            $result = $conn->query("SELECT o.orderid, o.booker, u.username, o.location, o.event_id, o.state 
                        FROM order_detail o 
                        LEFT JOIN user u ON o.booker = u.uid");
            while ($row = $result->fetch_assoc()) {
                $bookerUsername = htmlspecialchars($row['username'] ?? $row['booker']);
                $bookerLink = "<a style='color: darkblue;' href='../profile/profile.php?uid=" . urlencode($row['booker']) . "'>" . $bookerUsername . "</a>";
                echo "<tr>
                        <td>{$row['orderid']}</td>
                        <td>{$bookerLink}</td>
                        <td>{$row['location']}</td>
                        <td>{$row['event_id']}</td>
                        <td>{$row['state']}</td>
                    </tr>";
            }

            ?>
        </table>

        <!-- 顯示評價 -->
        <h2 id="eval">⭐ 評價</h2>
        <table>
            <tr><th>訂單ID</th><th>參與者</th><th>評價給發起人</th><th>發起人回應</th><th>正負評</th></tr>
            <?php
            $result = $conn->query("SELECT i.*, u.username 
                        FROM involvement i 
                        LEFT JOIN user u ON i.uid = u.uid");
            while ($row = $result->fetch_assoc()) {
                $username = htmlspecialchars($row['username'] ?? $row['uid']);
                $userLink = "<a style='color: darkblue;' href='../profile/profile.php?uid=" . urlencode($row['uid']) . "'>$username</a>";
                echo "<tr>
                        <td>{$row['orderid']}</td>
                        <td>{$userLink}</td>
                        <td>{$row['eval_to_booker']}</td>
                        <td>{$row['booker_eval']}</td>
                        <td>{$row['evaluation']}</td>
                    </tr>";
            }

            ?>
        </table>

        <!-- 顯示使用者 -->
        <h2 id="user">
            👤 使用者 
            <button id="toggleUserBtn" onclick="toggleEditActions('user', 'toggleUserBtn')">✏️ 編輯</button>
        </h2>

        <table>
            <tr>
                <th>UID</th><th>帳號</th><th>姓名</th><th>性別</th><th>電話</th><th>身份證</th>
                <th class="user-header" style="display: none;">操作</th>
            </tr>
            <?php
            $res = $conn->query("SELECT * FROM user");
            while ($row = $res->fetch_assoc()) {
                echo "<tr>
                    <td><a style='color: darkblue;' href='../profile/profile.php?uid=" . urlencode($row['uid']) . "'>" . htmlspecialchars($row['uid']) . "</a></td>
                    <td>" . htmlspecialchars($row['username']) . "</td>
                    <td>" . htmlspecialchars($row['name']) . "</td>
                    <td>" . htmlspecialchars($row['gender']) . "</td>
                    <td>" . htmlspecialchars($row['phone']) . "</td>
                    <td>" . htmlspecialchars($row['identify_ID']) . "</td>
                    <td class='user-actions' style='display: none;'>
                        <form method='POST' style='display:inline-block;'>
                            <input type='hidden' name='delete_user_id' value='" . htmlspecialchars($row['uid']) . "'>
                            <button type='submit' onclick=\"return confirm('確定刪除此使用者？')\">🗑 刪除</button>
                        </form>
                    </td>
                </tr>";
            }
            ?>
        </table>

    </div>
</div>
</body>

<script>
function toggleEditActions(sectionClassName, buttonId) {
    const isHidden = document.querySelector(`.${sectionClassName}-actions`)?.style.display === 'none';
    const actionCells = document.querySelectorAll(`.${sectionClassName}-actions`);
    const actionHeader = document.querySelector(`.${sectionClassName}-header`);
    const button = document.getElementById(buttonId);

    actionCells.forEach(cell => {
        cell.style.display = isHidden ? 'table-cell' : 'none';
    });
    if (actionHeader) actionHeader.style.display = isHidden ? 'table-cell' : 'none';
    button.textContent = isHidden ? '✅ 完成' : '✏️ 編輯';
}

function toggleCategoryEdit() {
    // 顯示 / 隱藏 表格操作欄
    document.querySelectorAll('.category-action-header, .category-action-cell').forEach(el => {
        el.style.display = el.style.display === 'none' ? 'table-cell' : 'none';
    });

    // 顯示 / 隱藏 新增類別表單
    const form = document.getElementById('category-form');
    form.style.display = (form.style.display === 'none') ? 'block' : 'none';
}

function toggleEventEdit() {
    document.querySelectorAll('.event-action-header, .event-action-cell').forEach(el => {
        el.style.display = el.style.display === 'none' ? 'table-cell' : 'none';
    });

    const form = document.getElementById('event-form');
    form.style.display = (form.style.display === 'none') ? 'block' : 'none';
}

</script>




</html>

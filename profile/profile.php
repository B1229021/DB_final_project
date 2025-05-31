<?php
require_once 'db_connect.php';

$login_uid = 'f8dh3ld8bnwe3bfx8hre3jt7b01gvd';  //這邊要改為現在登入的帳號
$uid = $_GET['uid'] ?? null;

echo $login_uid;
echo '<br>';
echo $uid;

if (!$uid) {
    header("Location: ../index/index.php");
    exit;
}

// 查詢登入者是否為管理員
$isAdmin = false;
if ($login_uid) {
    $stmt = $conn->prepare("SELECT isadmin FROM user WHERE uid = ?");
    $stmt->bind_param("s", $login_uid);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $isAdmin = $row['isadmin'] == 1;
    }
}

// 身份判斷
$isSelf = $login_uid === $uid;
$canEdit = $isSelf || $isAdmin;  // 可完整顯示 & 編輯

// ✅ 到這裡就代表是自己或管理員，可顯示 profile
?>



<?php
// 取得使用者資料
$user_sql = "SELECT * FROM user WHERE uid = ?";
$stmt = $conn->prepare($user_sql);
$stmt->bind_param("s", $uid);
$stmt->execute();
$user_result = $stmt->get_result();
$user = $user_result->fetch_assoc();
?>

<?php
$created_sql = "
SELECT od.*, e.content AS event_name 
FROM order_detail od
JOIN event e ON od.event_id = e.event_id
WHERE od.booker = ?";
$stmt = $conn->prepare($created_sql);
$stmt->bind_param("s", $uid);
$stmt->execute();
$created_events = $stmt->get_result();
?>

<?php
$joined_sql = "
SELECT od.*, e.content AS event_name, u.username AS booker_username, i.eval_to_booker, i.booker_eval, i.evaluation 
FROM involvement i
JOIN order_detail od ON i.orderid = od.orderid
JOIN event e ON od.event_id = e.event_id
JOIN user u ON od.booker = u.uid
WHERE i.uid = ?";
$stmt = $conn->prepare($joined_sql);
$stmt->bind_param("s", $uid);
$stmt->execute();
$joined_events = $stmt->get_result();
?>

<?php
$feedback_sql = "
SELECT i.booker_eval, od.orderid, e.content AS event_name, u.name AS booker_name 
FROM involvement i
JOIN order_detail od ON i.orderid = od.orderid
JOIN event e ON od.event_id = e.event_id
JOIN user u ON od.booker = u.uid
WHERE i.uid = ? AND i.booker_eval IS NOT NULL
";
$stmt = $conn->prepare($feedback_sql);
$stmt->bind_param("s", $uid);
$stmt->execute();
$feedbacks = $stmt->get_result();
?>

<?php
$evaluation_sql = "
SELECT 
  SUM(CASE WHEN i.evaluation = 1 THEN 1 ELSE 0 END) AS likes,
  SUM(CASE WHEN i.evaluation = -1 THEN 1 ELSE 0 END) AS dislikes
FROM involvement i
JOIN order_detail o ON i.orderid = o.orderid
WHERE i.uid = ? AND o.booker != i.uid
";
$stmt = $conn->prepare($evaluation_sql);
$stmt->bind_param("s", $uid);
$stmt->execute();
$eval_result = $stmt->get_result();
$eval_data = $eval_result->fetch_assoc();
?>

<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // 更新用戶資料
    $new_username = $_POST['username'] ?? '';
    $new_name = $_POST['name'] ?? '';
    $new_gender = $_POST['gender'] ?? '';
    $new_birthday = $_POST['birthday'] ?? null;
    $new_phone = $_POST['phone'] ?? '';
    $new_intro = $_POST['self_introduction'] ?? '';

    $update_sql = "
        UPDATE user SET 
            username = ?, 
            name = ?, 
            gender = ?, 
            birthday = ?, 
            phone = ?, 
            self_introduction = ? 
        WHERE uid = ?";
    $stmt = $conn->prepare($update_sql);
    $stmt->bind_param("sssssss", $new_username, $new_name, $new_gender, $new_birthday, $new_phone, $new_intro, $uid);
    $stmt->execute();

    // 重新載入最新資料
    header("Location: profile.php?edit=success");
    exit;
}
?>




<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <title>個人檔案 - <?php echo htmlspecialchars($user['username']); ?></title>
  <link rel="stylesheet" href="profile.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>
<body>
    <div class="container">

        <div class="profile-info">
            <h1>使用者個人資料</h1>

            <!-- 顯示模式 -->
            <?php if ($canEdit): ?>
                <!-- 顯示完整版 + 編輯按鈕 -->
                <div id="view-mode">
                    <p><strong>暱稱：</strong> <?php echo htmlspecialchars($user['username']); ?></p>
                    <p><strong>真實姓名：</strong> <?php echo htmlspecialchars($user['name']); ?></p>
                    <p><strong>性別：</strong> <?php echo htmlspecialchars($user['gender']); ?></p>
                    <p><strong>生日：</strong> <?php echo htmlspecialchars($user['birthday']); ?></p>
                    <p><strong>電話：</strong> <?php echo htmlspecialchars($user['phone']); ?></p>
                    <p><strong>自我介紹：</strong> <?php echo htmlspecialchars($user['self_introduction'] ?? '尚未填寫'); ?></p>
                    <button class="edit-button" onclick="toggleEdit()">✏️ 編輯個資</button>
                </div>
                <!-- 編輯表單同 profile.php -->
            <?php else: ?>
                <!-- 僅顯示 preview 內容 -->
                <p><strong>暱稱：</strong> <?php echo htmlspecialchars($user['username']); ?></p>
                <p><strong>性別：</strong> <?php echo htmlspecialchars($user['gender'] ?? '未填寫'); ?></p>
                <p><strong>自我介紹：</strong> <?php echo nl2br(htmlspecialchars($user['self_introduction'] ?? '尚未填寫')); ?></p>
            <?php endif; ?>


            <!-- 編輯模式 -->
            <form id="edit-mode" method="post" style="display:none;">
                <div class="form-group">
                    <label for="username">暱稱</label>
                    <input type="text" name="username" id="username" value="<?php echo htmlspecialchars($user['username']); ?>">
                </div>

                <div class="form-group">
                    <label for="name">真實姓名</label>
                    <input type="text" name="name" id="name" value="<?php echo htmlspecialchars($user['name']); ?>">
                </div>

                <div class="form-group">
                    <label for="gender">性別</label>
                    <select name="gender" id="gender">
                        <option value="男" <?php if ($user['gender'] === '男') echo 'selected'; ?>>男</option>
                        <option value="女" <?php if ($user['gender'] === '女') echo 'selected'; ?>>女</option>
                        <option value="其他" <?php if ($user['gender'] === '其他') echo 'selected'; ?>>其他</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="birthday">生日</label>
                    <input type="date" name="birthday" id="birthday" value="<?php echo $user['birthday']; ?>">
                </div>

                <div class="form-group">
                    <label for="phone">電話</label>
                    <input type="text" name="phone" id="phone" value="<?php echo htmlspecialchars($user['phone']); ?>">
                </div>

                <div class="form-group">
                    <label for="self_introduction">自我介紹</label>
                    <textarea name="self_introduction" id="self_introduction"><?php echo htmlspecialchars($user['self_introduction']); ?></textarea>
                </div>

                <button type="submit" class="edit-button">儲存</button>
                <button type="button" onclick="toggleEdit()" class="cancel-button">取消</button>
            </form>

        </div>

        <h2>我發起的活動</h2>
        <div class="event-card">
        <?php while ($row = $created_events->fetch_assoc()): ?>
            <div>
            <h3><?php echo htmlspecialchars($row['event_name']); ?></h3>
            <p>地點：<?php echo htmlspecialchars($row['location']); ?></p>
            <p>開始時間：<?php echo $row['start_time']; ?></p>
            <p>備註：<?php echo htmlspecialchars($row['annotation']); ?></p>
            <p>狀態：<?php echo $row['state']; ?></p>
            </div>
        <?php endwhile; ?>
        </div>


        <h2>我參加的活動</h2>
        <div class="event-card">
            <?php while ($row = $joined_events->fetch_assoc()): ?>
                <div>
                    <h3>
                        <?php echo htmlspecialchars($row['event_name']); ?>（主揪：
                        <a href="profile.php?uid=<?php echo urlencode($row['booker']); ?>" style="color: lightblue;">
                            <?php echo htmlspecialchars($row['booker_username']); ?>
                        </a>）
                    </h3>

                    <p>地點：<?php echo htmlspecialchars($row['location']); ?></p>
                    <p>開始時間：<?php echo $row['start_time']; ?></p>
                    <p>主揪評價：<?php echo htmlspecialchars($row['eval_to_booker'] ?? '未填寫'); ?></p>
                    <p>對我評價：<?php echo htmlspecialchars($row['booker_eval'] ?? '未填寫'); ?></p>
                    <p>整體評價：
                        <?php
                        if ($row['evaluation'] === null) echo '未評價';
                        elseif ($row['evaluation'] == 1) echo '👍';
                        elseif ($row['evaluation'] == -1) echo '👎';
                        ?>
                    </p>
                </div>
            <?php endwhile; ?>
        </div>

        <h2>評價統計</h2>
        <div class="stat-box">
            <p><strong>👍 收到的讚數：</strong> <?php echo $eval_data['likes'] ?? 0; ?></p>
            <p><strong>👎 收到的倒讚數：</strong> <?php echo $eval_data['dislikes'] ?? 0; ?></p>
        </div>

    </div>

</body>
        <script>
            function toggleEdit() {
                const view = document.getElementById('view-mode');
                const edit = document.getElementById('edit-mode');
                view.style.display = (view.style.display === 'none') ? 'block' : 'none';
                edit.style.display = (edit.style.display === 'none') ? 'block' : 'none';
            }
        </script>
</html>

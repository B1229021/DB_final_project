<?php
require_once 'db_connect.php';

$uid = $_GET['uid'] ?? null;

if (!$uid) {
    echo "使用者不存在。";
    exit;
}

// 取得使用者基本資料（只取必要欄位、加入 gender 和 self_introduction）
$user_sql = "SELECT username, gender, self_introduction FROM user WHERE uid = ?";

$stmt = $conn->prepare($user_sql);
$stmt->bind_param("s", $uid);
$stmt->execute();
$user_result = $stmt->get_result();

if ($user_result->num_rows === 0) {
    echo "找不到此使用者。";
    exit;
}

$user = $user_result->fetch_assoc();

// 他發起的活動
$created_sql = "
SELECT od.*, e.content AS event_name 
FROM order_detail od
JOIN event e ON od.event_id = e.event_id
WHERE od.booker = ?";
$stmt = $conn->prepare($created_sql);
$stmt->bind_param("s", $uid);
$stmt->execute();
$created_events = $stmt->get_result();

// 他參加的活動
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

// 評價統計
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


<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <title><?php echo htmlspecialchars($user['username']); ?> 的個人預覽</title>
  <link rel="stylesheet" href="profile.css">
</head>
<body>
    <div class="container">
        <h1>使用者：<?php echo htmlspecialchars($user['username']); ?> 的個人檔案預覽</h1>
        <p><strong>性別：</strong> <?php echo htmlspecialchars($user['gender'] ?? '未填寫'); ?></p>
        <p><strong>自我介紹：</strong> <?php echo nl2br(htmlspecialchars($user['self_introduction'] ?? '尚未填寫')); ?></p>


        <h2>他發起的活動</h2>
        <div class="event-card">
        <?php if ($created_events->num_rows === 0): ?>
            <p>目前尚未發起任何活動。</p>
        <?php else: ?>
            <?php while ($row = $created_events->fetch_assoc()): ?>
                <div>
                    <h3><?php echo htmlspecialchars($row['event_name']); ?></h3>
                    <p>地點：<?php echo htmlspecialchars($row['location']); ?></p>
                    <p>時間：<?php echo $row['start_time']; ?></p>
                </div>
            <?php endwhile; ?>
        <?php endif; ?>
        </div>

        <h2>他參加的活動</h2>
        <div class="event-card">
        <?php if ($joined_events->num_rows === 0): ?>
            <p>目前尚未參加任何活動。</p>
        <?php else: ?>
            <?php while ($row = $joined_events->fetch_assoc()): ?>
                <div>
                    <h3>
                        <?php echo htmlspecialchars($row['event_name']); ?>（主揪：
                        <a href="preview_user.php?uid=<?php echo urlencode($row['booker']); ?>" style="color: lightblue;">
                            <?php echo htmlspecialchars($row['booker_username']); ?>
                        </a>）
                    </h3>
                    <p>地點：<?php echo htmlspecialchars($row['location']); ?></p>
                    <p>時間：<?php echo $row['start_time']; ?></p>
                    <p>整體評價：<?php
                        if ($row['evaluation'] === null) echo '未評價';
                        elseif ($row['evaluation'] == 1) echo '👍';
                        elseif ($row['evaluation'] == -1) echo '👎';
                    ?></p>
                </div>
            <?php endwhile; ?>
        <?php endif; ?>
        </div>

        <h2>評價統計</h2>
        <div class="stat-box">
            <p><strong>👍 收到的讚數：</strong> <?php echo $eval_data['likes'] ?? 0; ?></p>
            <p><strong>👎 收到的倒讚數：</strong> <?php echo $eval_data['dislikes'] ?? 0; ?></p>
        </div>
    </div>
</body>
</html>

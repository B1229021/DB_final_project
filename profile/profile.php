<?php
session_start();
require_once 'db_connect.php'; // 假設這個檔案裡有 $conn 的資料庫連線
$uid = $_SESSION['uid'] ?? "f8dh3ld8bnwe3bfx8hre3jt7b01gvd";

if (!$uid) {
    header('Location: login.php');
    exit;
}
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
SELECT od.*, e.content AS event_name, u.name AS booker_name, i.eval_to_booker, i.booker_eval, i.evaluation 
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
            <p><strong>暱稱：</strong> <?php echo htmlspecialchars($user['username']); ?></p>
            <p><strong>真實姓名：</strong> <?php echo htmlspecialchars($user['name']); ?></p>
            <p><strong>性別：</strong> <?php echo htmlspecialchars($user['gender']); ?></p>
            <p><strong>生日：</strong> <?php echo htmlspecialchars($user['birthday']); ?></p>
            <p><strong>電話：</strong> <?php echo htmlspecialchars($user['phone']); ?></p>
            <p><strong>自我介紹：</strong> <?php echo htmlspecialchars($user['self_introduction'] ?? '尚未填寫'); ?></p>
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
                    <h3><?php echo htmlspecialchars($row['event_name']); ?>（主揪：<?php echo htmlspecialchars($row['booker_name']); ?>）</h3>
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
        </div>

        <h2>評價統計</h2>
        <div class="stat-box">
            <p><strong>👍 收到的讚數：</strong> <?php echo $eval_data['likes'] ?? 0; ?></p>
            <p><strong>👎 收到的倒讚數：</strong> <?php echo $eval_data['dislikes'] ?? 0; ?></p>
        </div>


        <!-- <h2>歷史收到的評價</h2>
            <div class="event-card">
                <?php if ($feedbacks->num_rows === 0): ?>
                <p>目前尚未收到評價。</p>
                <?php else: ?>
                <?php while ($row = $feedbacks->fetch_assoc()): ?>
                    <div class="event-card">
                    <h3><?php echo htmlspecialchars($row['event_name']); ?>（活動 ID：<?php echo $row['orderid']; ?>）</h3>
                    <p><strong>主揪 <?php echo htmlspecialchars($row['booker_name']); ?> 給您的評價：</strong></p>
                    <p><?php echo htmlspecialchars($row['booker_eval']); ?></p>
                    </div>
                <?php endwhile; ?>
            <?php endif; ?>
        </div> -->


</body>
</html>

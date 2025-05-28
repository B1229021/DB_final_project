<?php
session_start();
require_once("project.php"); // 請確認這裡能連線到 `project` 資料庫

$uid = $_SESSION['uid']; // 登入者的 uid

// POST：儲存評分與評論
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $orderid = $_POST['orderid'];
    $target_uid = $_POST['uid']; // 要評價的對象（發起者或參與者）
    $comment = $_POST['comment'];
    $evaluation = intval($_POST['evaluation']);

    // 取得該活動的發起者
    $stmt = $conn->prepare("SELECT booker_id FROM order_detail WHERE orderid = ?");
    $stmt->bind_param("i", $orderid);
    $stmt->execute();
    $result = $stmt->get_result();
    $booker_id = $result->fetch_assoc()['booker_id'];

    if ($uid === $booker_id) {
        // 發起者對參與者評價
        $sql = "UPDATE involvement SET booker_eval = ?, evaluation = ? WHERE orderid = ? AND uid = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("siis", $comment, $evaluation, $orderid, $target_uid);
    } else {
        // 參與者對發起者評價
        $sql = "UPDATE involvement SET eval_to_booker = ?, evaluation = ? WHERE orderid = ? AND uid = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("siis", $comment, $evaluation, $orderid, $uid);
    }

    if ($stmt->execute()) {
        echo "評分成功";
    } else {
        echo "評分失敗：" . $stmt->error;
    }
    exit;
}

// GET：取得歷史活動
$sql = "
SELECT od.orderid, od.title, od.location, od.time, od.booker_id,
       inv.uid, inv.eval_to_booker, inv.booker_eval, inv.evaluation
FROM order_detail od
JOIN involvement inv ON od.orderid = inv.orderid
WHERE (inv.uid = ? OR od.booker_id = ?) AND od.status = '已完成'
ORDER BY od.time DESC
";

$stmt = $conn->prepare($sql);
$stmt->bind_param("ss", $uid, $uid);
$stmt->execute();
$result = $stmt->get_result();

$events = [];
while ($row = $result->fetch_assoc()) {
    $can_rate = false;

    if ($uid === $row['booker_id'] && ($row['booker_eval'] === null)) {
        // 發起人尚未評論
        $can_rate = true;
    } elseif ($uid === $row['uid'] && ($row['eval_to_booker'] === null)) {
        // 參與者尚未評論
        $can_rate = true;
    }

    $events[] = [
        'orderid' => $row['orderid'],
        'title' => $row['title'],
        'location' => $row['location'],
        'time' => $row['time'],
        'uid' => ($uid === $row['booker_id']) ? $row['uid'] : $row['booker_id'], // 評分對象 uid
        'participants' => [], // 匿名處理
        'can_rate' => $can_rate,
    ];
}

echo json_encode($events);
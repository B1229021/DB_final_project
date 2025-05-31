<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header("Content-Type: application/json");
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}
$mysqli = new mysqli('localhost', 'root', '', 'project');
$mysqli->set_charset('utf8mb4');

if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode(['error' => '資料庫連線失敗']);
    exit;
}

$action = $_GET['action'] ?? '';

if ($action == 'ping') { echo json_encode(['pong'=>true]); exit; }

function fetch_all($sql, $params = [], $types = '') {
    global $mysqli;
    $stmt = $mysqli->prepare($sql);
    if ($params && $types) $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $result = $stmt->get_result();
    return $result->fetch_all(MYSQLI_ASSOC);
}

// 類別
if ($action == 'list_categories') {
    $rows = fetch_all("SELECT categories_id, content FROM categories");
    echo json_encode($rows); exit;
}

// 活動種類
if ($action == 'list_event_types') {
    $rows = fetch_all("SELECT e.event_id, e.content, c.categories_id, c.content as category_name FROM event e LEFT JOIN categories c ON e.categories_id=c.categories_id");
    echo json_encode($rows); exit;
}

// 用戶
if ($action == 'list_users') {
    $rows = fetch_all("SELECT uid, username, name, gender, isadmin FROM user");
    foreach ($rows as &$u) {
        $reviews = fetch_all("SELECT evaluation, eval_to_booker FROM involvement WHERE uid=?", [$u['uid']], "s");
        $u['review_good'] = count(array_filter($reviews, fn($r)=>$r['evaluation']==1));
        $u['review_bad'] = count(array_filter($reviews, fn($r)=>$r['evaluation']==-1));
        $u['review_msgs'] = array_column($reviews, 'eval_to_booker');
        $u['avatarUrl'] = ""; // 依需求
    }
    echo json_encode($rows); exit;
}

// 活動列表
if ($action == 'list_events') {
    $where = [];
    $params = [];
    $types = '';
    if (!empty($_GET['cat'])) {$where[]="c.categories_id=?"; $params[]=$_GET['cat']; $types.='i';}
    if (!empty($_GET['time'])) {$where[]="od.deadtime>=?"; $params[]=$_GET['time']; $types.='s';}
    $sql = "SELECT od.*, e.content as event_name, c.content as category_name, c.categories_id, 
        COALESCE(od.male_limit+od.female_limit, od.participants) as participants_limit
        FROM order_detail od
        LEFT JOIN event e ON od.event_id = e.event_id
        LEFT JOIN categories c ON e.categories_id = c.categories_id";
    if ($where) $sql.=" WHERE ".implode(" AND ",$where);
    $sql.=" ORDER BY od.deadtime DESC";
    $events = fetch_all($sql, $params, $types);
    foreach ($events as &$ev) {
        $invs = fetch_all("SELECT uid FROM involvement WHERE orderid=?", [$ev['orderid']], "i");
        $ev['participants'] = array_column($invs, 'uid');
    }
    echo json_encode($events); exit;
}

// 活動詳情
if ($action == 'event_detail') {
    $orderid = $_GET['orderid'] ?? '';
    $evs = fetch_all("SELECT od.*, e.content as event_name, c.content as category_name, c.categories_id, 
        COALESCE(od.male_limit+od.female_limit, od.participants) as participants_limit
        FROM order_detail od
        LEFT JOIN event e ON od.event_id = e.event_id
        LEFT JOIN categories c ON e.categories_id = c.categories_id
        WHERE od.orderid=?", [$orderid], "i");
    if (!$evs) {echo json_encode(['error'=>'not found']); exit;}
    $ev = $evs[0];
    $invs = fetch_all("SELECT uid FROM involvement WHERE orderid=?", [$orderid], "i");
    $ev['participants'] = array_column($invs, 'uid');
    echo json_encode($ev); exit;
}

// 發起活動
if ($action == 'create_event' && $_SERVER['REQUEST_METHOD']==='POST') {
    $booker = $_POST['booker']??'';
    $event_id = $_POST['eventType']??'';
    $deadtime = $_POST['deadtime']??'';
    $location = $_POST['location']??'';
    $participants = $_POST['participants']??'';
    $annotation = $_POST['annotation']??'';
    $stmt = $mysqli->prepare("INSERT INTO order_detail(booker, location, deadtime, annotation, participants, state, event_id) VALUES (?,?,?,?,?,'已成立',?)");
    $stmt->bind_param("ssssii", $booker, $location, $deadtime, $annotation, $participants, $event_id);
    $stmt->execute();
    // 自動讓發起人參加
    $orderid = $mysqli->insert_id;
    $stmt = $mysqli->prepare("INSERT INTO involvement(orderid, uid, evaluation) VALUES (?, ?, NULL)");
    $stmt->bind_param("is", $orderid, $booker);
    $stmt->execute();
    echo json_encode(['message'=>'活動已發起']); exit;
}

// 參加活動
if ($action == 'join_event' && $_SERVER['REQUEST_METHOD']==='POST') {
    $orderid = $_POST['orderid'] ?? '';
    $uid = $_POST['uid'] ?? '';
    $check = fetch_all("SELECT * FROM involvement WHERE orderid=? AND uid=?", [$orderid, $uid], "is");
    if ($check) { echo json_encode(['message'=>'您已參與']); exit; }
    $od = fetch_all("SELECT COALESCE(male_limit+female_limit, participants) as participants_limit FROM order_detail WHERE orderid=?", [$orderid], "i");
    $curr = fetch_all("SELECT COUNT(*) as cnt FROM involvement WHERE orderid=?", [$orderid], "i");
    if ($curr[0]['cnt'] >= $od[0]['participants_limit']) { echo json_encode(['message'=>'活動已滿']); exit; }
    $stmt = $mysqli->prepare("INSERT INTO involvement(orderid, uid, evaluation) VALUES (?, ?, NULL)");
    $stmt->bind_param("is", $orderid, $uid);
    $stmt->execute();
    echo json_encode(['message'=>'加入成功']); exit;
}
// 退出活動
if ($action == 'leave_event' && $_SERVER['REQUEST_METHOD']==='POST') {
    $orderid = $_POST['orderid'] ?? '';
    $uid = $_POST['uid'] ?? '';
    $od = fetch_all("SELECT booker FROM order_detail WHERE orderid=?", [$orderid], "i");
    if ($od && $od[0]['booker'] === $uid) { echo json_encode(['message'=>'發起人無法退出']); exit; }
    $stmt = $mysqli->prepare("DELETE FROM involvement WHERE orderid=? AND uid=?");
    $stmt->bind_param("is", $orderid, $uid);
    $stmt->execute();
    echo json_encode(['message'=>'已退出']); exit;
}
// 取消活動
if ($action == 'cancel_event' && $_SERVER['REQUEST_METHOD']==='POST') {
    $orderid = $_POST['orderid'] ?? '';
    $uid = $_POST['uid'] ?? '';
    $od = fetch_all("SELECT booker FROM order_detail WHERE orderid=?", [$orderid], "i");
    if (!$od || $od[0]['booker'] !== $uid) { echo json_encode(['message'=>'只有發起人可取消']); exit; }
    $stmt = $mysqli->prepare("DELETE FROM order_detail WHERE orderid=?");
    $stmt->bind_param("i", $orderid);
    $stmt->execute();
    echo json_encode(['message'=>'活動已取消']); exit;
}



http_response_code(400);
echo json_encode(['error'=>'unknown action']);
exit;
<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *'); // CORS

require_once 'conn.php';

$action = $_GET['action'] ?? '';

function getEventParticipantsAndEvaluation($conn, $orderid) {
    // 取得參加者清單
    $stmt = $conn->prepare("SELECT uid, evaluation FROM involvement WHERE orderid=?");
    $stmt->execute([$orderid]);
    $participants = [];
    $evals = [];
    foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $row) {
        $participants[] = $row['uid'];
        if (!isset($evals[$row['uid']])) $evals[$row['uid']] = ['good'=>0, 'bad'=>0];
        if ($row['evaluation'] == 1) $evals[$row['uid']]['good'] += 1;
        if ($row['evaluation'] == -1) $evals[$row['uid']]['bad'] += 1;
    }
    return [$participants, $evals];
}

switch ($action) {
    case 'list_categories':
        $result = $conn->query("SELECT * FROM categories");
        echo json_encode($result->fetchAll(PDO::FETCH_ASSOC));
        break;

    case 'list_event_types':
        $result = $conn->query("SELECT e.event_id, e.content, c.categories_id, c.content AS category_name
                                FROM event e
                                JOIN categories c ON e.categories_id = c.categories_id");
        echo json_encode($result->fetchAll(PDO::FETCH_ASSOC));
        break;

    case 'list_users':
        $result = $conn->query("SELECT * FROM user");
        echo json_encode($result->fetchAll(PDO::FETCH_ASSOC));
        break;

    case 'list_events':
        $sql = "SELECT od.*, e.content AS event_name, c.content AS category_name
                FROM order_detail od
                JOIN event e ON od.event_id = e.event_id
                JOIN categories c ON e.categories_id = c.categories_id
                WHERE od.state != '已取消'";
        $conds = [];
        $params = [];
        if (!empty($_GET['cat'])) {
            $conds[] = "c.categories_id=?";
            $params[] = $_GET['cat'];
        }
        if (!empty($_GET['time'])) {
            $conds[] = "od.deadtime>=?";
            $params[] = $_GET['time'];
        }
        if ($conds) $sql .= " AND " . implode(" AND ", $conds);
        $sql .= " ORDER BY od.deadtime DESC";

        $stmt = $conn->prepare($sql);
        $stmt->execute($params);
        $events = $stmt->fetchAll(PDO::FETCH_ASSOC);

        foreach ($events as &$event) {
            list($participants, $evals) = getEventParticipantsAndEvaluation($conn, $event['orderid']);
            $event['participants_list'] = $participants; // 改名為 participants_list
            $event['evaluation'] = $evals;
        }
        echo json_encode($events);
        break;

    case 'event_detail':
        $orderid = $_GET['orderid'] ?? '';
        $stmt = $conn->prepare("SELECT od.*, e.content AS event_name, c.content AS category_name
                                FROM order_detail od
                                JOIN event e ON od.event_id = e.event_id
                                JOIN categories c ON e.categories_id = c.categories_id
                                WHERE od.orderid=?");
        $stmt->execute([$orderid]);
        $event = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($event) {
            list($participants, $evals) = getEventParticipantsAndEvaluation($conn, $event['orderid']);
            $event['participants_list'] = $participants; // 改名為 participants_list
            $event['evaluation'] = $evals;
        }
        echo json_encode($event);
        break;

    case 'create_event':
        $booker = $_POST['booker'] ?? '';
        $eventType = $_POST['eventType'] ?? '';
        $start_time = $_POST['start_time'] ?? '';
        $deadtime = $_POST['deadtime'] ?? '';
        $location = $_POST['location'] ?? '';
        $participants_limit = $_POST['participants'] ?? 1;
        $annotation = $_POST['annotation'] ?? '';
        // 取得 event_id, category_id, category_name, event_name
        $stmtType = $conn->prepare("SELECT e.event_id, e.content AS event_name, c.categories_id, c.content AS category_name
                                    FROM event e
                                    JOIN categories c ON e.categories_id = c.categories_id
                                    WHERE e.event_id=?");
        $stmtType->execute([$eventType]);
        $etype = $stmtType->fetch(PDO::FETCH_ASSOC);
        if (!$etype) {
            echo json_encode(['success'=>false, 'message'=>'活動種類不存在']);
            exit;
        }
        // 新增活動(主檔)
        $sql = "INSERT INTO order_detail (booker, location, deadtime, start_time, annotation, participants, state, event_id)
                VALUES (?, ?, ?, ?, ?, ?, '進行中', ?)";
        $stmt = $conn->prepare($sql);
        $ok = $stmt->execute([
            $booker, $location, $deadtime, $start_time, $annotation, $participants_limit, $eventType
        ]);
        if ($ok) {
            $orderid = $conn->lastInsertId();
            // 自己自動加入 involvement
            $stmtP = $conn->prepare("INSERT INTO involvement (orderid, uid) VALUES (?, ?)");
            $stmtP->execute([$orderid, $booker]);
            echo json_encode(['success'=>true, 'message'=>'活動已建立']);
        } else {
            echo json_encode(['success'=>false, 'message'=>'建立失敗']);
        }
        break;

    case 'join_event':
        $orderid = $_POST['orderid'] ?? '';
        $uid = $_POST['uid'] ?? '';
        if (!$orderid || !$uid) {
            echo json_encode(['success'=>false, 'message'=>'缺少參數']);
            exit;
        }
        $stmt = $conn->prepare("SELECT COUNT(*) FROM involvement WHERE orderid=? AND uid=?");
        $stmt->execute([$orderid, $uid]);
        if ($stmt->fetchColumn() > 0) {
            echo json_encode(['success'=>false, 'message'=>'已參加']);
            exit;
        }
        $stmt = $conn->prepare("SELECT participants FROM order_detail WHERE orderid=?");
        $stmt->execute([$orderid]);
        $max = $stmt->fetchColumn();
        $stmt = $conn->prepare("SELECT COUNT(*) FROM involvement WHERE orderid=?");
        $stmt->execute([$orderid]);
        $count = $stmt->fetchColumn();
        if ($count >= $max) {
            echo json_encode(['success'=>false, 'message'=>'人數已滿']);
            exit;
        }
        $stmt = $conn->prepare("INSERT INTO involvement (orderid, uid) VALUES (?, ?)");
        $ok = $stmt->execute([$orderid, $uid]);
        echo json_encode(['success'=>$ok, 'message'=>$ok?'加入成功':'加入失敗']);
        break;

    case 'leave_event':
        $orderid = $_POST['orderid'] ?? '';
        $uid = $_POST['uid'] ?? '';
        if (!$orderid || !$uid) {
            echo json_encode(['success'=>false, 'message'=>'缺少參數']);
            exit;
        }
        $stmt = $conn->prepare("DELETE FROM involvement WHERE orderid=? AND uid=?");
        $ok = $stmt->execute([$orderid, $uid]);
        echo json_encode(['success'=>$ok, 'message'=>$ok?'已退出':'退出失敗']);
        break;

    case 'cancel_event':
        $orderid = $_POST['orderid'] ?? '';
        $uid = $_POST['uid'] ?? '';
        $stmt = $conn->prepare("SELECT booker FROM order_detail WHERE orderid=?");
        $stmt->execute([$orderid]);
        $booker = $stmt->fetchColumn();
        if ($booker != $uid) {
            echo json_encode(['success'=>false, 'message'=>'只有發起人能取消活動']);
            exit;
        }
        $stmt = $conn->prepare("UPDATE order_detail SET state='已取消' WHERE orderid=?");
        $ok = $stmt->execute([$orderid]);
        echo json_encode(['success'=>$ok, 'message'=>$ok?'已取消活動':'取消失敗']);
        break;

    case 'end_event':
        $orderid = $_POST['orderid'] ?? '';
        $uid = $_POST['uid'] ?? '';
        $stmt = $conn->prepare("SELECT booker FROM order_detail WHERE orderid=?");
        $stmt->execute([$orderid]);
        $booker = $stmt->fetchColumn();
        if ($booker != $uid) {
            echo json_encode(['success'=>false, 'message'=>'只有發起人能結束活動']);
            exit;
        }
        $stmt = $conn->prepare("UPDATE order_detail SET state='已結束' WHERE orderid=?");
        $ok = $stmt->execute([$orderid]);
        echo json_encode(['success'=>$ok, 'message'=>$ok?'已結束活動':'結束失敗']);
        break;

    case 'list_my_events':
        $uid = $_GET['uid'] ?? '';
        $stmt = $conn->prepare("SELECT od.*, e.content AS event_name, c.content AS category_name
                                FROM order_detail od
                                JOIN event e ON od.event_id = e.event_id
                                JOIN categories c ON e.categories_id = c.categories_id
                                WHERE od.booker=? ORDER BY od.deadtime DESC");
        $stmt->execute([$uid]);
        $events = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($events as &$event) {
            list($participants, $evals) = getEventParticipantsAndEvaluation($conn, $event['orderid']);
            $event['participants_list'] = $participants; // 改名為 participants_list
            $event['evaluation'] = $evals;
        }
        echo json_encode($events);
        break;

    default:
        echo json_encode(['error'=>'未知 action']);
        break;
}
?>

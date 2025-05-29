<?php
if (isset($_GET['action'])) {
    header('Content-Type: application/json');
    $host = 'localhost';
    $dbname = 'db_project';
    $user = 'root';
    $pass = '12345678';
    try {
        $conn = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $user, $pass);
        $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } catch (PDOException $e) {
        echo json_encode(["error" => "資料庫連線失敗: " . $e->getMessage()]);
        exit;
    }
    $action = $_GET['action'] ?? '';
    function getEventParticipantsAndEvaluation($conn, $orderid) {
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
                $event['participants_list'] = $participants;
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
                $event['participants_list'] = $participants;
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
            $sql = "INSERT INTO order_detail (booker, location, deadtime, start_time, annotation, participants, state, event_id)
                    VALUES (?, ?, ?, ?, ?, ?, '進行中', ?)";
            $stmt = $conn->prepare($sql);
            $ok = $stmt->execute([
                $booker, $location, $deadtime, $start_time, $annotation, $participants_limit, $eventType
            ]);
            if ($ok) {
                $orderid = $conn->lastInsertId();
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
                $event['participants_list'] = $participants;
                $event['evaluation'] = $evals;
            }
            echo json_encode($events);
            break;
        default:
            echo json_encode(['error'=>'未知 action']);
            break;
    }
    exit;
}
?>
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>相約系統</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
     * {
            margin: 0;
            padding: 0;
            box-sizing: border-box; /* 讓邊框和內距包含在元素總寬度內 */
        }

        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            /* 設定漸層背景色 */
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; /* 確保頁面至少佔滿整個視窗高度 */
            color: #333;
        }

        /* ========== 主要容器樣式 ========== */
        .container {
            max-width: 1200px;
            margin: 0 auto; /* 水平置中 */
            padding: 0 15px;
            min-height: 100vh;
        }

        /* ========== 頁面標題區域 ========== */
        .header {
            background: rgba(255, 255, 255, 0.95); /* 半透明白色背景 */
            backdrop-filter: blur(10px); /* 背景模糊效果 */
            padding: 1rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); /* 陰影效果 */
            text-align: center;
        }

        .header h1 {
            color: #764ba2;
            font-size: 1.8rem;
            font-weight: 700;
        }

        /* ========== 控制面板樣式 ========== */
        .control-panel {
            background: rgba(255, 255, 255, 0.9);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            display: flex;
            gap: 15px; /* 元素間距 */
            flex-wrap: wrap; /* 允許換行 */
            align-items: center;
        }

        /* ========== 按鈕基礎樣式 ========== */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px; /* 圓角按鈕 */
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease; /* 平滑過渡效果 */
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        /* 主要按鈕樣式（漸層藍紫色） */
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px); /* 懸停時向上移動 */
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        }

        /* 次要按鈕樣式（灰色） */
        .btn-secondary {
            background: #f8f9fa;
            color: #666;
            border: 1px solid #ddd;
        }

        /* 危險按鈕樣式（紅色） */
        .btn-danger {
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
        }

        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
        }

        /* ========== 表單控制項樣式 ========== */
        .select-dropdown, .time-input {
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 0.9rem;
            background: white;
            transition: all 0.3s ease;
            min-width: 150px;
        }

        /* ========== 活動列表網格佈局 ========== */
        .events-list {
            display: grid;
            /* 響應式網格：每列最少300px寬度，自動填滿 */
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem; /* 網格間距 */
            margin-bottom: 2rem;
        }

        /* ========== 活動卡片樣式 ========== */
        .event-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer; /* 滑鼠指標變成手型 */
        }

        /* 卡片懸停效果 */
        .event-card:hover {
            transform: translateY(-5px); /* 向上浮起效果 */
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }

        /* 活動卡片頭部區域 */
        .event-header {
            display: flex;
            justify-content: space-between; /* 兩端對齊 */
            align-items: center;
            margin-bottom: 1rem;
        }

        /* 活動類別標籤 */
        .event-category {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        /* 活動時間顯示 */
        .event-time {
            color: #666;
            font-size: 0.9rem;
            font-weight: 500;
        }

        /* ========== 活動詳情區域 ========== */
        .event-details {
            margin-bottom: 1rem;
        }

        /* 每個詳情項目 */
        .event-detail-item {
            display: flex;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        /* 詳情標籤（如：活動、出發等） */
        .event-detail-label {
            font-weight: 600;
            color: #555;
            min-width: 80px; /* 固定寬度讓對齊更整齊 */
        }

        /* 詳情值 */
        .event-detail-value {
            color: #777;
            flex: 1; /* 佔據剩餘空間 */
        }
        .admin-btn {
            position: absolute;
            top: 18px;
            right: 32px;
            z-index: 10;
            background: linear-gradient(45deg, #ff9800, #ff5722);
            color: white;
            border: none;
            border-radius: 18px;
            padding: 10px 22px;
            font-weight: bold;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
            cursor: pointer;
            transition: all 0.2s;
        }
        .admin-btn:hover {
            background: linear-gradient(45deg, #ff5722, #ff9800);
        }

        .avatar-list {
            display: flex;
            flex-direction: row;
            gap: 0.5rem;
            align-items: center;
        }
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            overflow: hidden;
            border: 2px solid #fff;
            box-shadow: 0 2px 6px rgba(100,80,150,0.09);
            cursor: pointer;
            position: relative;
        }
        .avatar.creator::after {
            content: '👑';
            position: absolute;
            right: -10px;
            top: -10px;
            font-size: 1rem;
        }
        .avatar:hover {
            outline: 2px solid #764ba2;
        }

        /* 評價彈窗 */
        .user-review-modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.35);
        }
        .user-review-content {
            background: #fff;
            border-radius: 20px;
            width: 90%;
            max-width: 400px;
            margin: 6% auto;
            padding: 1.5rem 1rem 1rem 1rem;
            box-shadow: 0 18px 44px rgba(0,0,0,0.24);
            position: relative;
        }
        .close-user-review {
            position: absolute;
            top: 14px;
            right: 18px;
            font-size: 1.5rem;
            cursor: pointer;
            color: #888;
        }
        .user-review-header {
            text-align: center;
            margin-bottom: 1.2rem;
        }
        .user-review-header img {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            border: 3px solid #764ba2;
        }
        .user-review-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: #764ba2;
            margin-top: 0.3rem;
        }
        .user-review-gb {
            margin: 0.4rem 0 1rem 0;
            font-size: 1rem;
        }
        .review-msg-list {
            max-height: 160px;
            overflow-y: auto;
            margin-top: 0.7rem;
        }
        .review-msg-item {
            font-size: 0.97rem;
            padding: 0.3rem 0.2rem;
            border-bottom: 1px solid #eee;
        }
        .review-msg-item:last-child { border-bottom: none; }
        /* 性別人數下拉 */
        .gender-selects {
            display: flex;
            gap: 1rem;
        }
        .gender-selects .form-group {
            flex: 1;
            margin-bottom: 0;
        }
        .admin-btn {
            position: absolute;
            top: 18px;
            right: 32px;
            z-index: 100;
            background: linear-gradient(45deg, #ff9800, #ff5722);
            color: white;
            border: none;
            border-radius: 18px;
            padding: 10px 22px;
            font-weight: bold;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
            cursor: pointer;
            transition: all 0.2s;
        }
        .admin-btn:hover {
            background: linear-gradient(45deg, #ff5722, #ff9800);
        }
        /* ========== Modal z-index 修正 ========== */
        .modal {
            z-index: 2001 !important;
        }
        .user-review-modal {
            z-index: 2002 !important;
        }
        .modal {
    display: none;
    position: fixed;
    z-index: 2001;
    left: 0; top: 0;
    width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.35);
    justify-content: center;
    align-items: center;
}
.modal.show {
    display: flex;
}
.modal-content {
    background: #fff;
    border-radius: 20px;
    min-width: 340px;
    max-width: 430px;
    width: 96%;
    box-shadow: 0 18px 44px rgba(0,0,0,0.24);
    position: relative;
    padding: 2rem 2rem 1.2rem 2rem;
    animation: modalFadeIn 0.32s;
}
@keyframes modalFadeIn {
    from { opacity: 0; transform: translateY(30px);}
    to { opacity: 1; transform: translateY(0);}
}
.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.2rem;
}
.modal-header h2 {
    color: #6c48c9;
    font-size: 1.28rem;
    margin: 0;
    font-weight: bold;
}
.close {
    font-size: 1.6rem;
    cursor: pointer;
    color: #888;
    font-weight: bold;
    transition: color 0.2s;
}
.close:hover {
    color: #444;
}
.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
}
        .user-btn {
            position: absolute;
            top: 18px;
            left: 32px;
            z-index: 20;
            background: linear-gradient(45deg, #009688, #26c6da);
            color: white;
            border: none;
            border-radius: 18px;
            padding: 10px 22px;
            font-weight: bold;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
            cursor: pointer;
            transition: all 0.2s;
        }
        .user-btn:hover {
            background: linear-gradient(45deg, #26c6da, #009688);
        }
        .history-btn {
            /* 歷史紀錄按鈕樣式 */
            background: linear-gradient(45deg, #8e24aa, #ba68c8);
            color: white;
            border: none;
            border-radius: 18px;
            padding: 10px 22px;
            font-weight: bold;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
            cursor: pointer;
            transition: all 0.2s;
        }
        .history-btn:hover {
            background: linear-gradient(45deg, #ba68c8, #8e24aa);
        }
        /* 歷史紀錄 Modal */
        #historyModal.modal {
            z-index: 2100;
        }
        /* 讚/倒讚顯示 */
        .eval-area { display:inline-flex; align-items:center; gap:4px; font-size:0.95em;}
        .eval-good {color: #388e3c; margin-left:3px;}
        .eval-bad {color: #d32f2f; margin-left:3px;}
        .member-btn {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 2px 10px;
            border: 1px solid #ddd;
            margin: 0 3px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.2s;
        }
        .member-btn:hover {
            background: #e0e0ff;
        }
</head>
<body>
    <!-- 你的HTML內容 -->
    <div class="container" style="position:relative">
    <!-- 使用者名稱按鈕（左上角） -->
    <button class="user-btn" id="userBtn"></button>
    <!-- 管理員按鈕（右上角） -->
    <button class="admin-btn" id="adminBtn">管理者</button>
    <header class="header"><h1>相約系統</h1></header>
    <main>
        <div class="control-panel">
            <button id="createBtn" class="btn btn-primary">發起活動</button>
            <select id="categoryFilter" class="select-dropdown"></select>
            <input type="datetime-local" id="timeFilter" class="time-input">
            <button id="filterBtn" class="btn btn-secondary">篩選</button>
            <button id="refreshBtn" class="btn btn-secondary">重新載入</button>
            <button id="historyBtn" class="history-btn">歷史紀錄</button>
        </div>
        <div id="eventsList" class="events-list"></div>
    </main>
</div>
<!-- 發起活動 Modal -->
<div id="createModal" class="modal">
     <div class="modal-content">
        <div class="modal-header">
            <h2>發起活動</h2>
            <span class="close" id="closeCreate">&times;</span>
        </div>
        <form id="createForm">
            <div class="form-group">
                <label>活動種類:</label>
                <select id="eventType" name="eventType" required></select>
            </div>
            <div class="form-group">
                <label>開始時間:</label>
                <input type="datetime-local" id="start_time" name="start_time" required>
            </div>
            <div class="form-group">
                <label>截止時間:</label>
                <input type="datetime-local" id="deadtime" name="deadtime" required>
            </div>
            <div class="form-group">
                <label>地點:</label>
                <input type="text" id="location" name="location" required>
            </div>
            <div class="form-group">
                <label>人數限制:</label>
                <input type="number" id="participants" name="participants" min="2" max="20" required>
            </div>
            <div class="form-group">
                <label>說明:</label>
                <textarea id="annotation" name="annotation"></textarea>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">確定發起</button>
                <button type="button" id="cancelCreate" class="btn btn-secondary">取消</button>
            </div>
        </form>
    </div>
</div>
<!-- 詳情 Modal -->
<div id="detailModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>活動詳情</h2>
            <span class="close" id="closeDetail">&times;</span>
        </div>
        <div id="detailContent"></div>
    </div>
</div>
<!-- 歷史紀錄 Modal -->
<div id="historyModal" class="modal">
    <div class="modal-content" style="max-width:650px;">
        <div class="modal-header">
            <h2>歷史發起活動紀錄</h2>
            <span class="close" id="closeHistory">&times;</span>
        </div>
        <div id="historyContent"></div>
    </div>
</div>
<script>
let CURRENT_UID = 'f8dh3ld8bnwe3bfx8hre3jt7b01gvd';
let usersCache = {};
let eventTypeCache = {};

async function loadCategories() {
    const resp = await fetch('index.php?action=list_categories');
    const cats = await resp.json();
    let html = `<option value="">所有類別</option>`;
    cats.forEach(c => html += `<option value="${c.categories_id}">${c.content}</option>`);
    document.getElementById('categoryFilter').innerHTML = html;
}
async function loadEventTypes() {
    const resp = await fetch('index.php?action=list_event_types');
    const types = await resp.json();
    let html = `<option value="">請選擇</option>`;
    types.forEach(e => {
        html += `<option value="${e.event_id}">${e.content}（${e.category_name}）</option>`;
        eventTypeCache[e.event_id] = e;
    });
    document.getElementById('eventType').innerHTML = html;
}
async function loadUsers() {
    const resp = await fetch('index.php?action=list_users');
    const users = await resp.json();
    users.forEach(u => { usersCache[u.uid] = u; });
    document.getElementById('userBtn').textContent = usersCache[CURRENT_UID]?.name || usersCache[CURRENT_UID]?.username || "我的檔案";
}
async function loadEvents(catId = '', time = '') {
    document.getElementById('eventsList').innerHTML = '載入中...';
    let url = 'index.php?action=list_events';
    let params = [];
    if (catId) params.push('cat='+encodeURIComponent(catId));
    if (time) params.push('time='+encodeURIComponent(time));
    if (params.length) url += '&' + params.join('&');
    const resp = await fetch(url);
    const events = await resp.json();
    renderEvents(events);
}
function renderEvents(events) {
    const now = new Date();
    let displayEvents = events.filter(event => {
        // 只顯示還沒截止的活動(deadtime尚未過)
        return !event.deadtime || (new Date(event.deadtime) > now);
    });
    if (!displayEvents.length) {
        document.getElementById('eventsList').innerHTML = '<div>目前沒有活動</div>';
        return;
    }
    document.getElementById('eventsList').innerHTML = displayEvents.map(event => {
        // 取得發起人
        let booker = usersCache[event.booker] || {name:"未知", uid: event.booker};
        // 取得參加者名單（排除發起人）
        let participants = (event.participants_list || []).filter(uid => uid !== event.booker).map(uid => usersCache[uid] || {name:"未知", uid});
        // 評價資料格式: {uid: {good:數量, bad:數量}}
        let evaluation = event.evaluation || {};
        // 目前人數＝所有 involvement 筆數（含發起人）
        let total = event.participants_list ? event.participants_list.length : 0;
        let max = event.participants;
        // 狀態
        let state = event.state || '';
        // 按鈕
        let actionBtn = '';
        if (event.booker === CURRENT_UID) {
            if (state === '已結束') {
                actionBtn = `<span class="btn btn-secondary">活動已結束</span>`;
            } else {
                actionBtn = `
                    <button class="btn btn-danger" onclick="event.stopPropagation(); cancelEvent('${event.orderid}')">取消活動</button>
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); endEvent('${event.orderid}')">結束活動</button>
                `;
            }
        } else if ((event.participants_list || []).includes(CURRENT_UID)) {
            actionBtn = `<button class="btn btn-secondary" onclick="event.stopPropagation(); leaveEvent('${event.orderid}')">取消參與</button>`;
        } else if (total >= max) {
            actionBtn = `<span class="btn btn-secondary">已滿</span>`;
        } else {
            actionBtn = `<button class="btn btn-primary" onclick="event.stopPropagation(); joinEvent('${event.orderid}')">加入 +1</button>`;
        }
        // 名單區
        let memberStr = `
            <span><b>發起人:</b>
                <button class="member-btn" onclick="event.stopPropagation(); gotoProfile('${booker.uid}')">${booker.name||booker.username||'未知'}</button>
                <span class="eval-area">
                    <span class="eval-good">👍${(evaluation[booker.uid]?.good)||0}</span>
                    <span class="eval-bad">👎${(evaluation[booker.uid]?.bad)||0}</span>
                </span>
            </span>
            <br>
            <span><b>參加者:</b>
                ${participants.length ? participants.map(u=>`
                    <button class="member-btn" onclick="event.stopPropagation(); gotoProfile('${u.uid}')">${u.name||u.username||'未知'}</button>
                    <span class="eval-area">
                        <span class="eval-good">👍${(evaluation[u.uid]?.good)||0}</span>
                        <span class="eval-bad">👎${(evaluation[u.uid]?.bad)||0}</span>
                    </span>
                `).join(' ') : '無'}
            </span>
        `;
        return `
        <div class="event-card" onclick="showEventDetail('${event.orderid}')">
            <div class="event-header">
                <span class="event-category">${event.category_name}</span>
                <span class="event-time">${event.deadtime ? event.deadtime.substr(5,11) : ''}</span>
            </div>
            <div class="event-details">
                <div class="event-detail-item"><span class="event-detail-label">活動:</span>
                    <span class="event-detail-value">${event.event_name||''}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">地點:</span>
                    <span class="event-detail-value">${event.location}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">說明:</span>
                    <span class="event-detail-value">${event.annotation||''}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">人數:</span>
                    <span class="event-detail-value">${total}/${max}</span></div>
            </div>
            <div style="margin-bottom:6px">${memberStr}</div>
            <div class="form-actions">${actionBtn}</div>
        </div>`;
    }).join('');
}

// --------- 活動詳情 Modal ---------
window.showEventDetail = async function(orderid) {
    const resp = await fetch(`index.php?action=event_detail&orderid=`+orderid);
    const event = await resp.json();
    let booker = usersCache[event.booker] || {name:"未知", uid: event.booker};
    let participants = (event.participants_list || []).filter(uid => uid !== event.booker).map(uid => usersCache[uid] || {name:"未知", uid});
    let evaluation = event.evaluation || {};
    let male = event.male_num || 0, female = event.female_num || 0;
    let state = event.state || '';
    let total = event.participants_list ? event.participants_list.length : 0;
    let actionBtn = '';
    if (event.booker === CURRENT_UID) {
        if (state === '已結束') {
            actionBtn = `<span class="btn btn-secondary">活動已結束</span>`;
        } else {
            actionBtn = `
                <button class="btn btn-danger" onclick="event.stopPropagation(); cancelEvent('${event.orderid}')">取消活動</button>
                <button class="btn btn-secondary" onclick="event.stopPropagation(); endEvent('${event.orderid}')">結束活動</button>
            `;
        }
    } else if ((event.participants_list || []).includes(CURRENT_UID)) {
        actionBtn = `<button class="btn btn-secondary" onclick="event.stopPropagation(); leaveEvent('${event.orderid}')">取消參與</button>`;
    } else if (total >= event.participants) {
        actionBtn = `<span class="btn btn-secondary">已滿</span>`;
    } else {
        actionBtn = `<button class="btn btn-primary" onclick="event.stopPropagation(); joinEvent('${event.orderid}')">加入 +1</button>`;
    }
    let memberStr = `
        <span><b>發起人:</b>
            <button class="member-btn" onclick="gotoProfile('${booker.uid}')">${booker.name||booker.username||'未知'}</button>
            <span class="eval-area">
                <span class="eval-good">👍${(evaluation[booker.uid]?.good)||0}</span>
                <span class="eval-bad">👎${(evaluation[booker.uid]?.bad)||0}</span>
            </span>
        </span>
        <br>
        <span><b>參加者:</b>
            ${participants.length ? participants.map(u=>`
                <button class="member-btn" onclick="gotoProfile('${u.uid}')">${u.name||u.username||'未知'}</button>
                <span class="eval-area">
                    <span class="eval-good">👍${(evaluation[u.uid]?.good)||0}</span>
                    <span class="eval-bad">👎${(evaluation[u.uid]?.bad)||0}</span>
                </span>
            `).join(' ') : '無'}
        </span>
    `;
    document.getElementById('detailContent').innerHTML = `
        <div>
            <div class="event-detail-item"><span class="event-detail-label">活動:</span><span class="event-detail-value">${event.event_name||''}</span></div>
            <div class="event-detail-item"><span class="event-detail-label">地點:</span><span class="event-detail-value">${event.location}</span></div>
            <div class="event-detail-item"><span class="event-detail-label">說明:</span><span class="event-detail-value">${event.annotation||''}</span></div>
            <div class="event-detail-item"><span class="event-detail-label">人數:</span><span class="event-detail-value">${total}/${event.participants}（男${male} 女${female}）</span></div>
            <div style="margin-bottom:6px">${memberStr}</div>
        </div>
        <div class="form-actions">${actionBtn}<button class="btn btn-secondary" onclick="document.getElementById('detailModal').style.display='none'">關閉</button></div>
    `;
    document.getElementById('detailModal').style.display = 'flex';
};

// --------- 活動參與/取消/結束/取消活動功能 ---------
async function joinEvent(orderid) {
    const resp = await fetch(`index.php?action=join_event`, {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `orderid=${orderid}&uid=${CURRENT_UID}`
    });
    const result = await resp.json();
    alert(result.message || "加入完成");
    await loadEvents();
}
async function leaveEvent(orderid) {
    const resp = await fetch(`index.php?action=leave_event`, {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `orderid=${orderid}&uid=${CURRENT_UID}`
    });
    const result = await resp.json();
    alert(result.message || "已取消參與");
    await loadEvents();
}
async function cancelEvent(orderid) {
    if (!confirm("確定要取消這個活動嗎？")) return;
    const resp = await fetch(`index.php?action=cancel_event`, {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `orderid=${orderid}&uid=${CURRENT_UID}`
    });
    const result = await resp.json();
    alert(result.message || "已取消活動");
    await loadEvents();
}
async function endEvent(orderid) {
    if (!confirm("確定要結束這個活動嗎？")) return;
    const resp = await fetch(`index.php?action=end_event`, {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `orderid=${orderid}&uid=${CURRENT_UID}`
    });
    const result = await resp.json();
    alert(result.message || "已結束活動");
    await loadEvents();
}

// --------- 跳轉個人頁 ---------
function gotoProfile(uid) {
    window.location.href = "profile.html?uid=" + encodeURIComponent(uid);
}

// --------- 歷史紀錄 Modal ---------
document.getElementById('historyBtn').onclick = async function() {
    // 從 API 取得歷史紀錄（僅顯示目前使用者為發起者的活動，含已結束/取消）
    const resp = await fetch(`index.php?action=list_my_events&uid=${CURRENT_UID}`);
    const events = await resp.json();
    // 渲染歷史紀錄
    document.getElementById('historyContent').innerHTML = events.length ? events.map(event => {
        let state = event.state || '';
        let actionBtn = '';
        if (state === '已結束') {
            actionBtn = `<span class="btn btn-secondary">活動已結束</span>`;
        } else {
            actionBtn = `
                <button class="btn btn-danger" onclick="endEvent('${event.orderid}')">結束活動</button>
                <button class="btn btn-secondary" onclick="cancelEvent('${event.orderid}')">取消活動</button>
            `;
        }
        return `
            <div class="event-card" style="margin-bottom:10px">
                <div class="event-header">
                    <span class="event-category">${event.category_name}</span>
                    <span class="event-time">${event.deadtime ? event.deadtime.substr(5,11) : ''}</span>
                    <span style="margin-left:20px;">狀態：${state || '進行中'}</span>
                </div>
                <div class="event-details">
                    <div class="event-detail-item"><span class="event-detail-label">活動:</span><span class="event-detail-value">${event.event_name||''}</span></div>
                    <div class="event-detail-item"><span class="event-detail-label">地點:</span><span class="event-detail-value">${event.location}</span></div>
                </div>
                <div class="form-actions">${actionBtn}</div>
            </div>
        `;
    }).join('') : '<div>尚無歷史紀錄</div>';
    document.getElementById('historyModal').style.display = 'flex';
};
document.getElementById('closeHistory').onclick = function() {
    document.getElementById('historyModal').style.display='none';
};

// --------- Modal顯示/隱藏 ---------
document.getElementById('createBtn').onclick = function() { document.getElementById('createModal').style.display='flex'; };
document.getElementById('closeCreate').onclick = function() { document.getElementById('createModal').style.display='none'; };
document.getElementById('cancelCreate').onclick = function() { document.getElementById('createModal').style.display='none'; };
document.getElementById('closeDetail').onclick = function() { document.getElementById('detailModal').style.display='none'; };

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) event.target.style.display = 'none';
};

// --------- 發起活動表單 ---------
document.getElementById('createForm').onsubmit = async function(e) {
    e.preventDefault();
    let data = new FormData(this);
    data.append('booker', CURRENT_UID);
    const resp = await fetch(`index.php?action=create_event`, {
        method: 'POST',
        body: data
    });
    const result = await resp.json();
    alert(result.message || "已發起");
    document.getElementById('createModal').style.display='none';
    await loadEvents();
};

// --------- 篩選與載入 ---------
document.getElementById('filterBtn').onclick = function() {
    const cat = document.getElementById('categoryFilter').value;
    const time = document.getElementById('timeFilter').value;
    loadEvents(cat, time);
};
document.getElementById('refreshBtn').onclick = function() {
    loadEvents();
};
document.getElementById('adminBtn').onclick = function() {
    if (usersCache[CURRENT_UID]?.isadmin=='1') {
        window.location.href = 'admin.html';
    } else {
        alert("您無管理員權限！");
    }
};
document.getElementById('userBtn').onclick = function() {
    gotoProfile(CURRENT_UID);
};
window.onload = async function() {
    await loadCategories();
    await loadEventTypes();
    await loadUsers();
    await loadEvents();
};
// ...其餘 JS 省略，只要 fetch('index.php?action=xxx') 即可，其餘都不用加 API_BASE_URL ...
</script>
</body>
</html>

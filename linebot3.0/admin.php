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

$action = $_GET['action'] ?? $_POST['action'] ?? '';

// 工具：簡單 fetch_all
function fetch_all($sql) {
    global $conn;
    $res = $conn->query($sql);
    $out = [];
    while ($row = $res->fetch_assoc()) $out[] = $row;
    return $out;
}

if ($action === 'list_categories') {
    echo json_encode(fetch_all("SELECT * FROM categories"));
    exit;
}
if ($action === 'add_category') {
    $name = $_POST['name'];
    $stmt = $conn->prepare("INSERT INTO categories (content) VALUES (?)");
    $stmt->bind_param("s", $name);
    $stmt->execute();
    echo json_encode(['success'=>true]);
    exit;
}
if ($action === 'delete_category') {
    $id = intval($_POST['id']);
    $stmt = $conn->prepare("DELETE FROM categories WHERE categories_id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    echo json_encode(['success'=>true]);
    exit;
}
if ($action === 'list_events') {
    $sql = "SELECT e.*, c.content AS category_name FROM event e
            LEFT JOIN categories c ON e.categories_id = c.categories_id";
    echo json_encode(fetch_all($sql));
    exit;
}
if ($action === 'list_orders') {
    $sql = "SELECT od.orderid, u.username, od.location, od.event_id, od.state
            FROM order_detail od
            LEFT JOIN user u ON od.booker = u.uid";
    echo json_encode(fetch_all($sql));
    exit;
}
if ($action === 'list_evals') {
    $sql = "SELECT i.orderid, u.username, i.eval_to_booker, i.booker_eval, i.evaluation
            FROM involvement i
            LEFT JOIN user u ON i.uid = u.uid";
    echo json_encode(fetch_all($sql));
    exit;
}
if ($action === 'list_users') {
    echo json_encode(fetch_all("SELECT * FROM user"));
    exit;
}

echo json_encode(['error'=>'unknown action']);
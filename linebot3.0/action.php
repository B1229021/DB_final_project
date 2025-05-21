<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");
header('Content-Type: application/json; charset=utf-8');

# 全域變數，修改ngrok抓的80
define('NGROK_URL', 'https://68a8-211-72-73-194.ngrok-free.app');


$host     = "localhost";
$user     = "root";
$password = "";
$database = "project";

$link = mysqli_connect($host, $user, $password, $database);
if (!$link) {
    http_response_code(500);
    echo json_encode(["error" => "無法連線 MySQL: " . mysqli_connect_error()]);
    exit;
}
mysqli_query($link, "SET NAMES utf8");

$list = [];

$action = isset($_GET['act']) ? $_GET['act'] : '';

switch ($action) {

    case 'professor':
    $sql    = "SELECT department, position, name FROM professor";
    $result = mysqli_query($link, $sql);
    if (!$result) {
        error_log("SQL Error (professor): " . mysqli_error($link));
        break;
    }
    
    $index = 1; // 計算第幾個教授
    while ($row = mysqli_fetch_assoc($result)) {
        $list[] = [
            "id" => $index, // 這裡使用遞增的 index 當作 id
            "department" => $row['department'],
            "position"   => $row['position'],
            "name"       => $row['name']
        ];
        $index++;
    }
    mysqli_free_result($result);
    break;

    case 'title':
        // 根據 department 查 position（文字欄位）
        if (!empty($_GET['val'])) {
            $dep = mysqli_real_escape_string($link, $_GET['val']);
            // 假設 professor.department 存的是「系名」文字
            $sql = "SELECT DISTINCT position 
                    FROM professor
                    WHERE department = '{$dep}'";
            $result = mysqli_query($link, $sql);
            if (!$result) {
                error_log("SQL Error (position): " . mysqli_error($link));
                break;
            }
            while ($row = mysqli_fetch_assoc($result)) {
                // 為了前端方便，我們把 title 同時當作 id
                $list[] = [
                    "id"    => $row['position'],  // 使用職稱作為 ID
                    "title" => $row['position']   // 改成 position，不是 title
                ];
            }
            mysqli_free_result($result);
        }
        break;

    case 'name':
        // 根據 title 查教授 name 與 id
        if (!empty($_GET['val'])) {
            $title = mysqli_real_escape_string($link, $_GET['val']);
            $sql = "SELECT id, name 
                    FROM professor 
                    WHERE title = '{$position}'";
            $result = mysqli_query($link, $sql);
            if (!$result) {
                error_log("SQL Error (name): " . mysqli_error($link));
                break;
            }
            while ($row = mysqli_fetch_assoc($result)) {
                $list[] = [
                    "id"   => $row['id'],
                    "name" => $row['name']
                ];
            }
            mysqli_free_result($result);
        }
        break;

    default:
        // 沒有 act 或 act 未定義時，回傳空陣列
        break;
}

mysqli_close($link);

// 最後輸出 JSON
echo json_encode($list, JSON_UNESCAPED_UNICODE);
exit;

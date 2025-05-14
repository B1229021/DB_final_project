<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");
header('Content-Type: application/json; charset=utf-8');

$host     = "localhost";
$user     = "root";
$password = "123456";
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
    case 'professors':
        // 回傳所有教授（包含 id, department, title, name）
        $sql    = "SELECT id, department, title, name FROM professors";
        $result = mysqli_query($link, $sql);
        if (!$result) {
            error_log("SQL Error (professors): " . mysqli_error($link));
            break;
        }
        while ($row = mysqli_fetch_assoc($result)) {
            $list[] = $row;
        }
        mysqli_free_result($result);
        break;

    case 'title':
        // 根據 department 查 title（文字欄位）
        if (!empty($_GET['val'])) {
            $dep = mysqli_real_escape_string($link, $_GET['val']);
            // 假設 professors.department 存的是「系名」文字
            $sql = "SELECT DISTINCT title 
                    FROM professors 
                    WHERE department = '{$dep}'";
            $result = mysqli_query($link, $sql);
            if (!$result) {
                error_log("SQL Error (title): " . mysqli_error($link));
                break;
            }
            while ($row = mysqli_fetch_assoc($result)) {
                // 為了前端方便，我們把 title 同時當作 id
                $list[] = [
                    "id"    => $row['title'],
                    "title" => $row['title']
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
                    FROM professors 
                    WHERE title = '{$title}'";
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

        case 'save_user':
            // 新增使用者資料
            // $line_id    = mysqli_real_escape_string($link, $_POST['line_id']);
            $u_id = mysqli_real_escape_string($link, $_POST['u_id']);
            $department = mysqli_real_escape_string($link, $_POST['department']);

            // if ($line_id && $student_id && $department) {
            //     $sql = "INSERT INTO users (line_id, student_id, department) VALUES ('$line_id', '$u_id', '$department')";
            //     if (mysqli_query($link, $sql)) {
            //         $list = ["status" => "success", "message" => "使用者資料已儲存"];
            //     } else {
            //         $list = ["status" => "error", "message" => "無法儲存資料：" . mysqli_error($link)];
            //     }
            // } else {
            //     $list = ["status" => "error", "message" => "缺少必要資料"];
            // }
            // break;
            if ($student_id && $department) {
                $sql = "INSERT INTO users (student_id, department) VALUES ('$u_id', '$department')";
                if (mysqli_query($link, $sql)) {
                    $list = ["status" => "success", "message" => "使用者資料已儲存"];
                } else {
                    $list = ["status" => "error", "message" => "無法儲存資料：" . mysqli_error($link)];
                }
            } else {
                $list = ["status" => "error", "message" => "缺少必要資料"];
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

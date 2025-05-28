<?php
$host = 'localhost';
$dbname = 'db_project';
$user = 'root';
$pass = '12345678';

try {
    $conn = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $user, $pass);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo "資料庫連線失敗: " . $e->getMessage();
    exit;
}
?>

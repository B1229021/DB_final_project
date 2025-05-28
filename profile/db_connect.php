<?php
$host = 'localhost';
$user = 'root';
$password = '12345678';
$dbname = 'db_project';

$conn = new mysqli($host, $user, $password, $dbname);
if ($conn->connect_error) {
    die('連線失敗：' . $conn->connect_error);
}
?>

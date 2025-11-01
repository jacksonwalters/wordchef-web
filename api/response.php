<?php
function json_response($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json');
    header('Access-Control-Allow-Origin: *'); // optional, for JS fetch()
    echo json_encode($data, JSON_PRETTY_PRINT);
    exit;
}
?>

<?php
header('Content-Type: application/json');
echo json_encode([
    'api' => 'WordChef REST API',
    'endpoints' => [
        '/api/nearest.php?words=word1,word2' => 'Returns nearest neighbors of averaged embedding'
    ]
], JSON_PRETTY_PRINT);
?>
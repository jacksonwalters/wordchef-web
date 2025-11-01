<?php
require_once('utils.php');
require_once('response.php');

$conn = db_connect();

// Parse input: either GET or POST
$input = $_GET['words'] ?? ($_POST['words'] ?? '');
if ($input === '') {
    json_response(['error' => 'Missing parameter: words'], 400);
}
$words = array_filter(array_map('trim', explode(',', $input)));

if (count($words) === 0) {
    json_response(['error' => 'No valid words provided'], 400);
}

// Fetch embeddings for each
$embeddings = [];
foreach ($words as $w) {
    $embeddings[] = fetch_embedding($conn, $w);
}

// Compute average
$average = average_embeddings($embeddings);
$average_str = '[' . implode(',', $average) . ']';

// Query nearest neighbors
$query = "SELECT word, embedding <-> $1 AS distance FROM wordembeddings ORDER BY embedding <-> $1 LIMIT 5";
$result = pg_query_params($conn, $query, [$average_str]);

$neighbors = [];
while ($row = pg_fetch_assoc($result)) {
    $neighbors[] = [
        'word' => $row['word'],
        'distance' => (float)$row['distance']
    ];
}
pg_free_result($result);
pg_close($conn);

// Return JSON response
json_response([
    'input' => $words,
    'nearest' => $neighbors
]);
?>

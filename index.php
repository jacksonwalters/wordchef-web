<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');

// Load database credentials from external config
$config = include('/var/www/wordchef.app/html/db_config.php');
$conn_string = sprintf(
    "host=%s port=%d dbname=%s user=%s password=%s",
    $config['host'],
    $config['port'],
    $config['dbname'],
    $config['user'],
    $config['password']
);

$conn = pg_connect($conn_string);
if (!$conn) {
    die("Connection failed: " . pg_last_error());
}

// Validate user input from forms
function validate_string($user_input, $max_len) {
    if ($user_input === '') return true; // allow empty
    if (!preg_match("/^[a-zA-Z0-9_]*$/", $user_input)) return false;
    if (strlen($user_input) > $max_len) return false;
    return true;
}

// Vector utilities
function add_arrays($arr1, $arr2) {
    $n = count($arr1);
    assert($n == count($arr2), "Arrays must be same length");
    $sum = [];
    for ($i = 0; $i < $n; $i++) {
        $sum[$i] = $arr1[$i] + $arr2[$i];
    }
    return $sum;
}

function scale_array($scalar, $arr) {
    $scaled = [];
    foreach ($arr as $val) {
        $scaled[] = $scalar * $val;
    }
    return $scaled;
}

// Initialize 300-dimensional zero vectors
$embedding_array_1 = array_fill(0, 300, 0);
$embedding_array_2 = array_fill(0, 300, 0);

$word_1 = $_POST['word_1'] ?? '';
$word_2 = $_POST['word_2'] ?? '';

$valid_input_1 = validate_string($word_1, 14);
$valid_input_2 = validate_string($word_2, 14);

// Function to fetch embedding safely with prepared statement
function fetch_embedding($conn, $word) {
    if ($word === '') return array_fill(0, 300, 0); // zero vector for empty input

    $query = "SELECT embedding FROM wordembeddings WHERE word = $1";
    $result = pg_query_params($conn, $query, [$word]);
    if ($row = pg_fetch_assoc($result)) {
        $embedding_string = str_replace(['[', ']'], '', $row['embedding']);
        return array_map('floatval', explode(',', $embedding_string));
    }
    return array_fill(0, 300, 0); // zero vector if word not found
}

// Fetch embeddings
$embedding_array_1 = $valid_input_1 ? fetch_embedding($conn, $word_1) : $embedding_array_1;
$embedding_array_2 = $valid_input_2 ? fetch_embedding($conn, $word_2) : $embedding_array_2;

// Compute average vector (sum and scale)
$sum_array = add_arrays($embedding_array_1, $embedding_array_2);
$average_array = scale_array(0.5, $sum_array);
$average_array_string = '[' . implode(',', $average_array) . ']';

?>

<html>
<head>
<title>wordchef</title>
</head>
<body>
<h1>wordchef</h1>
<p>This is a webapp which uses PHP + pgSQL w/ pgvector to lookup word embeddings, find their sum, and do a fast semantic similarity search to find the nearest five words.</p>

<form action="/" method="POST">
    Word 1: <input type="text" id="word_1" name="word_1" value="<?= htmlspecialchars($word_1) ?>">
    Word 2: <input type="text" id="word_2" name="word_2" value="<?= htmlspecialchars($word_2) ?>">
    <input type="submit" value="Submit">
</form>

<?php

// Generate vector image using external Python script
function generate_vector_image($embedding_array, $word) {
    $embedding_csv = implode(',', $embedding_array);
    $python_venv = '/home/jackson/wordchef/wordchefenv/bin/python3';
    $img_gen_script = '/var/www/wordchef.app/html/scripts/vector_image.py';

    $cmd = escapeshellcmd($python_venv . ' ' . $img_gen_script) . ' '
         . escapeshellarg($embedding_csv) . ' '
         . escapeshellarg($word)
         . ' 2>&1'; // redirect stderr -> stdout

    $output = shell_exec($cmd);
    return is_string($output) ? trim($output) : '';
}

// --- Collect available images ---
$images = [];

if ($word_1 !== '') {
    $img_path_1 = generate_vector_image($embedding_array_1, $word_1);
    if (str_starts_with($img_path_1, '/var/www/wordchef.app/html/')) {
        $images[$word_1] = str_replace('/var/www/wordchef.app/html/', '/', $img_path_1);
    }
}

if ($word_2 !== '') {
    $img_path_2 = generate_vector_image($embedding_array_2, $word_2);
    if (str_starts_with($img_path_2, '/var/www/wordchef.app/html/')) {
        $images[$word_2] = str_replace('/var/www/wordchef.app/html/', '/', $img_path_2);
    }
}

if ($word_1 !== '' && $word_2 !== '') {
    $avg_label = "($word_1 + $word_2) / 2";
    $safe_label = "($word_1 + $word_2)_avg"; // no slash, for file safety
    $img_path_avg = generate_vector_image($average_array, $safe_label);
    if (str_starts_with($img_path_avg, '/var/www/wordchef.app/html/')) {
        $images[$avg_label] = str_replace('/var/www/wordchef.app/html/', '/', $img_path_avg);
    }
}

// --- Display images in a single row ---
if (!empty($images)) {
    echo "<table style='border-collapse:collapse; margin-top:10px; text-align:center;'><tr>";
    foreach ($images as $label => $url) {
        echo "<td style='padding:10px;'>";
        echo "<div style='font-family:monospace; font-size:0.9em; margin-bottom:4px;'>"
             . htmlspecialchars($label) . "</div>";
        echo "<img src='" . htmlspecialchars($url, ENT_QUOTES) . "' "
             . "alt='vector image' style='width:120px; image-rendering:pixelated; border:1px solid #ccc;'>";
        echo "</td>";
    }
    echo "</tr></table>";
}

// Perform nearest-neighbor query safely
$query = "SELECT * FROM wordembeddings ORDER BY embedding <-> $1 LIMIT 5";
$result = pg_query_params($conn, $query, [$average_array_string]);

// Display results in HTML table
if ($result) {

    // Determine display text
    if ($word_1 === '' && $word_2 === '') {
        echo "<h2>Both empty. Similar to zero:</h2><br>";
    } elseif ($word_1 === '') {
        echo "<h2>$word_2 is similar to:</h2><br>";
    } elseif ($word_2 === '') {
        echo "<h2>$word_1 is similar to:</h2><br>";
    } else {
        echo "<h2>avg($word_1, $word_2) is similar to:</h2><br>";
    }

    echo "<table border='1' cellspacing='0' cellpadding='6' style='border-collapse:collapse; text-align:center;'>\n";

    // Collect neighbors
    $neighbors = [];
    while ($row = pg_fetch_assoc($result)) {
        $neighbor_word = htmlspecialchars($row['word']);
        $embedding_str = $row['embedding'];

        $embedding_array = array_map('floatval', preg_split('/[,\s]+/', trim($embedding_str, '{}()')));
        $img_path = generate_vector_image($embedding_array, $neighbor_word);
        $img_url = str_replace('/var/www/wordchef.app/html/', '/', $img_path);

        $neighbors[] = [
            'word' => $neighbor_word,
            'img_url' => ($img_url && file_exists($img_path)) ? $img_url : null
        ];
    }

    // First row: words
    echo "<tr>";
    foreach ($neighbors as $n) {
        echo "<th style='font-weight:bold; padding:8px;'>" . $n['word'] . "</th>";
    }
    echo "</tr>\n";

    // Second row: images
    echo "<tr>";
    foreach ($neighbors as $n) {
        if ($n['img_url']) {
            echo "<td><img src='" . htmlspecialchars($n['img_url'], ENT_QUOTES) . "' alt='vector image' "
                . "style='width:100px; image-rendering:pixelated;'></td>";
        } else {
            echo "<td>(no image)</td>";
        }
    }
    echo "</tr>\n";

    echo "</table>\n";
    pg_free_result($result);
}

// Close connection
pg_close($conn);
?>
</body>
</html>

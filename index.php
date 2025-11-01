<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');

// Load database credentials from external config
$config = include(__DIR__ . '/include/db_config.php');
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
    if ($n !== count($arr2)) {
        throw new Exception("Arrays must be the same length");
    }
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

// Fetch embedding safely with prepared statement
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

// Generate vector image base64 string from embedding via Python script
function generate_vector_image($embedding_array, $word) {
    $embedding_csv = implode(',', $embedding_array);
    $python_venv = '/home/jackson/wordchef/wordchefenv/bin/python3';
    $img_gen_script = '/var/www/wordchef.app/html/scripts/generate_image.py';

    $cmd = escapeshellcmd($python_venv . ' ' . $img_gen_script) . ' '
         . escapeshellarg($embedding_csv) . ' '
         . escapeshellarg($word)
         . ' 2>&1';

    $output = shell_exec($cmd);
    return is_string($output) ? trim($output) : '';
}

// Initialize zero vectors
$embedding_array_1 = array_fill(0, 300, 0);
$embedding_array_2 = array_fill(0, 300, 0);

$word_1 = $_POST['word_1'] ?? '';
$word_2 = $_POST['word_2'] ?? '';

$valid_input_1 = validate_string($word_1, 14);
$valid_input_2 = validate_string($word_2, 14);

if (!$valid_input_1) {
    die("Invalid input for word 1");
}
if (!$valid_input_2) {
    die("Invalid input for word 2");
}

// Fetch embeddings for valid inputs
$embedding_array_1 = $valid_input_1 ? fetch_embedding($conn, $word_1) : $embedding_array_1;
$embedding_array_2 = $valid_input_2 ? fetch_embedding($conn, $word_2) : $embedding_array_2;

// Compute average vector
$sum_array = add_arrays($embedding_array_1, $embedding_array_2);
$average_array = scale_array(0.5, $sum_array);
$average_array_string = '[' . implode(',', $average_array) . ']';

?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>wordchef</title>
<style>
    body { font-family: Arial, sans-serif; }
    table { border-collapse: collapse; margin-top: 10px; text-align: center; }
    td, th { padding: 8px; border: 1px solid #ccc; }
    .vector-label { font-family: monospace; font-size: 0.9em; margin-bottom: 4px; }
    img.vector-image { width: 120px; image-rendering: pixelated; border: 1px solid #ccc; }
    img.neighbor-image { width: 100px; image-rendering: pixelated; }
</style>
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
// Collect base64 images for input words and average vector
$images = [];

if ($word_1 !== '') {
    $base64_1 = generate_vector_image($embedding_array_1, $word_1);
    if ($base64_1 !== '') {
        $images[$word_1] = $base64_1;
    }
}

if ($word_2 !== '') {
    $base64_2 = generate_vector_image($embedding_array_2, $word_2);
    if ($base64_2 !== '') {
        $images[$word_2] = $base64_2;
    }
}

if ($word_1 !== '' && $word_2 !== '') {
    $avg_label = "($word_1 + $word_2) / 2";
    $safe_label = "($word_1 + $word_2)_avg";
    $base64_avg = generate_vector_image($average_array, $safe_label);
    if ($base64_avg !== '') {
        $images[$avg_label] = $base64_avg;
    }
}

// Display the images inline
if (!empty($images)) {
    echo "<table><tr>";
    foreach ($images as $label => $base64_img) {
        echo "<td>";
        echo "<div class='vector-label'>" . htmlspecialchars($label) . "</div>";
        echo "<img class='vector-image' src='data:image/png;base64," . htmlspecialchars($base64_img, ENT_QUOTES) . "' alt='vector image'>";
        echo "</td>";
    }
    echo "</tr></table>";
}

// Query nearest neighbors
$query = "SELECT * FROM wordembeddings ORDER BY embedding <-> $1 LIMIT 5";
$result = pg_query_params($conn, $query, [$average_array_string]);

if ($result) {
    // Determine display heading
    if ($word_1 === '' && $word_2 === '') {
        echo "<h2>Both empty. Similar to zero:</h2><br>";
    } elseif ($word_1 === '') {
        echo "<h2>" . htmlspecialchars($word_2) . " is similar to:</h2><br>";
    } elseif ($word_2 === '') {
        echo "<h2>" . htmlspecialchars($word_1) . " is similar to:</h2><br>";
    } else {
        echo "<h2>avg(" . htmlspecialchars($word_1) . ", " . htmlspecialchars($word_2) . ") is similar to:</h2><br>";
    }

    echo "<table>";

    // Collect neighbors and their images
    $neighbors = [];
    while ($row = pg_fetch_assoc($result)) {
        $neighbor_word = htmlspecialchars($row['word']);
        $embedding_str = $row['embedding'];

        $embedding_array = array_map('floatval', preg_split('/[,\s]+/', trim($embedding_str, '{}()')));
        $base64_img = generate_vector_image($embedding_array, $neighbor_word);

        $neighbors[] = [
            'word' => $neighbor_word,
            'base64_img' => $base64_img !== '' ? $base64_img : null
        ];
    }

    // Display neighbor words
    echo "<tr>";
    foreach ($neighbors as $n) {
        echo "<th>" . $n['word'] . "</th>";
    }
    echo "</tr>";

    // Display neighbor images
    echo "<tr>";
    foreach ($neighbors as $n) {
        if ($n['base64_img']) {
            echo "<td><img class='neighbor-image' src='data:image/png;base64," . htmlspecialchars($n['base64_img'], ENT_QUOTES) . "' alt='vector image'></td>";
        } else {
            echo "<td>(no image)</td>";
        }
    }
    echo "</tr>";

    echo "</table>";

    pg_free_result($result);
}

pg_close($conn);
?>

</body>
</html>

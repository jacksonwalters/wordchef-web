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
// Determine display text
if ($word_1 === '' && $word_2 === '') {
    echo "Both empty. Nearest to zero:<br>";
} elseif ($word_1 === '') {
    echo "$word_2 is similar to:<br>";
} elseif ($word_2 === '') {
    echo "$word_1 is similar to:<br>";
} else {
    echo "($word_1 + $word_2)/2 --> $average_array_string<br>";
}

// Perform nearest-neighbor query safely
$query = "SELECT * FROM wordembeddings ORDER BY embedding <-> $1 LIMIT 5";
$result = pg_query_params($conn, $query, [$average_array_string]);

// Display results in HTML table
if ($result) {
    echo "<table border='1'>\n";
    while ($row = pg_fetch_assoc($result)) {
        echo "\t<tr>\n";
        foreach ($row as $col_value) {
            echo "\t\t<td>$col_value</td>\n";
        }
        echo "\t</tr>\n";
    }
    echo "</table>\n";
    pg_free_result($result);
}

// Close connection
pg_close($conn);
?>
</body>
</html>

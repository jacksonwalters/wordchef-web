<?php
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
    //connect to a database named "jackson" on the host "localhost" with a username and password
    $conn = pg_connect("host=localhost port=5432 dbname=jackson user=jackson password=your-password-here");
?>

<?php
// validate user input from forms
function validate_string($user_input,$max_len){
    if (empty($user_input)) {
        return false;
    }
    // To check that username only contains alphabets, numbers, and underscores 
    elseif (!preg_match("/^[a-zA-Z0-9_]*$/", $user_input)) {
        return false;
    }
    elseif (strlen($user_input) > $max_len) {
        return false;
    }
    else{
        return true;
        }
    }
?>

<form action="/" method="POST">
        Word 1: <input type="text" id="word_1" name="word_1">
        Word 2: <input type="text" id="word_2" name="word_2">
        <input type="submit" value="Submit">
    </form>

<?php
//define vector functions for PHP arrays
function add_arrays($arr1,$arr2){
    $n = count($arr1);
    assert($n == count($arr2), "Error: arrays are different sizes.");
    $sum_array = array_fill(0, $n, 0);
    for ($i = 0; $i < $n; $i++) {
        $sum_array[$i] = $arr1[$i] + $arr2[$i];
    }
    return $sum_array;
}
//define vector functions for PHP arrays
function scale_array($scalar,$arr){
    $n = count($arr);
    $scaled_array = array_fill(0, $n, 0);
    for ($i = 0; $i < $n; $i++) {
        $scaled_array[$i] = $scalar*$arr[$i];
    }
    return $scaled_array;
}
?>

<?php
    if(isset($_POST['word_1'])){
        $word_1 = $_POST['word_1'];
        $valid_input_1 = validate_string($word_1,14);
        if($valid_input_1){
            $word_1_query = "SELECT * FROM wordembeddings WHERE word='$word_1'";
            $result = pg_query($conn,$word_1_query) or die('Query failed: ' . pg_last_error());
            //fetch the associative array of results. keys should be ['word','embedding']
            while ($row = pg_fetch_array($result, null, PGSQL_ASSOC)) {
                $embedding_string_1 = str_replace(array( '[', ']' ), '', $row['embedding']);
                $embedding_array_1 = explode(',', $embedding_string_1);
                echo "<br>";
            }
        }
    }
    if(isset($_POST['word_2'])){
        $word_2 = $_POST['word_2'];
        $valid_input_2 = validate_string($word_2,14);
        if($valid_input_2){
            $word_2_query = "SELECT * FROM wordembeddings WHERE word='$word_2'";
            $result = pg_query($conn,$word_2_query) or die('Query failed: ' . pg_last_error());
            //fetch the associative array of results. keys should be ['word','embedding']
            while ($row = pg_fetch_array($result, null, PGSQL_ASSOC)) {
                $embedding_string_2 = str_replace(array( '[', ']' ), '', $row['embedding']);
                $embedding_array_2 = explode(',', $embedding_string_2);
                echo "<br>";
            }
        }
    }
    if($valid_input_1 && $valid_input_2){
        echo $word_1 . "+" . $word_2;
        $sum_array = add_arrays($embedding_array_1,$embedding_array_2);
        $sum_array_string = '[' . implode(',', $sum_array) . ']';
    }
    
?>

<?php
// Performing SQL query
$query = "SELECT * FROM wordembeddings ORDER BY embedding <-> '$sum_array_string' LIMIT 5;";
$result = pg_query($conn,$query) or die('Query failed: ' . pg_last_error());

// Printing results in HTML
echo "<table>\n";
while ($row = pg_fetch_array($result, null, PGSQL_ASSOC)) {
    echo "\t<tr>\n";
    foreach ($row as $col_value) {
        echo "\t\t<td>$col_value</td>\n";
    }
    echo "\t</tr>\n";
}
echo "</table>\n";

// Free resultset
pg_free_result($result);

// Closing connection
pg_close($conn);
?>

<html>
<head>
</head>
<body>
<h1>Hello!</h1>
</body>
</html>
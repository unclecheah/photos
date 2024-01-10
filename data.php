<?php
    function test () {
        // echo "one two three";
        $age = array("Peter"=>35, "Ben"=>37, "Joe"=>43);
        // header ("Content-Type: application/json; charset=utf-8");
        echo json_encode ($age);
        // return json_encode (['d1' => 'abc', 'd2' => 'def']);
    }


    if (isset ($_GET['test'])) {
        test ();
        // else    echo "nothing";
    } else {
        $data = "{'name': 'John', 'age':30}";
        // $data->name = "John";
        // $data->age = 30;
        // header ("Content-Type: application/json");
        echo json_encode ($data);
        // echo $data;
    }
?>

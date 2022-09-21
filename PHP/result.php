<?php

echo "<div id='myDiv'></div>";

?>
<script src='https://cdn.plot.ly/plotly-2.12.1.min.js'></script>
<script type="text/JavaScript">

var php = <?php
$url = 'http://localhost:5000/feature';

// Create a new cURL resource
$ch = curl_init($url);

$payload = json_encode($_POST['check_list']);

// Attach encoded JSON string to the POST fields
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);

// Set the content type to application/json
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));

// Return response instead of outputting
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

// Execute the POST request
$result = curl_exec($ch);
// Close cURL resource
curl_close($ch);

echo $result
?>

console.log(php)

var data = JSON.parse(JSON.stringify(php))['body']['data']

let all_traces = []

Object.keys(data).forEach(function(key) {
  let cluster = data[key]
  Object.keys(cluster).forEach(function(usr) {
    let x_val = []
    let y_val = []
    let names = []
    let users = cluster[usr]
    for (const [user_nr, value] of Object.entries(users)) {
      x_val.push(value.x)
      y_val.push(value.y)
      names.push([value.username, value.x, value.y])
    }

    let trace_ex = {
      x: x_val,
      y: y_val,
      mode: 'markers',
      type: 'scatter',
      text: names,
      hovertemplate: "Username: <b>%{text[0]}</b><br>"+
      "X: <b>%{text[1]}</b><br>" +
      "Y: <b>%{text[2]}</b><br>"
    };

    all_traces.push(trace_ex)
  })
})

const layout = {
  title: "Flora feature clustering"
}; // It's a stub, put layout config here.

const config = {
  displayModeBar: false, // this is the line that hides the bar.
};

Plotly.newPlot('myDiv', all_traces, layout, config);
    

</script>
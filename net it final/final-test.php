<?php
$dbh = new PDO('mysql:host=db;dbname=velko', 'root', '393ff977',[PDO::ATTR_DEFAULT_FETCH_MODE=> PDO::FETCH_ASSOC
		]);
		$stmt = $dbh->prepare('INSERT INTO `Blog`(`id`, `Pizza_name`,`extras`, `Time`) VALUES (8,$topic,10,11,7)');
		$stmt->execute([]);
?>
<?php
$Pizza_name = $_GET["Pizza_name"];
echo $topic;
$extras = $_GET["extras"];
echo $Title;
$time = $_GET['time'];

?>
sadasd

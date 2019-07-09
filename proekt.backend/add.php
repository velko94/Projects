
<?php
$dbh = new PDO('mysql:host=db;dbname=velko', 'root', '393ff977',[PDO::ATTR_DEFAULT_FETCH_MODE=> PDO::FETCH_ASSOC
		]);
		$stmt = $dbh->prepare('INSERT INTO `Blog`(`id`, `Topic`, `Title`, `Content`, `Time`) VALUES (8,$topic,10,11,7)');
		$stmt->execute([]);
?>
<?php
$topic = $_GET["Topic"];
echo $topic;
$Title = $_GET["Title"];
echo $Title;
$Content = $_GET['Content'];

?>

<!DOCTYPE html>
<html>
<body onload="myFunction()">
<script>
function myFunction() {
if (window.confirm('Post added')) 
{
window.location.href='http://velkorizov.site/proekt_admin.php';
};
}
</script>

</body>
</html>
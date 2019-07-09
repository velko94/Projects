<!DOCTYPE html>
<html>

<head></head>
<?php
		$dbh = new PDO('mysql:host=db;dbname=velko', 'root', '393ff977');
		$stmt = $dbh->prepare('DELETE FROM `Pizza` WHERE `Pizza_name`="Peperoni"');
		$stmt->execute([]);

	?>

<body onload="myFunction()">
	<script>
		function myFunction() {
			if (window.confirm('Post deleted')) {
				window.location.href = 'http://velkorizov.site/final-admin.php';
			};
		}

	</script>

</body>

</html>

<?php
$dbh = new PDO('mysql:host=db;dbname=velko', 'root', '393ff977');
		$stmt = $dbh->prepare("
			INSERT INTO `Pizza`(`Pizza_name`, `Extras`) VALUES (?,?)");
		$stmt->execute(
			[
		$_POST['Pizza_name'],
		$_POST['Extras']
		]);
?>

<!DOCTYPE html>
<html>

<head>
	<link rel="stylesheet" type="text/css" href="final.css">
	<link rel="stylesheet" type="text/css" href="order.css">
	<link href="https://fonts.googleapis.com/css?family=Lato|Rubik&display=swap" rel="stylesheet">

	<title>Final project</title>
</head>

<body>
	<header>
		<a class="text order-head" href="final-menu.html">Menu</a>
		<a class="text menu-head" href="order.php">Order</a>
		<a class="text login-head" href="final-login-form.html">Login</a>
	</header>

	<div class="heading">
		<h1 class="text company-name">Pizzeria Djidji</h1>
	</div>
	<form action="order.php" method="POST" class="orders-menu">
		<select class="text  dropdown" name="Pizza_name">
			<option class="text drop dropdown-item">Please
			</option>
			<option class="text drop dropdown-item">Peperoni
			</option>
			<option class="text drop dropdown-item">Hawaii
			</option>
			<option class="text drop dropdown-item">American-hot</option>
			<option class="text drop dropdown-item">Prosciutto</option>
		</select>
		<div class="condiment">
			<p class="text condiment-txt">Want something extra!</p>
			<textarea name="Extras" rows="4" cols="50" placeholder="Write it here">
</textarea>
		</div>
		<button onclick="sent()" class="text submitbtn" type="submit">Give order</button>
	</form>
	<script type="text/javascript">
		function sent() {
			alert("Order sent!");
		}

	</script>
</body>

</html>

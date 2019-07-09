<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Proekt</title>
	<link rel="stylesheet" href="final-admin.css">
	<link rel="stylesheet" type="text/css" href="final.css">
	<link href="https://fonts.googleapis.com/css?family=Lato|Rubik&display=swap" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css?family=Lato|Open+Sans" rel="stylesheet">
</head>

<?php
		$dbh = new PDO('mysql:host=db;dbname=velko', 'root', '393ff977',[PDO::ATTR_DEFAULT_FETCH_MODE=> PDO::FETCH_ASSOC
		]);
		$stmt = $dbh->prepare('SELECT* FROM Pizza');
		$stmt->execute([]);
		$sql_print = $stmt->fetchAll();

	?>

<body>
	<header>
		<a class="text order-head" href="final-menu.html">Menu</a>
		<a class="text menu-head" href="order.php">Order</a>
		<a class="text login-head" href="final-admin.php">Login</a>
	</header>
	<div class="heading">
		<h1 class="text company-name">Pizzeria Djidji</h1>
	</div>
	<?php foreach($sql_print as $print) { ?>
	<div class="big-box">
		<div class="id">
			<h2 class="text id-content">ID:<?php echo $print ['id']; ?></h2>
		</div>
		<div class="container">
			<h1 class="text Pizza-name">Pizza-Name:
				<?php echo $print['Pizza_name'];?>
			</h1>
			<h1 class="text extra">Condiment:<?php echo $print ['Extras'];?></h1>
		</div>
		<div class="btn delbtn">
			<h1 class="btns-text"><a class=" text btntxt" href="final-delete.php">Delete
				</a>
			</h1>
			<h1 class="btns-text"><a class=" text btntxt rdybtn" id="button" href="#">Done
				</a>
			</h1>
		</div>
	</div>
	<?php } ?>
	<script type="text/javascript">
	</script>
</body>

<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Proekt</title>
	<link rel="stylesheet" href="proekt_public.css">
	<link href="https://fonts.googleapis.com/css?family=Lato|Open+Sans" rel="stylesheet">
</head>

<?php
		$dbh = new PDO('mysql:host=db;dbname=velko', 'root', '393ff977',[PDO::ATTR_DEFAULT_FETCH_MODE=> PDO::FETCH_ASSOC
		]);
		$stmt = $dbh->prepare('SELECT* FROM Blog');
		$stmt->execute([]);
		$sql_print = $stmt->fetchAll();

	?>

<body>
	<h1 class="blog-name">Public</h1>
	<div class="big-box">
		<div class="enterbtn">
	<a class="enterlink" href="/proekt_login.html">Admin side</a></div>

		<?php foreach($sql_print as $print) { ?>
		<div class="container">
			<h1 class="topic">Topic:
				<?php echo $print['Topic'];?>
			</h1>
			<h1 class="title">Title:<?php echo $print ['Title'];?></h1>
			<p>Content:<?php echo $print['Content']; ?></p>
			<div class="id">
				<h2 class="id-content">ID:<?php echo $print ['id']; ?></h2>
			</div>
			<div class="timebox">
				<h2>Time:<?php echo
				$print['Time']; ?></h2>
			</div>
		</div>
		<?php } ?>
	</div>
	
</body>

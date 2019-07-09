<?php
$sql = "DELETE FROM Blog WHERE Topic = 'HTML5'";
$stmt = $pdo->prepare($sql);
$stmt->bindParam(':filmID', $_POST['filmID'], PDO::PARAM_INT);   
$stmt->execute();
?>
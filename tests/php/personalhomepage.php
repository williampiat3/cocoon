#!/usr/bin/php -q
<?php
function addrList() {
	try {
		$db = getConnection();
		echo "<table border='1'>";
		foreach($db->query("SELECT * FROM houses") as $row) {
			echo "<tr>";
			echo "<td>";
			echo $row['address']; 
			echo "</td>";

			echo "<td>";
			echo $row['lng']; 
			echo "</td>";

			echo "<td>";
			echo $row['lat']; 
			echo "</a>";
			echo "</td>";
			echo "</tr>";
		}
		echo "</table>";
	} catch(PDOException $e) {
		echo "DB error:" . $e->getMessage(); 
	}
}

function getConnection() {
	$dbhost="35.189.18.225";
	$dbuser="root";
	$dbpass="C0coonlyfe";
	$dbname="ops";
	$dbh = new PDO("mysql:host=$dbhost;dbname=$dbname", $dbuser, $dbpass);	
	$dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	return $dbh;
}
addrList();


?>
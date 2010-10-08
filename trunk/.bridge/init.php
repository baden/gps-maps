<?php

require_once "header.php";


function eb_dbinit() {
	global $conf;
	mysql_query("DROP TABLE ".$conf['mysql_prefix']."log;");
	mysql_query("DROP TABLE ".$conf['mysql_prefix']."users;");
	$sql .= "CREATE TABLE ".$conf['mysql_prefix']."log (".
		"log_id int NOT NULL AUTO_INCREMENT,".
		"created timestamp DEFAULT NOW(),".
		"imei varchar(20) NOT NULL,".
		"log_data varchar(250) NOT NULL,".
		"PRIMARY KEY (log_id)".
		");";
	$sql .= "CREATE TABLE ".$conf['mysql_prefix']."users (".
		"user_id int NOT NULL AUTO_INCREMENT,".
		"user_name varchar(150) NOT NULL,".
		"PRIMARY KEY (user_id),".
		"UNIQUE KEY user_name (user_name)".
		");";
// Standart users
	$sql .= "INSERT INTO ".$conf['mysql_prefix']."users (user_name) VALUES ('bad-user');";
	$sql .= "INSERT INTO ".$conf['mysql_prefix']."users (user_name) VALUES ('baden');";
	$sql .= "INSERT INTO ".$conf['mysql_prefix']."users (user_name) VALUES ('alex');";
	$sql = explode(";",$sql);
	unset($sql[count($sql)-1]);
	$i=0;
	foreach($sql as $query) {
		$i++;
		if(!mysql_query($query)) {
			return "<h1>Ошибка очистки базы данных</h1>".mysql_error().$query;
			exit();
		}
	}
	if($i==count($sql)) return "<h1>База данных очищена.</h1>";
	return "<h1>Неизвестная ошибка</h1>";
}
echo(eb_dbinit());


require_once "footer.php";

?>

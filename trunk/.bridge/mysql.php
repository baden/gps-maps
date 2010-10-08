<?php
if (!isset($mysql)) {
	$mysql = mysql_connect($conf['mysql_server'], $conf['mysql_user'], $conf['mysql_password']);
	if (!$mysql) {
		die(mysql_error());
	}
	mysql_select_db($conf['mysql_database'], $mysql);
	mysql_query("SET LOCAL time_zone='".$conf['timezone']."';");
}
?>

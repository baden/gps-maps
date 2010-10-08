<?php	require_once "header.php"; ?>

<?php 
	$slogs = 0;
	$nlogs = 50;
	//mysql_connect($mysqlhost,$user,$password);
	//@mysql_select_db($database) or die( "Unable to select database");

	if(isset($_GET['imei']))
		$imei = mysql_real_escape_string(htmlspecialchars(str_replace(" ", "+", $_GET['imei'])));

	//echo("IMEI: " . $imei);

	echo("OK.");

	if(isset($imei)){
//		$name = mysql_real_escape_string(htmlspecialchars(str_replace(" ", "+", $_GET['name'])));
		$where_cond = " WHERE a.imei='$imei'";
	} else {
		$where_cond = "";
	}


	function get_logs_count() {
		global $where_cond;
		global $conf;

		$sql = "SELECT COUNT(log_id)
			FROM ".$conf['mysql_prefix']."log AS a$where_cond";
		$query = mysql_query($sql);
		return mysql_result($query, 0);
	}
	function get_logs() {
		global $imei, $where_cond;
		global $slogs, $nlogs;
		global $conf;

//		mysql_query("SET LOCAL time_zone='+02:00';");
//		mysql_query("SET LOCAL time_zone='Europe/Kiev';");

		$sql = "SELECT log_id,imei,created,log_data
			FROM ".$conf['mysql_prefix']."log AS a$where_cond
			ORDER BY created DESC
			LIMIT $slogs, $nlogs";

		$query = mysql_query($sql);
		if(mysql_num_rows($query)>0) {
			while($row = mysql_fetch_array($query)) $output[]=array($row[0],$row[1],$row[2],$row[3]);
			return $output;
		}
		else return array();
	}
	$logs = get_logs();

	$logs_count = get_logs_count();

?>

<h1>Записи в логе
		<?php if(!isset($imei)){
			echo("для всех систем:");
		} else {
			echo("для системы <i>". $imei ."</i>:");
		}?></h1>

<?php
	if(count($logs)>0) {
		echo("\t<table width=\"100%\">\r\n");
		echo("\t\t<tr><td>ID<br>сообщения</td><td>IMEI<a class=\"filterLink\" href=\"logs.php".$log[1]."\" title=\"Показывать записи всех пользователей\">...</a></td><td>Дата создания</td><td>Содержание лога</td></tr>\r\n");
		foreach($logs as $log){
			echo("\t\t<tr><td>" . $log[0] . "</td><td>". $log[1] . "<a class=\"filterLink\" href=\"logs.php?imei=".$log[1]."\" title=\"Показывать записи только этой системы\">...</a></td><td>" . $log[2] . "</td><td style=\"text-align: left;\">" . $log[3] . "</td></tr>\r\n");
		}
		echo("\t</table>\r\n");
	}
?>

Всег записей в логе: <?php $logs_count;?>

<?php require_once "footer.php"; ?>

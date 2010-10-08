<?php	require_once "header.php"; ?>

<?php 
	//mysql_connect($mysqlhost,$user,$password);
	//@mysql_select_db($database) or die( "Unable to select database");

	$imei = mysql_real_escape_string(htmlspecialchars(str_replace(" ", "+", $_GET['imei'])));

function eb_addlog($n) {
	global $conf;
	global $imei;

	$sql = "INSERT INTO ".$conf['mysql_prefix']."log (imei,log_data) VALUES ('".$imei."','".$n."');";
	$query = mysql_query($sql);
	return mysql_result($query, 0);
}

function dosend() {
	global $imei;

	echo("Открываем..."); 
	$ip = "212.110.139.65";
	$sock = fsockopen ($ip, 8015, $errno, $errstr); 

	if (!$sock) { 
		echo("Ошибка..."); 
		echo("$errno($errstr)");
		//eb_addlog('Bridge-error:'.$errno($errstr));
		eb_addlog("Bridge-error:$errno($errstr)");
		return; 
	} else { 
		echo("Открыли..."); 
		fputs ($sock, $ip."\r\n"); 
		while (!feof($sock)) { 
			echo (str_replace(":",":&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", fgets ($sock,128))."<br>");
		} 
	} 
	fclose ($sock); 
	echo("Закрыли..."); 
}
	
	//echo("IMEI: " . $imei);

	eb_addlog('Bridge-start.');
        dosend();
	eb_addlog('Bridge-end.');

	echo("OK.");
?>

<?php require_once "footer.php"; ?>

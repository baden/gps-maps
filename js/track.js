// Hello
function aaa(){

//	importScripts('io.js');

	var worker = new Worker('trackjs.js');
	worker.onmessage = function(event) {
		//alert(event.data);
		document.getElementById('result').textContent = event.data;
	}; 
	//alert('aaa');
}


function json(){
	var start = new Date().getTime()
	result = document.getElementById('result2');	// = 'json';

	result.textContent = 'Запрос...';

	$.getJSON("/trackcounter?callback=?", function (data) {
		result.textContent = "Обрабатываем...";
		if (data.responseData.counter) {
			result.textContent += "ok:" + data.responseData.counter;
			var time = new Date().getTime() - start;
			result.textContent += " Выполнено за: " + time/1000 + " секунд";

		}
	});

}

function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') { window.onload = func;} 
  else {window.onload = function() { if (oldonload) {oldonload();}func();}}
}
addLoadEvent(function() {
  //Выполняем произвольную JS "команду" :)
  document.getElementById("footer").style.bottom = 0;
}); 

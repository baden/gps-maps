/*
*/

SVG_NS_ = 'http://www.w3.org/2000/svg';

function MySvg(div, left, top) {
	this.div = div;

	var svg = document.createElementNS(SVG_NS_, "svg");
	//svg.id = "svgid";
	//svg.setAttribute('xmlns:svg', 'http://www.w3.org/2000/svg');
	svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
	svg.setAttribute('width', '16');
	svg.setAttribute('height', '16');
	svg.setAttribute('overflow', 'hidden');
//	svg.setAttribute('', 'inline');
	svg.setAttribute('style', 'position: absolute;display:inline;left:'+left.toString()+'px;top:'+top.toString()+'px;z-index:-1;');
//	svg.style.left = left;
//	svg.style.top = top;
//	svg.setAttribute('z-index', '-1');
	//svg.style.overflow = 'hidden';
	svg.setAttribute('version', '1.1');

	this.svg = svg;

	var svg_g = document.createElementNS(SVG_NS_, "g");
	svg.appendChild(svg_g);

	var svg_path = document.createElementNS(SVG_NS_, "path");
	svg_path.setAttribute('style', 'fill:none;stroke:#000000;stroke-width:2px;stroke-linecap:round;stroke-linejoin:round');
	svg_path.setAttribute('d', 'M 8,16 8,1 M 3,7 8,1 13,7');
	svg_g.appendChild(svg_path);

//	var svg_path = document.createElementNS(SVG_NS_, "path");
//	svg_path.setAttribute('style', 'fill:none;stroke:#000000;stroke-width:2px;stroke-linecap:butt;stroke-linejoin:miter');
//	svg_path.setAttribute('d', 'M 3,7 8,1 13,7');
//	svg_g.appendChild(svg_path);

	//var getfnc = function(a){ return function(){ alert(a);} } (1);
	//svg.onmouseover = getfnc;
/*
	div.addEventListener('mouseover', function(e) {
		//svg.setAttribute('width', e.clientX);
		svg_path.setAttribute('style', 'fill:none;stroke:#FF00FF;stroke-width:4px;stroke-linecap:butt;stroke-linejoin:miter');
	}, false);
	div.addEventListener('mouseout', function(e) {
		//svg.setAttribute('width', e.clientX);
		svg_path.setAttribute('style', 'fill:none;stroke:#000000;stroke-width:2px;stroke-linecap:butt;stroke-linejoin:miter');
	}, false);

	div.addEventListener('click', function(e) {
		//svg.setAttribute('width', e.clientX);
		svg_path.setAttribute('style', 'fill:none;stroke:#FF0000;stroke-width:2px;stroke-linecap:butt;stroke-linejoin:miter');
	}, false);
*/
	div.appendChild(svg);
}


MySvg.prototype.highlight = function() {
	alert('bu');
}

MySvg.prototype.remove = function() {
	this.div.removeChild(this.svg);
}

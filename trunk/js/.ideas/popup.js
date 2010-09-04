function showMessage(text, error){
		var clicked = false;
		var self = $("<div/>",{
			css:{
				width : "200px",
				height : "60px",
				background : error ? "#ED6060" : "#60ED60",
				position : "relative",
				zIndex : 10,
				textAlign : "center",
				lineHeight : "60px",
				display : "none",
			},
			text : text,
			click : function(){
				clicked = !clicked;
			},
			mouseover : function(){
				self.stop(true, true).fadeIn("slow");
			},
			mouseout : function(){
			if (!clicked){
				self.stop(true, true).fadeOut("slow").queue(function(){
					self.remove();
				});
 			}
		}})
		.appendTo("body")
		.fadeIn("slow")
		.delay(5000)
		.fadeOut("slow")
		.queue(function(){
			self.remove();
		});
	}

/*
¬се очень просто: при ошибке, например, загрузки данных с сервера вылазит маленькое окошечко
с сообщением о том что произошла ошибка. ѕримерно так как на ’абре. —ообщение держитьс€ 5 секунд
после чего исчезает. ≈сли на него не навести мышку, если навести то снова по€вл€етьс€ даже если
уже наполовину исчезло. ≈сли на него кликнуть то будет держатьс€ пока не кликнеш еще раз. ≈сли
сообщени€ два второе становитьс€ под первое.   сожелению изза дизайна сайта тут положение
высчитываетьс€ вврху экрана и если проскролить чуток то оно чуть сползет, поэтому лучше всего
смотритьс€ в абсолютным позиционированием контента. “акое позиционирование есть если дл€
создани€ сраницы исользовалс€ UI.Layout, так что нужно откорректировать top и left.
*/

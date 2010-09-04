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
��� ����� ������: ��� ������, ��������, �������� ������ � ������� ������� ��������� ��������
� ���������� � ��� ��� ��������� ������. �������� ��� ��� �� �����. ��������� ��������� 5 ������
����� ���� ��������. ���� �� ���� �� ������� �����, ���� ������� �� ����� ����������� ���� ����
��� ���������� �������. ���� �� ���� �������� �� ����� ��������� ���� �� ������� ��� ���. ����
��������� ��� ������ ����������� ��� ������. � ��������� ���� ������� ����� ��� ���������
�������������� ����� ������ � ���� ����������� ����� �� ��� ���� �������, ������� ����� �����
���������� � ���������� ����������������� ��������. ����� ���������������� ���� ���� ���
�������� ������� ������������ UI.Layout, ��� ��� ����� ���������������� top � left.
*/

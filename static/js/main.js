$(document).ready(function(){
	if ($("#id_info")[0].value.length < 500) {
		$("#id_submit")[0].setAttribute("disabled","true")
	};
  $("#id_info").change(function(){
    if ($("#id_info")[0].value.length < 500) {
    	$("#id_submit")[0].setAttribute("disabled","true")
    }else {
    	$("#id_submit")[0].removeAttribute("disabled")
    }
  });
});
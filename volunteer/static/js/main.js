$(document).ready(function(){
  $("#id_info").change(function(){
    if ($("#id_info")[0].value.length < 2500) {
    	$("#id_submit")[0].setAttribute("disabled","true")
    }else {
    	$("#id_submit")[0].disabled = ! $("#id_submit")[0].disabled
    }
  });
});
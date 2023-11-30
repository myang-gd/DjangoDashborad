(function($){   
    $(function(){
        $(document).ready(function() {
            $('#id_vip').change(function(){   
            	            	 
            	 $.ajax({
                     type    : "GET",
                     url     : "/healthcheck/action_change",
                     dataType : "json",
                     data : {"vip_id" : $("#id_vip option:selected").val() },
                     success : function(response, result, responseDataObject) {
                     	
                    	var jsonData = responseDataObject.responseJSON
                    	vip_name = jsonData['vip_name']
                    	if(vip_name == null || vip_name == "") {
                    		return false
                    	}
                    	old_text = $('#id_headers').val()
                    	new_text = ""
                    	if(/Host[\s]*=[^\,=]*$/.test(old_text)) {
                    		old_text += ","
                    		new_text = old_text.replace(/Host[\s]*=[\s\S]*\,/,"Host=" + vip_name + ",")
                    	} else if(/Host[\s]*=[\s\S]*\,/.test(old_text)) {
                    		new_text = old_text.replace(/Host[\s]*=[\s\S]*\,/,"Host=" + vip_name + ",")
                    	} else {
                      		new_text += "Host=" + vip_name
                    	}
                    	if(new_text.match(vip_name + ",$")) {
                    		new_text = new_text.slice(0, -1)
                    	}
                    	$('#id_headers').val(new_text)
                    	
                    }           
                })
            });
      });
    });
})(django.jQuery);


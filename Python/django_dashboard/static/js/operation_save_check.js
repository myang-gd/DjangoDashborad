(function($){   
    $(function(){
        $(document).ready(function() {
            $('[name="_save"]').click(function(event){   
            	event.preventDefault()
            	check_approve = false
            	check_expiration = true 
            	if($("#id_environment option:selected").text() == 'Production' ){
            		if($('#id_jiraTicket').val() == null || $('#id_jiraTicket').val() == '') {
	               		 alert("Jira ticket can't be null for production operation")
	               		 return false
               	 	}
            		check_approve = true
            	} else {
            		if($('#id_jiraTicket').val() == null || $('#id_jiraTicket').val() == '') {
            			 $("#operation_form").submit()
	               		 return false
              	 	}
            	}
            	
            	 $.ajax({
                     type     : "GET",
                     url      : "/healthcheck/operation_save_check",
                     dataType : "json",
                     data : {"tickets" :$('#id_jiraTicket').val(),
                    	      "team_id" : $("#id_team option:selected").val() ,
                    	     "check_approve": check_approve,
                    	     "check_expiration":check_expiration
                    	     },
                     success  : function(response, result, responseDataObject) {
                     	
                    	var jsonData = responseDataObject.responseJSON
                    	not_approve = jsonData['not_approve']
                    	not_valid = jsonData['not_valid']
                    	not_conform_team = jsonData['not_conform_team']
                    	expired = jsonData['expired']
                    	if (typeof not_valid !== 'undefined' && not_valid.length > 0) {
                    		alert("Jira tickets: " + not_valid.toString() + " are not valid")
                   		 	return false
                    	} 
                    	if (typeof not_conform_team !== 'undefined' && not_conform_team.length > 0) {
                    		alert("Jira tickets: " + not_conform_team.toString() + " doesn't belong to team " + $("#id_team option:selected").text())
                   		 	return false
                    	} 
                    	if(check_approve){
                    		if (typeof not_approve !== 'undefined' && not_approve.length > 0) {
                        		alert("Jira tickets: " + not_approve.toString() + " are not approved for production operation")
                       		 	return false
                        	}  	
                    	}
                    	if(check_expiration){
                    		if (typeof expired !== 'undefined' && expired.length > 0) {
                        		alert("Jira tickets: " + expired.toString() + " created on date earlier than a month ago are not allowed")
                       		 	return false
                        	}  	
                    	}
                    	$("#operation_form").submit()
                     },
                     error : function(jqXHR, textStatus, errorThrown) {	        		  
                    	  console.log(textStatus, errorThrown);
		        		  return false
		        	}
                })
            });
      });
    });
})(django.jQuery);


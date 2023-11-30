
		function toggle(source) {
			checkbox_prefix = source.id.replace("_CheckBox","")
			$('div').each(function(){
				if( this.id == checkbox_prefix ) {
		        	$(this).find(':checkbox').each(function(){
						this.checked = source.checked;	
					});				  
		        }
		    });				
		}
		function processAllSelect() {
			$(".row-select").each(function(){				 
				 if(this.id.indexOf("_CheckBox") != -1 &&  this.checked == true){
					 row_id = this.id.replace("_CheckBox","")
					 run_button_id =  row_id + "_run_Button"
					 $('#tb_result button').each(function(){
						 if(this.id == run_button_id && this.disabled == false ) {	
							this.onclick.apply(this)
						 }
					 });
				 }
			 });		
		}
		function processServiceRequest(clicked_id,operation_id, endpoint) {
			
			 var row_id = ""
			 
			 if(clicked_id.indexOf("_run_Button") !=-1 ){
				 row_id = clicked_id.replace("_run_Button","")
			 }else{
				 row_id = clicked_id
			 }
		
			var response_id = row_id + "_response__Link"
			var success_id  = row_id + "_SuccessLabel"
			document.getElementById(clicked_id).disabled = true;
			document.getElementById(clicked_id).innerHTML = "<span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span>Loading" ;
			document.getElementById(success_id).innerText = 'N/A' ;
			document.getElementById(success_id).style.backgroundColor = null;
			
		   

			$.ajax({
		        url : "/healthcheck/result",
		        type : "GET",
		        dataType: "json",
		        data : {"operation_id" : operation_id, "endpoint" : endpoint, "row_id" : row_id},
		        success: 
		        	function(response, result, responseDataObject) 
		        	{
		        		var jsonData = responseDataObject.responseJSON
						success = jsonData['success']
		        	    
		        		
		        		$('#tb_result span').each(function(){
		        	    	if( this.id == success_id ) {
		        	    		 $(this).text(success)
		        	    		 if(success == 'Y'){
		        	    			 $(this).css('background-color','#7FFF00');
		        	    		 } else if(jsonData['success'] == 'N') {
		        	    			 $(this).css('background-color','#DC143C');
		        	    		 }		        	    			 	        	    		 
		        	    	}
							
						});	
		        		
		        		document.getElementById(clicked_id).disabled = false;
		        		document.getElementById(clicked_id).innerHTML = "<span class=\"glyphicon glyphicon-play-circle\"></span>Run"
		        		
		        	},
		        	error: function(jqXHR, textStatus, errorThrown) {
		        		  console.log(textStatus, errorThrown);
		        		  document.getElementById(clicked_id).disabled = false;
		        		  document.getElementById(clicked_id).innerHTML = "<span class=\"glyphicon glyphicon-play-circle\"></span>Run"
		        	}
			});
		}		
		
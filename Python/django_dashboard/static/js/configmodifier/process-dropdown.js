
		
	function processEnvironmentDropDown(option, element, checked) 
		{
			$("button span:contains('Create')").parent().attr("disabled", true);
        	var enableList = ['id_server','id_file','id_config','id_field_value_list']
        	disable(enableList)
			var serverTypeValue = $("#id_server_type :selected").val()
			var data = {}
			
			if (/^\d+$/.test(serverTypeValue)) {
				data['server_type_id'] = serverTypeValue
			}
					
			var optionSelected = $(option).val()
			if (!(/^\d+$/.test(optionSelected))) 
			{
				$("#id_server").multiselect('dataprovider', []);
				$("#id_file").multiselect('dataprovider', [])
				$("#id_config").multiselect('dataprovider', [])
				$("#id_field_value_list").multiselect('dataprovider', [])
    			$("#id_field_value").val('')
				$("#id_server").multiselect('disable');
				$("#id_file").multiselect('disable');
				$("#id_config").multiselect('disable');
				$("#id_field_value_list").multiselect('disable')
			} else
			{  
				 $("button span:contains('Create')").parent().attr("disabled", true);
				data["environment_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{
    		        		
    		        		var server_list_array = [];
    			        	var jsonData = responseDataObject.responseJSON
    			        	server_list_array.push({
			        			'label' : '--Select Server--',
			        			'value' : 'NoneSelected',
			        	    })
    			        	if(jsonData.hasOwnProperty('server_list')){
	    			        	for (var index in jsonData['server_list'])
	    			        	{
	    			        		server_list_array.push({
		    			        			'label' : jsonData['server_list'][index]['server_name'],
		    			        			'value' : jsonData['server_list'][index]['id'],
		    			        	})
	    			        	}
    			        	}
    			        	$("#id_server").multiselect('dataprovider', server_list_array)
    			        	reset(['id_file','id_config','id_field_value','id_field_value_list'])   			        	
    						//refresh()	    						

    						
    			        	if (server_list_array.length <= 1) {
    			        		disable(enableList)
    			        	}else{
    			        		enable(enableList)
    			        	} 
    									    						     		    					    
    		        	}
				});
			}
		}
		function processServerTypeDropDown(option, element, checked) 
		{
			$("button span:contains('Create')").parent().attr("disabled", true);
			var enableList = ['id_server','id_file','id_config','id_field_value_list']
			disable(enableList)
			var environmentValue = $("#id_environment :selected").val()
			var data = {}
			var optionSelected = $(option).val()
			if (/^\d+$/.test(environmentValue)) {
				data['environment_id'] = environmentValue
			}
			if (/^\d+$/.test(optionSelected) || /^\d+$/.test(environmentValue)) 
			{
			
				data["server_type_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{
    		        		
    		        		var server_list_array = [];
    			        	var jsonData = responseDataObject.responseJSON
    			        	server_list_array.push({
			        			'label' : '--Select Server--',
			        			'value' : 'NoneSelected',
			        	    })
    			        	if(jsonData.hasOwnProperty('server_list')){
	    			        	for (var index in jsonData['server_list'])
	    			        	{
	    			        		server_list_array.push({
		    			        			'label' : jsonData['server_list'][index]['server_name'],
		    			        			'value' : jsonData['server_list'][index]['id'],
		    			        	})
	    			        	}
    			        	}
    			        	
    			        	$("#id_server").multiselect('dataprovider', server_list_array)
    			        	enable(enableList)
    			        	reset(['id_file','id_config','id_field_value','id_field_value_list'])      		    					    
    		        	}
				});
			} 
		}	
		function processServerDropDown(option, element, checked) 
		{
			$("button span:contains('Create')").parent().attr("disabled", true);
			var enableList = ['id_file','id_config','id_field_value_list']
			disable(enableList)
			var data = {}

			var optionSelected = $(option).val()
			if (/^\d+$/.test(optionSelected)) 
			{
				data["server_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{
    		        		
    		        		var file_list_array = [];
    			        	var jsonData = responseDataObject.responseJSON
    			        	file_list_array.push({
			        			'label' : '--Select File--',
			        			'value' : 'NoneSelected',
			        	    })
    			        	if(jsonData.hasOwnProperty('file_list')){
	    			        	for (var index in jsonData['file_list'])
	    			        	{
	    			        		file_list_array.push({
		    			        			'label' : jsonData['file_list'][index]['location'],
		    			        			'value' : jsonData['file_list'][index]['id'],
		    			        	})
	    			        	}
    			        	}
    						$("#id_file").multiselect('dataprovider', file_list_array)
    						reset(['id_config','id_field_value','id_field_value_list'])    
    						enable(enableList)
    		        	}
				});
			} else {
				reset(['id_file','id_config','id_field_value','id_field_value_list'])    
			} 
		}
		function processFileDropDown(option, element, checked) 
		{
			$("button span:contains('Create')").parent().attr("disabled", true);
			var data = {}
			var enableList = ['id_config','id_field_value_list']
			disable(enableList)
			var optionSelected = $(option).val()

			if (/^\d+$/.test(optionSelected)) 
			{
				data["file_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{
    		        		
    		        		var config_list_array = [];
    			        	var jsonData = responseDataObject.responseJSON
    			        	config_list_array.push({
			        			'label' : '--Select Config--',
			        			'value' : 'NoneSelected',
			        	    })
    			        	if(jsonData.hasOwnProperty('config_list')){
	    			        	for (var index in jsonData['config_list'])
	    			        	{
	    			        		config_list_array.push({
		    			        			'label' : jsonData['config_list'][index]['display'],
		    			        			'value' : jsonData['config_list'][index]['id'],
		    			        	})
	    			        	}
    			        	}
    						$("#id_config").multiselect('dataprovider', config_list_array)	
    						reset(['id_field_value','id_field_value_list']) 
    						enable(enableList)
    		        	}
				});
			} else {
    			reset(['id_config','id_field_value','id_field_value_list']) 
			}
		}
		function processConfigDropDown(option, element, checked) 
		{
			$("button span:contains('Create')").parent().attr("disabled", true);
			var data = {}
			var enableList = ['id_field_value_list']
			disable(enableList)
			var optionSelected = $(option).val()
			console.log('haha')
			if (/^\d+$/.test(optionSelected)) 
			{
				data["config_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{   		        		
    		        		reset(['id_field_value_list']) 
							$("#id_field_value").val('')
    		        		var value_list_array = [];
    			        	var jsonData = responseDataObject.responseJSON
    			        	value_list_array.push({
			        			'label' : '--Select Value--',
			        			'value' : 'NoneSelected',
			        	    })
			        	    var enable_element = ''
    			        	if(jsonData.hasOwnProperty('value_list')){
	    			        	for (var index in jsonData['value_list'])
	    			        	{
	    			        		value_list_array.push({
		    			        			'label' : jsonData['value_list'][index]['field_value'],
		    			        			'value' : jsonData['value_list'][index]['id'],
		    			        	})
	    			        	}
	    			        	$("#id_field_value_list").multiselect('dataprovider', value_list_array)
	    			        	enable_element = 'list'
    			        	} else {	
    			        		enable_element = 'value'
    			        	} 
    			        	
    			        	var show_value_type = false 
    			        	if(jsonData.hasOwnProperty('show_value_type')) {
    			        		show_value_type = jsonData['show_value_type']
    			        	}
    			        	
    			        	var fvl = 'field_value_list'
    				     	var fv = 'field_value'
    				     	var vt = 'value_type'
    				     	$('#id_value_type').multiselect("refresh");
    			        	
    			    		$('#field-value-type-text').multiselect('deselect', $('#field-value-type-text').val()) 
							$('#field-value-type-text').multiselect('select', 'NoneSelected')
							
    				        if(show_value_type) {   				     
    				       	 	$('label[for=id_form--' + vt +']').removeAttr("style")
    				       	 	$('#id_' + vt).parent().removeAttr("style") 
    				       	 	$("#field-value-type-text-div").removeAttr("style")
    				        } else {
    				       	    $('label[for=id_form--' + vt +']').attr("style", "display: none")
	     					    $('#id_' + vt).parent().attr("style", "display: none") 
	     					    $("#field-value-type-text-div").attr("style", "display: none")
    				        }		
			     			if(enable_element=='value'){
			     				    // $('#id_value_type').multiselect('enable')
			     					 $('label[for=id_form--' + fvl +']').attr("style", "visibility: hidden")
			     					 $('#id_' + fvl).parent().attr("style", "visibility:  hidden") 
			     					 $('label[for=id_form--'+ fv +']').attr("style", "visibility: visible")
			     					 $('#id_' + fv).attr("style", "visibility:  visible")
			     					 $('label[for=id_form--'+ fv +']').parents(".form-group").insertBefore($('label[for=id_form--' + fvl +']').parents(".form-group"))
			     			} else if (enable_element=='list') {
			     				     //$('#id_value_type').multiselect('disable')
			     					 $('label[for=id_form--' + fvl +']').attr("style", "visibility: visible")
			     					 $('#id_' + fvl).parent().attr("style", "visibility:  visible") 
			     					 $('label[for=id_form--'+ fv +']').attr("style", "visibility: hidden")
			     					 $('#id_' + fv).attr("style", "visibility:  hidden")
			     					 $('label[for=id_form--' + fvl +']').parents(".form-grou1p").insertBefore($('label[for=id_form--'+ fv +']').parents(".form-group"))
			     			}
			     			enable(enableList)
			     			$('#id_value_type').multiselect('deselect', $('#id_value_type').val()) 
							$('#id_value_type').multiselect('select', 'NoneSelected')
    			        /*	if(enable=='value'){
	   							 $('label[for=id_form--field_value_list]').attr("style", "visibility: hidden")
	   							 $('#id_field_value_list').parent().attr("style", "visibility:  hidden") 
	   							 $('label[for=id_form--field_value]').attr("style", "visibility: visible")
	   							 $('#id_field_value').attr("style", "visibility:  visible")
	   							 $("label[for=id_form--field_value]").parents(".form-group").insertBefore($("label[for=id_form--field_value_list]").parents(".form-group"))
	   						} else if (enable=='list') {
	   							 $('label[for=id_form--field_value_list]').attr("style", "visibility: visible")
	   							 $('#id_field_value_list').parent().attr("style", "visibility:  visible") 
	   							 $('label[for=id_form--field_value]').attr("style", "visibility: hidden")
	   							 $('#id_field_value').attr("style", "visibility:  hidden")
	   							 $("label[for=id_form--field_value_list]").parents(".form-group").insertBefore($("label[for=id_form--field_value]").parents(".form-group"))
	   						}*/
    			        
    			  
			     			
    		        	}
				});
			} else {
				reset(['id_field_value','id_field_value_list']) 
			}
		}
		
		function processValueDropDown(option, element, checked) 
		{
			$("button span:contains('Create')").parent().attr("disabled", true);
			var data = {}
			
			var optionSelected = $(option).val()         
            
			if (/^\d+$/.test(optionSelected)) 
			{
				data["action_id" ] =  'get_value_type'
				data["value_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{   		        		
    		        	    var jsonData = responseDataObject.responseJSON	
    		        	    if(jsonData.hasOwnProperty('value_type_id')){
    			        		$('#id_value_type').multiselect('deselect', $('#id_value_type').val())
    			        		$('#id_value_type').multiselect('select', jsonData['value_type_id'])
    			        		$('#pre_value_type').val(jsonData['value_type_id'])
    		        	    }  			        	
    				        				     		  			      						
    		        	}
				});
			} else {
				$('#id_value_type').multiselect('deselect', $('#id_value_type').val()) 
				$('#id_value_type').multiselect('select', 'NoneSelected')
			}
			
		}
		
		function processValueTypeDropDown(option, element, checked) 
		{
			
			var optionSelected = $(option).val()
			if($('#id_field_value_list').parent().attr('style') == "visibility:  visible") {
				$('#id_value_type').multiselect('deselect', optionSelected)
				$('#id_value_type').multiselect('select', $('#pre_value_type').val())
			}
			
			
		}
		
		
		function processFeatureDropDown(option, element, checked) 
		{
			var data = {}	
			var optionSelected = $(option).val()
			if (/^\d+$/.test(optionSelected)) 
			{
				data["feature_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{   		        		
	    		        	$("#id_field_value_list_f").multiselect('dataprovider', [])
	    		        	reset(['id_file','id_config','id_field_value','id_field_value_list_f']) 
							$("#id_field_value_f").val('')
    		        		var value_list_array = [];
    			        	var jsonData = responseDataObject.responseJSON
    			        	value_list_array.push({
			        			'label' : '--Select Value--',
			        			'value' : 'NoneSelected',
			        	    })
			        	    var enable = ''
    			        	if(jsonData.hasOwnProperty('value_list')){
	    			        	for (var index in jsonData['value_list'])
	    			        	{
	    			        		value_list_array.push({
		    			        			'label' : jsonData['value_list'][index]['field_value'],
		    			        			'value' : jsonData['value_list'][index]['id'],
		    			        	})
	    			        	}
	    			        	$("#id_field_value_list_f").multiselect('dataprovider', value_list_array)
	    			        	enable = 'list'
    			        	} else {	
    	    		        	enable = 'value'
    			        	}  
    			        	
			        	    var fvl = 'field_value_list_f'
			     			var fv = 'field_value_f'
			     								
			     			if(enable=='value'){
			     					 $('label[for=id_form--' + fvl +']').attr("style", "visibility: hidden")
			     					 $('#id_' + fvl).parent().attr("style", "visibility:  hidden") 
			     					 $('label[for=id_form--'+ fv +']').attr("style", "visibility: visible")
			     					 $('#id_' + fv).attr("style", "visibility:  visible")
			     					 $('label[for=id_form--'+ fv +']').parents(".form-group").insertBefore($('label[for=id_form--' + fvl +']').parents(".form-group"))
			     			} else if (enable=='list') {
			     					 $('label[for=id_form--' + fvl +']').attr("style", "visibility: visible")
			     					 $('#id_' + fvl).parent().attr("style", "visibility:  visible") 
			     					 $('label[for=id_form--'+ fv +']').attr("style", "visibility: hidden")
			     					 $('#id_' + fv).attr("style", "visibility:  hidden")
			     					 $('label[for=id_form--' + fvl +']').parents(".form-group").insertBefore($('label[for=id_form--'+ fv +']').parents(".form-group"))
			     			}
    			     	    // can't use function inside a function
    			        	/*if(enable=='value'){
	   							 $('label[for=id_form--field_value_list_f]').attr("style", "visibility: hidden")
	   							 $('#id_field_value_list_f').parent().attr("style", "visibility:  hidden") 
	   							 $('label[for=id_form--field_value_f]').attr("style", "visibility: visible")
	   							 $('#id_field_value_f').attr("style", "visibility:  visible")
	   							 $("label[for=id_form--field_value_f]").parents(".form-group").insertBefore($("label[for=id_form--field_value_list_f]").parents(".form-group"))
	   						} else if (enable=='list') {
	   							 $('label[for=id_form--field_value_list_f]').attr("style", "visibility: visible")
	   							 $('#id_field_value_list_f').parent().attr("style", "visibility:  visible") 
	   							 $('label[for=id_form--field_value_f]').attr("style", "visibility: hidden")
	   							 $('#id_field_value_f').attr("style", "visibility:  hidden")
	   							 $("label[for=id_form--field_value_list_f]").parents(".form-group").insertBefore($("label[for=id_form--field_value_f]").parents(".form-group"))
	   						}*/
    			        						
    		        	}
				});
			} else {
				$("#id_field_value_list_f").multiselect('dataprovider', [])		
    			$("#id_field_value_f").val('')
			}
		}
		function processTeamDropDown(option, element, checked) 
		{
			$("button span:contains('Create')").parent().attr("disabled", true);
			var data = {}

			var optionSelected = $('#id_team_f :selected').val()
			var environment_id = $('#id_environment_f :selected').val()
			if (/^\d+$/.test(environment_id)) 
				data["environment_id" ] =  environment_id
			if (/^\d+$/.test(optionSelected)) 
			{
				data["team_id" ] =  optionSelected
	 			$.ajax({
    		        url : "/configModifier/ajax",
    		        type : "GET",
    		        dataType: "json",
    		        data : data,
    		        success: 
    		        	function(response, result, responseDataObject) 
    		        	{
    		        		
    		        		var feature_list_array = [];
    			        	var jsonData = responseDataObject.responseJSON
    			        	feature_list_array.push({
			        			'label' : '--Select Config--',
			        			'value' : 'NoneSelected',
			        	    })
    			        	if(jsonData.hasOwnProperty('feature_list')){
	    			        	for (var index in jsonData['feature_list'])
	    			        	{
	    			        		feature_list_array.push({
		    			        			'label' : jsonData['feature_list'][index]['name'],
		    			        			'value' : jsonData['feature_list'][index]['id'],
		    			        	})
	    			        	}
    			        	}
    						$("#id_feature_f").multiselect('dataprovider', feature_list_array)		    					    
    		        	}
				});
			} else {
				$("#id_feature_f").multiselect('dataprovider', [])		
			}
		}
		function refresh(){
			  if($("#id_environment").attr('type') != "hidden")
				  $('#id_environment').multiselect("refresh");
			  if($("#id_server_type").attr('type') != "hidden")
				  $('#id_server_type').multiselect("refresh");
			  if($("#id_server").attr('type') != "hidden")
				  $('#id_server').multiselect("refresh");
			  if($("#id_file").attr('type') != "hidden")
				  $('#id_file').multiselect("refresh");
			  if($("#id_config").attr('type') != "hidden")
				  $('#id_config').multiselect("refresh");
			  if($("#id_field_value_list").attr('type') != "hidden")
				  $('#id_field_value_list').multiselect("refresh");	
		}
		function reset(ids){
			hiddenElementWithParent('value_type')
			
			for(i in ids) {
				/*if ('id_file' == ids[i] && $("#id_file").attr('type') != "hidden"){
					$("#id_file").multiselect('dataprovider', [])
				}
				if ('id_config' == ids[i] && $("#id_config").attr('type') != "hidden"){
					$("#id_config").multiselect('dataprovider', [])
				}
				if ('id_field_value' == ids[i] && $("#id_field_value").attr('type') != "hidden"){
					$("#id_field_value").val('')
				}
				if ('id_field_value_list' == ids[i] && $("#id_field_value_list").attr('type') != "hidden"){
					$("#id_field_value_list").multiselect('dataprovider', [])
				}*/
				if($("#" + ids[i]).prop("tagName") == "SELECT"){
					$("#" + ids[i]).multiselect('dataprovider', [])
				} else if ($("#" + ids[i]).prop("tagName") == "INPUT"){
					$("#" + ids[i]).val('')
				} 
			}
			
		}
		function hiddenElementWithParent(id) {
			 $('label[for=id_form--' + id +']').attr("style", "display: none") 
			 $('#id_' + id).parent().attr("style", "display: none") 
		}
		function showElementWithParent(id) {
			 $('label[for=id_form--' + id +']').removeAttr("style")
			 $('#id_' + id).parent().removeAttr("style") 
		} 
		function enable(ids){
			
			for(i in ids) {
				/*if ('id_server' == ids[i] && $("#id_server").attr('type') != "hidden"){
					$("#id_server").multiselect('enable');
				}
				if ('id_file' == ids[i] && $("#id_file").attr('type') != "hidden"){
					$("#id_file").multiselect('enable');
				}
				if ('id_config' == ids[i] && $("#id_config").attr('type') != "hidden"){
					$("#id_config").multiselect('enable');
				}
				if ('id_field_value_list' == ids[i] && $("#id_field_value_list").attr('type') != "hidden"){
					$("#id_field_value_list").multiselect('enable')
				}*/
				if($("#" + ids[i]).prop("tagName") == "SELECT"){
					$("#" + ids[i]).multiselect('enable')
				} 
			}		
		}
		function disable(ids){
			for(i in ids) {
				/*if ('id_server' == ids[i] && $("#id_server").attr('type') != "hidden"){
					$("#id_server").multiselect('disable');
				}
				if ('id_file' == ids[i] && $("#id_file").attr('type') != "hidden"){
					$("#id_file").multiselect('disable');
				}
				if ('id_config' == ids[i] && $("#id_config").attr('type') != "hidden"){
					$("#id_config").multiselect('disable');
				}
				if ('id_field_value_list' == ids[i] && $("#id_field_value_list").attr('type') != "hidden"){
					$("#id_field_value_list").multiselect('disable')
				}*/
				if($("#" + ids[i]).prop("tagName") == "SELECT"){
					$("#" + ids[i]).multiselect('disable')
				} 
			}
		}
	/*	function exchangeFieldVaueList(enable, is_server){ 
			console.log('hh')
		    var fvl = 'field_value_list'
			var fv = 'field_value'
			if(!is_server) {
				fvl = 'field_value_list_f'
				fv = 'field_value_f'
			}
								
			if(enable=='value'){
					 $('label[for=id_form--' + fvl +']').attr("style", "visibility: hidden")
					 $('#id_' + fvl).parent().attr("style", "visibility:  hidden") 
					 $('label[for=id_form--'+ fv +']').attr("style", "visibility: visible")
					 $('#id_' + fv).attr("style", "visibility:  visible")
					 $('label[for=id_form--'+ fv +']').parents(".form-group").insertBefore($('label[for=id_form--' + fvl +']').parents(".form-group"))
			} else if (enable=='list') {
					 $('label[for=id_form--' + fvl +']').attr("style", "visibility: visible")
					 $('#id_' + fvl).parent().attr("style", "visibility:  visible") 
					 $('label[for=id_form--'+ fv +']').attr("style", "visibility: hidden")
					 $('#id_' + fv).attr("style", "visibility:  hidden")
					 $('label[for=id_form--' + fvl +']').parents(".form-group").insertBefore($('label[for=id_form--'+ fv +']').parents(".form-group"))
			}
			
		
		}*/
		function exchangeFieldVaueList(){ 
			console.log('t')
		}
		/*function ready_dropdown(){
			 $('#id_environment').prepend('<option value="NoneSelected" selected=true>--Select Environment--</option>'); 
			 $('#id_server_type').prepend('<option value="NoneSelected" selected=true>--Select Server Type--</option>'); 
			 $('#id_server').prepend('<option value="NoneSelected" selected=true>--Select Server--</option>'); 
			 $('#id_file').prepend('<option value="NoneSelected" selected=true>--Select File--</option>'); 
			 $('#id_config').prepend('<option value="NoneSelected" selected=true>--Select Config--</option>'); 
			 
			  $('#id_environment').multiselect({
					onChange: processEnvironmentDropDown,	
			    })

			  $('#id_server_type').multiselect({
				 onChange: processServerTypeDropDown,
			  })
				 
			 $('#id_server').multiselect({
					onChange: processServerDropDown,
			 })
			 
			  $('#id_file').multiselect({
					onChange: processFileDropDown,
			 })
			 $("#id_server").multiselect('disable');
			 $("#id_file").multiselect('disable');
			 $("#id_config").multiselect('disable'); 
			 
		}*/

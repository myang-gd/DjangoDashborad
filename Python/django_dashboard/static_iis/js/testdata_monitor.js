/* 
 * Javascript functions for Data Monitor Configuration.
 * 
 * Author:  Steven Wang
 * 
 */

// TestData Monitor View Model
var my_view_model = {};
// My Action List
var my_action_list = [];
//My Customer Type List
var my_custtype_list = [];
//My Monitor List
var my_monitor_list = [];
//My Project List
var my_project_list = [];
// selected_monitor_id
var selected_monitor_id = "";


//initialize
function initial_hide(){
	$('#leftpanel #st_panel').hide();
	$('#CustType_Div').hide();	
	$('#Monitor_Div').hide();
	$('#Chain_Div').hide();
	$('#Mapping_Div').hide();
}


function initialize()
{	
				
	//clear selected_monitor_id
	selected_monitor_id = "";	
    
    //clear all page content
    clear_page_content();
    
    //ui_lock(1);
}


//Load Projects
function get_action_list(event){	
	my_action_list = []
	
	$.ajax({
		type:  "Get",
		url:  "../get_actionlist",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		
		success:  function(data) {            
			my_action_list = data;
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Get actions error');
			ui_unlock();
			}
		});		
}

//convert null to empty
function convert_null_to_empty(data)
{	
	json = data;
	
	$.each(json, function(index, value) {
		for (var key in value) {
			if (value[key] == null || value[key] == typeof null) {
				value[key] = "";
			}
		}
	});
	
	return json;
}

//Show Error Message
function show_error_dialog(message)
{
	$('h5#error_message').html('<p>'+ message +'</p>');
	$('#ErrorDialog').modal('show');
}

//Show Success Message
function show_success_dialog(message)
{
	$('h5#success_message').html('<p>'+ message +'</p>');
	$('#SuccessDialog').modal('show');
}


function get_custtype_list(event){
	my_custtype_list = []
	
	$.ajax({
		type:  "GET",
		url:  "../get_customertypelist",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		success:  function(data) {
			
			my_custtype_list = data;
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load Monitors error');
			ui_unlock();
			}
		});	
}


function load_cust_types(event){
	ui_lock(1);
	
	$.ajax({
		type:  "GET",
		url:  "../load_customertypes",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		success:  function(data) {
			
			append_custtypes_to_html(data);
						
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load Customer Types error');
			ui_unlock();
			}
		});	
}

function append_custtypes_to_html(data){
	
    var content = '';
    
    data = convert_null_to_empty(data);
    
	for(var i = 0; i < data.length; i++){
		if(data[i]["id"] != '' && data[i]["id"] != null){
			
			content += '<tr data-tt-id="'+ data[i]["id"] + '" class="success branch expanded">';
			content = content + '<td id="custtype_id">' + data[i]["id"] + '</td>';
			content = content + '<td id="custtype_name">' + data[i]["name"] + '</td>';
			content = content + '<td id="custtype_desc">'+ data[i]["desc"] + '</td>';
			content = content + '<td id="custtype_real">'+ data[i]["realCustType"] + '</td>';
			content = content + '<td algin="right"><button type="button" name="update_custtype" class="btn btn-primary btn-sm" onclick="update_custtype_tr(event);">Edit</button></td></tr>';
			//content = content + '<td algin="right"><button type="button" name="delete_custtype" class="btn btn-danger btn-sm" onclick="delete_custtype_tr(event, \''+csrf_token+'\');">Delete</button></td></tr>';
		}
	}
	
	$("#custtype_table tbody tr").remove();
	
	$("#custtype_table tbody").append(content);
	
//	$("#custtype_table").DataTable();
}

function get_monitor_list(event){
	my_monitor_list = []
	ui_lock(1);
	
	$.ajax({
		type:  "GET",
		url:  "../get_monitorlist",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		success:  function(data) {
			my_monitor_list = data
			
			append_monitor_list_to_html(data);
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load Monitors error');
			
			ui_unlock();
			}
		});	
}


function get_project_list(event){
	my_project_list = []
	ui_lock(1);
	
	$.ajax({
		type:  "GET",
		url:  "../get_projectlist",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		success:  function(data) {
			
			my_project_list = data
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load Monitors error');
			
			ui_unlock();
			}
		});	
}


function append_monitor_list_to_html(data){
	
	content = '';
	
	$("#listmonitor input").remove();
	
	var monitors = data;
	
	for(var i = 0; i < monitors.length; i++){	  		        
		
		content = content + '<input type="radio" id="' + monitors[i]["id"] + '" onclick="get_monitor_mappings(event, csrf_token);" name= "monitor" value="'+ monitors[i]["name"] +'">'+ monitors[i]["name"] + '</input>&nbsp;&nbsp;';	
		
//		for(var j = 0; j < data.length; j++){							
//			
//			if(data[j]["custType"] == monitors[i]){
//				content = content + '<input type="radio" isConfigurable="' + data[j]["isConfigurable"] + '" onclick="present_selected_custtypes(event);load_queries_by_custtype(event);" name= "cust_type" value="'+ custtypes[i] +'">'+ custtypes[i] + '</input>&nbsp;&nbsp;';								
//			}																	 	
//		}
		
		if(monitors[i] != monitors[monitors.length-1][i]){			
			
			content= content + '</br>';	
		}
		
		$("#listmonitor").html(content); 
	}	  	 
}

function load_monitors(event){
	ui_lock(1);
	
	$.ajax({
		type:  "GET",
		url:  "../load_monitors",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		success:  function(data) {
			
			append_monitors_to_html(data);
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load Monitors error');
			ui_unlock();
			}
		});	
}


function load_chains(event){
	ui_lock(1);
	
	$.ajax({
		type:  "GET",
		url:  "../load_chains",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		success:  function(data) {
			
			append_chains_to_html(data);
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load Chains error');
			ui_unlock();
			}
		});	
}


function append_chains_to_html(data){
	
    var content = '';
    
    data = convert_null_to_empty(data);
    
	for(var i = 0; i < data.length; i++){		   		    		
		
		if(data[i]["id"] != '' && data[i]["id"] != null){
			
		    content += '<tr data-tt-id="'+ data[i]["id"] + '" class="success branch expanded">';
			content = content + '<td id="chain_id">' + data[i]["id"] + '</td>';
			content = content + '<td id="chain_original_custtype" data-original-custtype-id="' + data[i]["originalCustTypeId"] + '">' + data[i]["originalCustType"] + '</td>';
			content = content + '<td id="chain_target_custtype" data-target-custtype-id="' + data[i]["targetCustTypeId"] + '">' + data[i]["targetCustType"] + '</td>';
			content = content + '<td id="chain_action">' + data[i]["action"] + '</td>';
			content = content + '<td id="chain_delay">' + data[i]["delay"] + '</td>';
			content = content + '<td algin="right"><button type="button" class="btn btn-primary btn-sm" onclick="update_chain_tr(event);">Edit</button></td></tr>';
			
		}		
	}	
	
	$("#chain_table tbody tr").remove();
	
	$("#chain_table tbody").append(content);
	
//	$("#chain_table").DataTable();
	
}

function get_monitor_mappings(event, token){
	
	if (selected_monitor_id == "" || selected_monitor_id === null) {
		my_view_model["selected_monitor_id"] = $(event.target).attr('id');
	} else {
		my_view_model["selected_monitor_id"] = selected_monitor_id;
	}
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
	
	$.ajax({
		type: "POST",
		url:  "../load_mappings",
		headers:  {"X-CSRFToken": token},	
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			append_monitor_mappings_to_html(data);
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
}

function append_monitor_mappings_to_html(data){
	
    var content = '';
    
    data = convert_null_to_empty(data);
    
	for(var i = 0; i < data.length; i++){		   		    		
		
		if(data[i]["id"] != '' && data[i]["id"] != null){
			
		    content += '<tr data-tt-id="'+ data[i]["id"] + '" class="success branch expanded">';
			content = content + '<td id="monitor_mapping_id">' + data[i]["id"] + '</td>';
			content = content + '<td id="monitor_mapping_monitor" data-monitor-id="' + data[i]["monitorId"] + '">' + data[i]["monitorName"] + '</td>';
			content = content + '<td id="monitor_mapping_custtype" data-custtype-id="' + data[i]["custConfigId"] + '">' + data[i]["custType"] + '</td>';
			content = content + '<td id="monitor_mapping_threshold">' + data[i]["threshold"] + '</td>';
			content = content + '<td algin="right"><button type="button" class="btn btn-primary btn-sm" onclick="update_mapping_tr(event);">Edit</button></td></tr>';
			
		}		
	}	
	
	$("#mapping_table tbody tr").remove();
	
	$("#mapping_table tbody").append(content);
	
//	$("#monitor_table").DataTable();
	
}


function append_monitors_to_html(data){
	
    var content = '';
    
    data = convert_null_to_empty(data);
    
	for(var i = 0; i < data.length; i++){		   		    		
		
		if(data[i]["id"] != '' && data[i]["id"] != null){
			
		    content += '<tr data-tt-id="'+ data[i]["id"] + '" class="success branch expanded">';
			content = content + '<td id="monitor_id">' + data[i]["id"] + '</td>';
			content = content + '<td id="monitor_name">' + data[i]["name"] + '</td>';
			content = content + '<td id="monitor_desc">' + data[i]["description"] + '</td>';
			content = content + '<td id="monitor_env" data-env-id="' + data[i]["environmentId"] + '">' + data[i]["environmentName"] + '</td>';
			content = content + '<td id="monitor_project" data-project-id="' + data[i]["projectId"] + '">' + data[i]["projectName"] + '</td>';
			content = content + '<td id="monitor_productcode">' + data[i]["productCode"] + '</td>';
			content = content + '<td id="monitor_intervaldays">' + data[i]["intervalDays"] + '</td>';
			content = content + '<td id="monitor_isips">' + data[i]["isIPS"] + '</td>';
			content = content + '<td id="monitor_multiplelayer">' + data[i]["multipleLayer"] + '</td>';
			content = content + '<td id="monitor_emailprefix">' + data[i]["emailPrefix"] + '</td>';
			content = content + '<td id="monitor_useridprefix">' + data[i]["userIDPrefix"] + '</td>';
			content = content + '<td id="monitor_scheduledstarttime"><input type="datetime-local" value="' + data[i]["scheduledStartTime"] + '"></input></td>';
			content = content + '<td id="monitor_appendquery">' + data[i]["appendQueryClause"] + '</td>';
			content = content + '<td algin="right"><button type="button" class="btn btn-primary btn-sm" onclick="update_monitor_tr(event);">Edit</button></td></tr>';
			
		}		
	}	
	
	$("#monitor_table tbody tr").remove();
	
	$("#monitor_table tbody").append(content);
	
//	$("#monitor_table").DataTable();
	
	$('input[type="datetime-local"]').prop('disabled', true);
}


//function append_custtype_list_to_html(data){
//	
//	content = '';
//	
//	$("#listcusttype input").remove();
//	
//	var custtypes = sort_custtypes_alphabetical(data);
//	
//	for(var i = 0; i < custtypes.length; i++){	  		        
//			    
//		for(var j = 0; j < data.length; j++){							
//			
//			if(data[j]["custType"] == custtypes[i]){
//				content = content + '<input type="radio" isConfigurable="' + data[j]["isConfigurable"] + '" onclick="present_selected_custtypes(event);load_queries_by_custtype(event);" name= "cust_type" value="'+ custtypes[i] +'">'+ custtypes[i] + '</input>&nbsp;&nbsp;';								
//			}																	 	
//		}
//		
//		if(custtypes[i] != custtypes[custtypes.length-1][i]){			
//			
//			content= content + '</br>';	
//		}
//		
//		$("#listcusttype").html(content); 
//	}	  	 
//}

//Handle with display of different entities
function handle_display_with_different_entities(event){
	
	selectd_entity = $('#entity').val();
	
	if(selectd_entity == 'CustomerType'){
		load_cust_types(event);
		
		$('#leftpanel #st_panel').hide();
		$('#CustType_Div').show();
		$('#Monitor_Div').hide();
		$('#Chain_Div').hide();
		$('#Mapping_Div').hide();
	}else if(selectd_entity == 'Monitor'){
		get_project_list(event);
		load_monitors(event);
		
		$('#leftpanel #st_panel').hide();
		$('#CustType_Div').hide();
		$('#Monitor_Div').show();
		$('#Chain_Div').hide();
		$('#Mapping_Div').hide();
	}else if(selectd_entity == 'Chain'){		
		get_action_list(event);
		get_custtype_list(event);
		load_chains(event);
		
		$('#leftpanel #st_panel').hide();
		$('#CustType_Div').hide();
		$('#Monitor_Div').hide();
		$('#Chain_Div').show();
		$('#Mapping_Div').hide();
	}else if(selectd_entity == 'Mapping'){		
		get_monitor_list(event);
		get_custtype_list(event);
		
		$('#leftpanel #st_panel').show();
		$('#CustType_Div').hide();
		$('#Monitor_Div').hide();
		$('#Chain_Div').hide();
		$('#Mapping_Div').show();
		$("#mapping_table tbody tr").remove();
	}else{
		$('#leftpanel #st_panel').hide();
		$('#CustType_Div').hide();
		$('#Monitor_Div').hide();
		$('#Chain_Div').hide();
		$('#Mapping_Div').hide();
	}
}

function add_custtype_click(event){
    
	var content = '';
	
	content = '<label for="custtype_id_lbl" style="display: none;">Id:</label><input type="text" class="form-control" id="new_custtype_id" placeholder="CustomerType Id" style="display: none;"></br>';
	content = content + '<label for="custtype_name_lbl">Name:</label><input type="text" class="form-control" id="new_custtype_name" placeholder="CustomerType Name"></br>';	
	content = content + '<label for="custtype_desc_lbl">Description:</label><input type="text" class="form-control" id="new_custtype_desc" placeholder="CustomerType Description"></br>';
	content = content + '<label for="custtype_real_lbl">Real CustomerType:</label><input type="text" class="form-control" id="new_custtype_real" placeholder="Real CustomerType Name"></br>';
    
	$('#CustTypeDialog .modal-body').html(content);
		
    $('#CustTypeDialog').modal('show');
    
    $('#deleteCustType').hide();
    
    $('#updateCustType').hide();
    
    $('#saveCustType').show();
}


function add_chain_click(event){
    
	var content = '';
	
	content = '<label for="chain_id_lbl" style="display: none;">Id:</label><input type="text" class="form-control" id="new_chain_id" placeholder="CustomerType Chain Id" style="display: none;"></br>';
	content = content + '<label for="chain_original_custtype_lbl">Original CustomerType:</label><select type="custtype" class="form-control" id="new_chain_original_custtype" placeholder="Select Original CustomerType"><option value="-1">-- Select Original CustomerType --</option>';
	
	for(var i = 0; i < my_custtype_list.length; i++){
		content = content + '<option value="' + my_custtype_list[i]["id"] + '">' + my_custtype_list[i]["name"] + '</option>'
		
		if(i == my_custtype_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="chain_target_custtype_lbl">Target CustomerType:</label><select type="custtype" class="form-control" id="new_chain_target_custtype" placeholder="Select Target CustomerType"><option value="-1">-- Select Target CustomerType --</option>';
	
	for(var i = 0; i < my_custtype_list.length; i++){
		content = content + '<option value="' + my_custtype_list[i]["id"] + '">' + my_custtype_list[i]["name"] + '</option>'
		
		if(i == my_custtype_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="chain_action_lbl">Action:</label><select type="action" class="form-control" id="new_chain_action" placeholder="Select Action"><option value="-1">-- Select Action --</option>';
	
	for(var i = 0; i < my_action_list.length; i++){
		content = content + '<option value="' + my_action_list[i]["name"] + '">' + my_action_list[i]["name"] + '</option>'
		
		if(i == my_action_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<input type="checkbox" id="new_chain_delay" />&nbsp;<label for="chain_delay_lbl">Time Delay</label></div>';
	
	$('#ChainDialog .modal-body').html(content);
		
    $('#ChainDialog').modal('show');
    
    $('#new_chain_original_custtype').val('-1');
    
    $('#new_chain_target_custtype').val('-1');
    
    $('#new_chain_action').val('-1');
    
    $('#new_chain_delay').attr('checked', false);
    
    $('#deleteChain').hide();
    
    $('#updateChain').hide();
    
    $('#saveChain').show();
}


function add_mapping_click(event){
    
	var content = '';
	
	content = '<label for="mapping_id_lbl" style="display: none;">Id:</label><input type="text" class="form-control" id="new_mapping_id" placeholder="Mapping Id" style="display: none;"></br>';
	content = content + '<label for="mapping_monitor_lbl">Monitor:</label><select type="monitor" class="form-control" id="new_mapping_monitor" placeholder="Select Monitor"><option value="-1">-- Select Monitor --</option>';
	
	for(var i = 0; i < my_monitor_list.length; i++){
		content = content + '<option value="' + my_monitor_list[i]["id"] + '">' + my_monitor_list[i]["name"] + '</option>'
		
		if(i == my_monitor_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="mapping_custtype_lbl">CustomerType:</label><select type="monitor" class="form-control" id="new_mapping_custtype" placeholder="Select CustomerType"><option value="-1">-- Select CustomerType --</option>';
	
	for(var i = 0; i < my_custtype_list.length; i++){
		content = content + '<option value="' + my_custtype_list[i]["id"] + '">' + my_custtype_list[i]["name"] + '</option>'
		
		if(i == my_custtype_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	
	content = content + '<label for="mapping_threshold_lbl">Threshold:</label><input type="text" class="form-control" id="new_mapping_threshold" placeholder="Threshold"></br>';
    
	$('#MappingDialog .modal-body').html(content);
		
    $('#MappingDialog').modal('show');
    
    $('#new_mapping_monitor').val('-1');
    
    $('#new_mapping_custtype').val('-1');
    
    $('#deleteMapping').hide();
    
    $('#updateMapping').hide();
    
    $('#saveMapping').show();
}


function add_chain(event){

	my_view_model["new_chain_action"] = $('#new_chain_action').val();
	my_view_model["new_chain_delay"] = $('#new_chain_delay').is(':checked');
	my_view_model["new_chain_original"] = $('#new_chain_original_custtype').val();
	my_view_model["new_chain_target"] = $('#new_chain_target_custtype').val();
	
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
	
	$.ajax({
		type: "POST",
		url:  "../add_chain",
		headers:  {"X-CSRFToken": event.data.csrf_token},	
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			load_chains(event);
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
	
}


function add_mapping(event){
	
	selected_monitor_id = $('#new_mapping_monitor').val();
	my_view_model["new_mapping_configid"] = $('#new_mapping_custtype').val();
	my_view_model["new_mapping_monitorid"] = $('#new_mapping_monitor').val();
	my_view_model["new_mapping_threshold"] = $('#new_mapping_threshold').val();
	
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
	
	$.ajax({
		type: "POST",
		url:  "../add_mapping",
		headers:  {"X-CSRFToken": event.data.csrf_token},	
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			get_monitor_mappings(event, event.data.csrf_token);
			
			$('#listmonitor input#' + selected_monitor_id).prop("checked", true);
			
			selected_monitor_id = ""
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			selected_monitor_id = ""
			
			ui_unlock();
			}
		});
	
}


function update_mapping_tr(event){
	
	var content = '';
	
	content = '<label for="mapping_id_lbl">Id:</label><input type="text" class="form-control" id="update_mapping_id" placeholder="Monitor CustomerType Mapping Id" value="' + $(event.target).parent().parent().find('#monitor_mapping_id').text() + '"></br>';
	content = content + '<label for="mapping_monitor_lbl">Monitor:</label><select type="monitor" class="form-control" id="update_mapping_monitor" placeholder="Select Monitor"><option value="-1">-- Select Monitor --</option>';
	
	for(var i = 0; i < my_monitor_list.length; i++){
		content = content + '<option value="' + my_monitor_list[i]["id"] + '">' + my_monitor_list[i]["name"] + '</option>'
		
		if(i == my_monitor_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="mapping_custtype_lbl">CustomerType:</label><select type="custtype" class="form-control" id="update_mapping_custtype" placeholder="Select CustomerType"><option value="-1">-- Select CustomerType --</option>';
	
	for(var i = 0; i < my_custtype_list.length; i++){
		content = content + '<option value="' + my_custtype_list[i]["id"] + '">' + my_custtype_list[i]["name"] + '</option>'
		
		if(i == my_custtype_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="mapping_threshold_lbl">Threshold:</label><input type="text" class="form-control" id="update_mapping_threshold" placeholder="Threshold" value="' + $(event.target).parent().parent().find('#monitor_mapping_threshold').text() + '"></br>';
	
	$('#MappingDialog .modal-body').html(content);
    
	$('#MappingDialog').modal('show');
    
    $('#update_mapping_id').prop('disabled', true);
    
    $('#update_mapping_monitor option[value="' + $(event.target).parent().parent().find('#monitor_mapping_monitor').attr("data-monitor-id") + '"]').attr('selected', 'selected');
    
    $('#update_mapping_custtype option[value="' + $(event.target).parent().parent().find('#monitor_mapping_custtype').attr("data-custtype-id") + '"]').attr('selected', 'selected');
    
    $('#deleteMapping').show();
    
    $('#updateMapping').show();
    
    $('#saveMapping').hide();
}


function update_mapping(event){
	
	selected_monitor_id = $('#update_mapping_monitor').val();
	my_view_model["update_mapping_id"] = $('#update_mapping_id').val();
	my_view_model["update_mapping_monitor"] = $('#update_mapping_monitor').val();
	my_view_model["update_mapping_custtype"] = $('#update_mapping_custtype').val();
	my_view_model["update_mapping_threshold"] = $('#update_mapping_threshold').val();
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
		
	$.ajax({
		type: "POST",
		url:  "../update_mapping",
		headers:  {"X-CSRFToken": event.data.csrf_token},		
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			get_monitor_mappings(event, event.data.csrf_token);
			
			$('#listmonitor input#' + selected_monitor_id).prop("checked", true);
			
			selected_monitor_id = ""
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			selected_monitor_id = ""
			
			ui_unlock();
			}
		});
	
}


function delete_mapping(event){
	
	selected_monitor_id = $('#update_mapping_monitor').val();
	my_view_model["delete_mapping_id"] = $('#update_mapping_id').val();
	
	var data = JSON.stringify(my_view_model);
	
	var r = confirm("Confirm Delete Monitor CustomerType Mapping?");
	
	if (r == true) {
		
		ui_lock(1);
		
		$.ajax({
			type: "POST",
			url:  "../delete_mapping",
			headers:  {"X-CSRFToken": event.data.csrf_token},
			data:  {"myjsondata": data},
	
			success:  function(data) {
			
				show_success_dialog(data["message"]);
			
				get_monitor_mappings(event, event.data.csrf_token);
				
				selected_monitor_id = ""
			
				ui_unlock();
				},
			error:function(data) {			
			
				show_error_dialog(data["message"]);
				
				selected_monitor_id = ""
			
				ui_unlock();
				}
			});
	} else {
		selected_monitor_id = ""
	}
}


function add_custtype(event){

	my_view_model["new_custtype_name"] = $('#new_custtype_name').val();
	my_view_model["new_custtype_desc"] = $('#new_custtype_desc').val();
	my_view_model["new_custtype_real"] = $('#new_custtype_real').val();
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
	
	$.ajax({
		type: "POST",
		url:  "../add_customertype",
		headers:  {"X-CSRFToken": event.data.csrf_token},	
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
//			show_success_dialog(data["message"]);
			
			load_cust_types(event);
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
	
}


function update_chain_tr(event){
	
	var content = '';
	
	content = '<label for="chain_id_lbl">Id:</label><input type="text" class="form-control" id="update_chain_id" placeholder="CustomerType Chain Id" value="' + $(event.target).parent().parent().find('#chain_id').text() + '"></br>';
	content = content + '<label for="chain_original_custtype_lbl">Original CustomerType:</label><select type="custtype" class="form-control" id="update_chain_original_custtype" placeholder="Select Original CustomerType"><option value="-1">-- Select Original CustomerType --</option>';
	
	for(var i = 0; i < my_custtype_list.length; i++){
		content = content + '<option value="' + my_custtype_list[i]["id"] + '">' + my_custtype_list[i]["name"] + '</option>'
		
		if(i == my_custtype_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="chain_target_custtype_lbl">Target CustomerType:</label><select type="custtype" class="form-control" id="update_chain_target_custtype" placeholder="Select Target CustomerType"><option value="-1">-- Select Target CustomerType --</option>';
	
	for(var i = 0; i < my_custtype_list.length; i++){
		content = content + '<option value="' + my_custtype_list[i]["id"] + '">' + my_custtype_list[i]["name"] + '</option>'
		
		if(i == my_custtype_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="chain_action_lbl">Action:</label><select type="action" class="form-control" id="update_chain_action" placeholder="Select Action"><option value="-1">-- Select Action --</option>';
	
	for(var i = 0; i < my_action_list.length; i++){
		content = content + '<option value="' + my_action_list[i]["name"] + '">' + my_action_list[i]["name"] + '</option>'
		
		if(i == my_action_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<input type="checkbox" id="update_chain_delay" />&nbsp;<label for="chain_delay_lbl">Time Delay</label></div>';
	
	$('#ChainDialog .modal-body').html(content);
    
	$('#ChainDialog').modal('show');
    
    $('#update_chain_id').prop('disabled', true);
    
    $('#update_chain_original_custtype option[value="' + $(event.target).parent().parent().find('#chain_original_custtype').attr("data-original-custtype-id") + '"]').attr('selected', 'selected');
    
    $('#update_chain_target_custtype option[value="' + $(event.target).parent().parent().find('#chain_target_custtype').attr("data-target-custtype-id") + '"]').attr('selected', 'selected');
    
    $('#update_chain_action option[value="' + $(event.target).parent().parent().find('#chain_action').text() + '"]').attr('selected', 'selected');
    
    $('#update_chain_delay').attr('checked', ($(event.target).parent().parent().find('#chain_delay').text() === 'true'));
    
    $('#deleteChain').show();
    
    $('#updateChain').show();
    
    $('#saveChain').hide();
}


function update_chain(event){
	
	my_view_model["update_chain_id"] = $('#update_chain_id').val();
	my_view_model["update_chain_original_custtype"] = $('#update_chain_original_custtype').val();
	my_view_model["update_chain_target_custtype"] = $('#update_chain_target_custtype').val();
	my_view_model["update_chain_action"] = $('#update_chain_action').val();
	my_view_model["update_chain_delay"] = $('#update_chain_delay').is(':checked');
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
		
	$.ajax({
		type: "POST",
		url:  "../update_chain",
		headers:  {"X-CSRFToken": event.data.csrf_token},		
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			load_chains(event);
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
	
}


function delete_chain(event){
	
	my_view_model["delete_chain_id"] = $('#update_chain_id').val();
	
	var data = JSON.stringify(my_view_model);
	
	var r = confirm("Confirm Delete CustomerType Chain?");
	
	if (r == true) {
		
		ui_lock(1);
		
		$.ajax({
			type: "POST",
			url:  "../delete_chain",
			headers:  {"X-CSRFToken": event.data.csrf_token},
			data:  {"myjsondata": data},
	
			success:  function(data) {
			
				show_success_dialog(data["message"]);
			
				load_chains(event);
			
				ui_unlock();
				},
			error:function(data) {			
			
				show_error_dialog(data["message"]);
			
				ui_unlock();
				}
			});
	}
}


function update_custtype_tr(event){
	
	var content = '';

	content = '<label for="custtype_id_lbl">Id:</label><input type="text" class="form-control" id="update_custtype_id" value="' + $(event.target).parent().parent().find('#custtype_id').text() + '" placeholder="CustomerType Id"></br>';
	content = content + '<label for="custtype_name_lbl">Name:</label><input type="text" class="form-control" id="update_custtype_name" value="' + $(event.target).parent().parent().find('#custtype_name').text() + '" placeholder="CustomerType Name"></br>';	
	content = content + '<label for="custtype_desc_lbl">Description:</label><input type="text" class="form-control" id="update_custtype_desc" value="' + $(event.target).parent().parent().find('#custtype_desc').text() + '" placeholder="CustomerType Description"></br>';
	content = content + '<label for="custtype_real_lbl">Real CustomerType:</label><input type="text" class="form-control" id="update_custtype_real" value="' + $(event.target).parent().parent().find('#custtype_real').text() + '" placeholder="Real CustomerType Name"></br>';
    
	$('#CustTypeDialog .modal-body').html(content);
    
	$('#CustTypeDialog').modal('show');
    
    $('#update_custtype_id').prop('disabled', true);
    
    $('#deleteCustType').show();
    
    $('#updateCustType').show();
    
    $('#saveCustType').hide();
}


function update_custtype(event){
	
	my_view_model["update_custtype_id"] = $('#update_custtype_id').val();
	my_view_model["update_custtype_name"] = $('#update_custtype_name').val();
	my_view_model["update_custtype_desc"] = $('#update_custtype_desc').val();
	my_view_model["update_custtype_real"] = $('#update_custtype_real').val();
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
		
	$.ajax({
		type: "POST",
		url:  "../update_customertype",
		headers:  {"X-CSRFToken": event.data.csrf_token},		
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			load_cust_types(event);
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
	
}


function delete_custtype(event){
	
	my_view_model["delete_custtype_id"] = $('#update_custtype_id').val();
	
	var data = JSON.stringify(my_view_model);
	
	var r = confirm("Confirm Delete CustomerType?");
	
	if (r == true) {
		
		ui_lock(1);
		
		$.ajax({
			type: "POST",
			url:  "../delete_customertype",
			headers:  {"X-CSRFToken": event.data.csrf_token},
			data:  {"myjsondata": data},
	
			success:  function(data) {
			
				show_success_dialog(data["message"]);
			
				load_cust_types(event);
			
				ui_unlock();
				},
			error:function(data) {			
			
				show_error_dialog(data["message"]);
			
				ui_unlock();
				}
			});
	}
}


function add_monitor_click(event){
    
	var content = '';
	
	content = '<label for="monitor_env_lbl">Environment:</label><select type="env" class="form-control" id="new_monitor_env" placeholder="Select Monitor Environment"><option value="-1">-- Select Environment --</option><option value="2">QA3</option><option value="1">QA4</option><option value="3">QA5</option><option value="4">PIE</option></select></br>';
	content = content + '<label for="monitor_project_lbl">Project:</label><select type="project" class="form-control" id="new_monitor_project" placeholder="Select Monitor Environment"><option value="-1">-- Select Project --</option>';
	
	for(var i = 0; i < my_project_list.length; i++){
		content = content + '<option value="' + my_project_list[i]["id"] + '">' + my_project_list[i]["name"] + '</option>'
		
		if(i == my_project_list.length-1){			
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="monitor_name_lbl">Name:</label><input type="text" class="form-control" id="new_monitor_name" placeholder="Monitor Name"></br>';
	content = content + '<label for="monitor_desc_lbl">Description:</label><input type="text" class="form-control" id="new_monitor_desc" placeholder="Monitor Description"></br>';
	
	content = content + '<label for="monitor_interval_lbl">Interval Days:</label><input type="text" class="form-control" id="new_monitor_intervaldays" placeholder="Monitor Interval Days"></br>';
	content = content + '<label for="monitor_schedule_lbl">Scheduled StartTime:</label><input type="datetime-local" class="form-control" id="new_monitor_scheduledstarttime" value=""></br>';
	
	content = content + '<label for="monitor_productcode_lbl">Product Code:</label><input type="text" class="form-control" id="new_monitor_productcode" placeholder="Product Code"></br>';
	content = content + '<label for="monitor_appendquery_lbl">Append Query Clause:</label><input type="text" class="form-control" id="new_monitor_appendquery" placeholder="Append Query Clause"></br>';
	
	content = content + '<label for="monitor_email_lbl">Email Prefix:</label><input type="text" class="form-control" id="new_monitor_email" placeholder="Email Prefix"></br>';	
	content = content + '<label for="monitor_userid_lbl">UserId Prefix:</label><input type="text" class="form-control" id="new_monitor_userid" placeholder="UserId Prefix"></br>';
	
	content = content + '<div class="form-inline"><input type="checkbox" id="new_monitor_multilayer" />&nbsp;<label for="monitor_multilayer_lbl">Multiple Layer</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';	
	content = content + '<input type="checkbox" id="new_monitor_ips" />&nbsp;<label for="monitor_ips_lbl">IPS</label></div>';
    
	$('#MonitorDialog .modal-body').html(content);
		
    $('#MonitorDialog').modal('show');
    
    $('#new_monitor_env').val('-1');
    
    $('#new_monitor_project').val('-1');
    
    $('#new_monitor_ips').attr('checked', false);
    
    $('#new_monitor_multilayer').attr('checked', false);
    
    $('#deleteMonitor').hide();
    
    $('#updateMonitor').hide();
    
    $('#saveMonitor').show();
}


function add_monitor(event){

	my_view_model["new_monitor_env_id"] = $('#new_monitor_env').val();
	my_view_model["new_monitor_project_id"] = $('#new_monitor_project').val();
	
	my_view_model["new_monitor_name"] = $('#new_monitor_name').val();
	my_view_model["new_monitor_product_code"] = $('#new_monitor_productcode').val();
	
	my_view_model["new_monitor_desc"] = $('#new_monitor_desc').val();
	my_view_model["new_monitor_create_by"] = $('.nav.navbar-nav.navbar-right p.navbar-text').text().replace('Logged in as: ', '');
	
	my_view_model["new_monitor_interval_days"] = $('#new_monitor_intervaldays').val();
	my_view_model["new_monitor_scheduled_starttime"] = $('#new_monitor_scheduledstarttime').val();
	
	my_view_model["new_monitor_multiple_layer"] = $('#new_monitor_multilayer').is(':checked');
	my_view_model["new_monitor_ips"] = $('#new_monitor_ips').is(':checked');
	
	my_view_model["new_monitor_email"] = $('#new_monitor_email').val();
	my_view_model["new_monitor_append_query"] = $('#new_monitor_appendquery').val();
	my_view_model["new_monitor_user_id"] = $('#new_monitor_userid').val();
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
	
	$.ajax({
		type: "POST",
		url:  "../add_monitor",
		headers:  {"X-CSRFToken": event.data.csrf_token},	
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			load_monitors(event);
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
	
}


function update_monitor_tr(event){
	
	var content = '';	
	content = '<label for="monitor_id_lbl">Id:</label><input type="text" class="form-control" id="update_monitor_id" value="' + $(event.target).parent().parent().find('#monitor_id').text() + '" placeholder="CustomerType Id"></br>';
	content = content + '<label for="monitor_env_lbl">Environment:</label><select type="env" class="form-control" id="update_monitor_env" placeholder="Select Monitor Environment"><option value="-1">-- Select Environment --</option><option value="2">QA3</option><option value="1">QA4</option><option value="3">QA5</option><option value="4">PIE</option></select></br>';
	content = content + '<label for="monitor_project_lbl">Project:</label><select type="project" class="form-control" id="update_monitor_project" placeholder="Select Monitor Environment"><option value="-1">-- Select Project --</option>';
	
	
	for(var i = 0; i < my_project_list.length; i++){
		content = content + '<option value="' + my_project_list[i]["id"] + '">' + my_project_list[i]["name"] + '</option>'
		
		if(i == my_project_list.length-1){	
			
			content= content + '</select></br>';
		}
	}
	
	content = content + '<label for="monitor_name_lbl">Name:</label><input type="text" class="form-control" id="update_monitor_name" value="' + $(event.target).parent().parent().find('#monitor_name').text() + '" placeholder="Monitor Name"></br>';
	content = content + '<label for="monitor_desc_lbl">Description:</label><input type="text" class="form-control" id="update_monitor_desc" value="' + $(event.target).parent().parent().find('#monitor_desc').text() + '" placeholder="Monitor Description"></br>';
	
	content = content + '<label for="monitor_interval_lbl">Interval Days:</label><input type="text" class="form-control" id="update_monitor_intervaldays" value="' + $(event.target).parent().parent().find('#monitor_intervaldays').text() + '" placeholder="Monitor Interval Days"></br>';
	content = content + '<label for="monitor_schedule_lbl">Scheduled StartTime:</label><input type="datetime-local" class="form-control" id="update_monitor_scheduledstarttime" value="' + $(event.target).parent().parent().find('#monitor_scheduledstarttime input[type="datetime-local"]').val() + '"></br>';
	
	content = content + '<label for="monitor_productcode_lbl">Product Code:</label><input type="text" class="form-control" id="update_monitor_productcode" value="' + $(event.target).parent().parent().find('#monitor_productcode').text() + '" placeholder="Product Code"></br>';
	content = content + '<label for="monitor_appendquery_lbl">Append Query Clause:</label><input type="text" class="form-control" id="update_monitor_appendquery" value="' + $(event.target).parent().parent().find('#monitor_appendquery').text() + '" placeholder="Append Query Clause"></br>';
	
	content = content + '<label for="monitor_email_lbl">Email Prefix:</label><input type="text" class="form-control" id="update_monitor_email" value="' + $(event.target).parent().parent().find('#monitor_emailprefix').text() + '" placeholder="Email Prefix"></br>';	
	content = content + '<label for="monitor_userid_lbl">UserId Prefix:</label><input type="text" class="form-control" id="update_monitor_userid" value="' + $(event.target).parent().parent().find('#monitor_useridprefix').text() + '" placeholder="UserId Prefix"></br>';
	
	content = content + '<div class="form-inline"><input type="checkbox" id="update_monitor_multilayer" />&nbsp;<label for="monitor_multilayer_lbl">Multiple Layer</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';	
	content = content + '<input type="checkbox" id="update_monitor_ips" />&nbsp;<label for="monitor_ips_lbl">IPS</label></div>';
	
	
	$('#MonitorDialog .modal-body').html(content);
		
    $('#MonitorDialog').modal('show');
    
    $('#update_monitor_id').prop('disabled', true);
    
    $('#update_monitor_env option[value="' + $(event.target).parent().parent().find('#monitor_env').attr("data-env-id") + '"]').attr('selected', 'selected');
    
    $('#update_monitor_project option[value="' + $(event.target).parent().parent().find('#monitor_project').attr("data-project-id") + '"]').attr('selected', 'selected');
    
    $('#update_monitor_ips').attr('checked', ($(event.target).parent().parent().find('#monitor_isips').text() === 'true'));
    
    $('#update_monitor_multilayer').attr('checked', ($(event.target).parent().parent().find('#monitor_multiplelayer').text() === 'true'));
    
    $('#deleteMonitor').show();
    
    $('#updateMonitor').show();
    
    $('#saveMonitor').hide();
	
}


function update_monitor(event){
	
	my_view_model["update_monitor_id"] = $('#update_monitor_id').val();
	
//	my_view_model["update_monitor_env_id"] = $('#update_monitor_env option[selected="selected"]').attr("value");
//	my_view_model["update_monitor_project_id"] = $('#update_monitor_project option[selected="selected"]').attr("value");
	
	my_view_model["update_monitor_env_id"] = $('#update_monitor_env').val();
	my_view_model["update_monitor_project_id"] = $('#update_monitor_project').val();
	
	my_view_model["update_monitor_name"] = $('#update_monitor_name').val();
	my_view_model["update_monitor_product_code"] = $('#update_monitor_productcode').val();
	my_view_model["update_monitor_desc"] = $('#update_monitor_desc').val();
	my_view_model["update_monitor_create_by"] = $('.nav.navbar-nav.navbar-right p.navbar-text').text().replace('Logged in as: ', '');
	my_view_model["update_monitor_interval_days"] = $('#update_monitor_intervaldays').val();
	my_view_model["update_monitor_scheduled_starttime"] = $('#update_monitor_scheduledstarttime').val();
	
	my_view_model["update_monitor_multiple_layer"] = $('#update_monitor_multilayer').is(':checked');
	my_view_model["update_monitor_ips"] = $('#update_monitor_ips').is(':checked');
	
	my_view_model["update_custtype_desc"] = $('#update_custtype_desc').val();
	my_view_model["update_monitor_email"] = $('#update_monitor_email').val();
	my_view_model["update_monitor_append_query"] = $('#update_monitor_appendquery').val();
	my_view_model["update_monitor_user_id"] = $('#update_monitor_userid').val();
	
	var data = JSON.stringify(my_view_model);
	
	ui_lock(1);
		
	$.ajax({
		type: "POST",
		url:  "../update_monitor",
		headers:  {"X-CSRFToken": event.data.csrf_token},		
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			load_monitors(event);
			
			ui_unlock();
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
	
}


function delete_monitor(event){
	
	my_view_model["delete_monitor_id"] = $('#update_monitor_id').val();
	
	var data = JSON.stringify(my_view_model);
	
	var r = confirm("Confirm Delete Monitor?");
	
	if (r == true) {
		
		ui_lock(1);
		
		$.ajax({
			type: "POST",
			url:  "../delete_monitor",
			headers:  {"X-CSRFToken": event.data.csrf_token},
			data:  {"myjsondata": data},
	
			success:  function(data) {
			
				show_success_dialog(data["message"]);
			
				load_monitors(event);
			
				ui_unlock();
				},
			error:function(data) {			
			
				show_error_dialog(data["message"]);
			
				ui_unlock();
				}
			});
	}
}




//Clear content for Entity
function clear_page_content(){
	
	//clear selected entity
	$('#entity').val('-1');
	
}

//Main Functions

//Load Projects
function load_projects(event){	
	
	$.ajax({
		type:  "Get",
		url:  "../get-projects",
		headers:  {"X-CSRFToken": event.data.csrf_token},
		
		success:  function(data) {            
			my_projects = data;			
			present_projects(my_projects);
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load projects error');
			ui_unlock();
			}
		});		
}



//Lock UI 
function ui_lock(taskcount)
{
  	$('#please_wait_modal').modal('show');
	loading_task = taskcount;
}

//Unlock UI
function ui_unlock()
{
	loading_task = loading_task -1;
	if(loading_task <= 0) {
		$('#please_wait_modal').modal('hide');
	}
}


function htmlEscape(str) {
	if (str == null) { return str;}
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

// I needed the opposite function today, so adding here too:
function htmlUnescape(str){
	if(str == null) { return str;}
    return str.toString()
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&');
}

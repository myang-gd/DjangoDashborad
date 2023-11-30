/* 
 * Javascript functions for Customer Finder.
 * 
 * Author:  William Chen
 * 
 */
// Customer View Model
var my_view_model = {};

//Current Environment
var my_environment ='';

//Current project
var my_project_name =-1;

//productkey or product type
var my_product = "";

//product map
var my_productmap = [];

//customer type list
var my_custtype_list = [];

//email
var email = "";

//current UI status
var my_status = "none";

//Loading task count 
var loading_task = 0;

//sorted customer type
var sorted_custType = [];

//Selected Customer Type count
var custtype_selected_count = 0 ;

//initialize
function initialize(event)
{			
	
	clear_page();
	
	my_view_model = {'database':'', 'env':'','project':-1, 'products':'', 'email':[], 'custtypes':[], 'selected_custtypes':'', 'extendedquery':''};
		
	$('#selected_cust_type').prop('disabled', true);		
	
	$('#statement').attr('placeholder','Given I get customerkey use productkey as \"#{productkey}\" and customertype as \"#{@customertype}\" and appendextendqueryclause \"\" and email like \"#{email}\" and store it to variable \"customerKey\"');
		
    ui_lock(1);        
		
	load_projects(event);	
	
}

//Create a new page (my_mapped_project: TestRail project id map to django Project id)
function is_valid_search_condition(event)
{		
		
	//Get Current value
	my_environment = $('#environment').val();
	my_project_name =  $('#project').val();
	my_product = $('#product').val();
	
	var selected_custtypes = $('#selected_cust_type').val();		
	var selected_option = $('#where_condition').val();	
	var extend_query = $('#extended_query').val();
	
	if(my_environment == -1){
		
		show_error_dialog('Please select environment');
		
		return false;
	}
	
	if(my_project_name == -1){
		
		show_error_dialog('Please select a project');
		
		return false; 
	}				
	
	if(my_product == ""){
		show_error_dialog('Please input product');
		
		return false;
	}							
	
	if(selected_custtypes == ""){
		
	    show_error_dialog('Please choose customer type!');
	    
	    return false;
	}			
	
	if(extend_query == ''&& selected_option != -1){
		
		show_error_dialog('Append Extended Query can not be null if Sql Command Selected.');
		
		return false;
			
	}
	
	if(extend_query != '' && selected_option == -1){
			
	    show_error_dialog('Please select Sql Command.');
	    
	    return false;
	    }
					
}


//New current conditions
function new_current_conditions(event){
	
	my_view_model = {'database':'', 'env':'','project':-1,'products':'','email':'','selected_custtypes' : '', 'extendedquery':'', "isCheckPassword": false };
	
	my_view_model['custtypes'] = [];
	my_view_model["database"] = $('#database').val();
	my_view_model["env"] = $('#environment').val();
	my_view_model["project"] = $('#project').val();
	my_view_model["products"] = $('#product').val();
	
	is_ips_checked(event);
	
	my_view_model["selected_custtypes"] = $('#selected_cust_type').val();	
	my_view_model["email"] = $('#email').val();
	
	if(my_view_model["selected_custtypes"].toString().indexOf("|") == -1){
		my_view_model['custtypes'] = [my_view_model["selected_custtypes"]];
	}else{
		my_view_model['custtypes'] = my_view_model["selected_custtypes"].split("|");
	}
	
	selected_option = $('#where_condition').val();
	
	extend_query = $('#extended_query').val(); 
	
	if(extend_query == '' && selected_option == -1){
		my_view_model["extendedquery"] = '';
	}else if(extend_query != '' && selected_option != -1){
		my_view_model["extendedquery"] = selected_option + " " +  extend_query;
	}			
	
	my_view_model["isCheckPassword"] = $('#isCheckPassword').prop('checked');
}


//Append product map to datalist
function append_productmap_to_datalist(data){
	
	var product_list = [];
	var ips_product_list = [];
	var content = '';
	var ips_content = '';			
	
	for(var i=0; i < data.length; i++){
		producttype = data[i]["productType"];
		productkey = data[i]["productKey"];
		ipsproductkey = data[i]["ipsProductKey"];				
		product = data[i]["productType"];		
		ipsproduct = data[i]["productType"];		
		
		product_list.push(product);
		
		ips_product_list.push(ipsproduct);
		
		content += '<option value="' + product +  '" title="ProductKey:' + productkey + ' IPSProductKey:'+ ipsproductkey + '">' + product + '</option>';
		//content += '<option value="' + product +  '" onMouseOver="present_productmap_tooltip(this);">' + product + '</option>'		
		
		ips_content += "<option value='" + ipsproduct +  "'>" + ipsproduct + "</option>"
	}				
	
	$('#product_list option').remove();	    
	
	$('#product_list').append(content);
	
	$('#product_list option').tooltip();
		
}

function present_productmap_tooltip(event){
			
	var current_target =  $(event.currentTarget);
	
	//initialize tooltip content
	current_target.attr("title","");
	
	var current_producttype = current_target.val();
	
	for(var i=0; i < my_productmap.length; i++){
		if(my_productmap[i]["productType"] == current_producttype){
			
			//content = '<option value="' + my_product[i]["productType"] +  '" data-toggle="tooltip" data-placement="right" title="ProductKey:' + my_product[i]["productKey"] + ' IPSProductKey:'+ my_product[i]["ipsProductKey"] + '">' + my_product[i]["productType"] + '</option>';
			//current_target.html(content);
			
			current_target.attr("data-toggle","tooltip");
			current_target.attr("data-placement","right");
			current_target.attr("title","ProductKey:"+ my_productmap[i]["productKey"] + " IPSProductKey:" + my_productmap[i]["ipsProductKey"]);						
		}
	}
	
	current_target.tooltip();
}



//reload page
function reload_page(event){
	
	//clear_all_checked_custtypes
	//clear_all_checked_custtypes(event);
	
	//$("#listcusttype").children().remove();
	
	//reload customer type list
	//load_custtype_list(event);
	//append_custtype_list_to_html(my_custtype_list);
		
}


//IPS checked or not 
function is_ips_checked(event){
	
	my_view_model["isips"] = false;
	
	var isIPS = false;
		
	//Set isIPS as True if checked
	if($('#ips').prop('checked') == true){
		isIPS = true;
	}else{
		isIPS = false;
	}
				
	my_view_model["isips"] = isIPS;
}

//Present Environment to html
/*function present_environment(data){
	
	my_environment = $("#environment").val();
		
	content = '<option value="-1" selected="selected">  </option>';
	
	for(var i=0;i<data.length;i++){
		if(data[i] == my_environment)
			content= content + '<option value="'+ data[i] +'" selected="selected">'+ data[i] +'</option>';
		else
			content= content + '<option value="'+ data[i] +'">'+ data[i] +'</option>';				
	}

	$("#environment").html(content);	
}*/

//present projects to page
function present_projects(data){		
	
	$('#project option').remove();
	
	content = '<option value="-1" selected="selected">  </option>';
	
	for(var i=0; i<data.length; i++){
		if(data[i]['projectName'] == my_project_name){						
			
			content= content + '<option value="'+ data[i]['projectName'] +'" selected="selected">'+ data[i]['projectName'] +'</option>';			
			}
		    
		else{content= content + '<option value="'+ data[i]['projectName'] +'">'+ data[i]['projectName'] +'</option>';
		}			
	}

	$("#project").html(content);		
}

//present email prefix
function present_email_prefix(data){
	
	content = '';
	
	for(var i=0;i<data.length;i++){			
		
		if(data[i]["IsEnable"]=="True"){
			
			content += data[i]["Name"] + "|";										    
			 				
		}else{
			content += '';
		}
		
	} 		
	
	if(content.slice(-1) == "|"){
		
		content = content.substring(0, content.length-1);
	}	
	
	$("#email").val(content);
				
}



//Sort Customer Types by alphabet
function sort_custtypes_alphabetical(data){		
	
	sorted_custType = [];
	
	for(var i=0;i<data.length;i++){
		if(data[i]["isVisible"] == "True" && data[i]["isEnable"] == "True"){
			sorted_custType.push(data[i]["custType"]);
		}		
	}			
	
	sorted_custType.sort();
	
	return sorted_custType;
}

//Show Customer Types on page
function append_custtype_list_to_html(data){
					
	content = '';
	
	var custtypes = [];
	
	var custtypes = sort_custtypes_alphabetical(data);		
	
	var my_custtype_list = custtypes;
	
	content = '<button type="button" class="btn btn-secondary btn-sm btn-info pull-right" onclick="clear_all_checked_custtypes(this)" id="clear_all_checked_custtypes">Clear All</button></br>'
	
	for(var i=0;i<custtypes.length;i++){			  		        
			    
		for(var j=0; j < data.length; j++){							
			
			if(data[j]["custType"] == custtypes[i] && data[j]["isVisible"] == "True" && data[j]["isEnable"] == "True"){								
				
				//content = content + '<input type="checkbox" isConfigurable="' + data[j]["isConfigurable"] + '" onclick="present_selected_custtypes(this)" id="'+ custtypes[i] +'"><label for="custtype_label">'+ custtypes[i] + '</label> ';
				content = content + '<input type="checkbox" data-toggle="tooltip" data-placement="right" title="' + data[j]["custTypeDescription"] + '" isConfigurable="' + data[j]["isConfigurable"] + '" onclick="present_selected_custtypes(this)" id="'+ custtypes[i] +'">'+ custtypes[i] + '</input>&nbsp;&nbsp;';
				
				//content = content + '<input type="radio" isConfigurable="' + data[j]["isConfigurable"] + '" onclick="present_selected_custtypes(this)" name= "cust_type" value="'+ custtypes[i] +'">'+ custtypes[i] + '</input>&nbsp;&nbsp;';
				
				if(data[j]["Params"] != '' && data[j]["Params"] != null){
					if(data[j]["custType"] == 'AcctAge'){
						content = content + '<input type="text" id="p_' + data[j]["Params"] +'" value=">=100" placeholder="' + data[j]["Params"] + '" data-toggle="tooltip" title="Param CardActivationDate Format like: >=100 "></input>';						
					}else if(data[j]["custType"] == 'AcctBalance'){
						content = content + '<input type="text" id="p_' + data[j]["Params"] +'" value=">10" placeholder="' + data[j]["Params"] + '" data-toggle="tooltip" title="Param Account Balance Format like: >10"></input>';						
					}else if(data[j]["custType"] == 'CreditRatingKey'){
						content = content + '<input type="text" id="p_' + data[j]["Params"] +'" value="=C5,R1" placeholder="' + data[j]["Params"] + '" data-toggle="tooltip" title="Param CreditRatingKey Format like: !=C5 "></input>';					
					}else if(data[j]["custType"] == 'AccountHasTransactions'){
						content = content + '<input type="text" id="p_' + data[j]["Params"] +'" value="<=20" placeholder="' + data[j]["Params"] + '" data-toggle="tooltip" title="Param Time Frame Format like: <=20 "></input>';					
					}else if(data[j]["custType"] == 'AcctStatus'){
						content = content + '<input type="text" id="p_' + data[j]["Params"] +'" value="=2" placeholder="' + data[j]["Params"] + '" data-toggle="tooltip" title="Param AccountStatusKey Format like: =3, !=2 "></input>';					
					}else{
						content = content + '<input type="text" id="p_' + data[j]["Params"] +'" placeholder="' + data[j]["Params"] + '" data-toggle="tooltip" title="Pls input Params here!"></input>';
					}
					
					
				}											
			}																	 	
		}				
		
		if(i != custtypes.length -1){					
			
			content= content + '</br>';	
		}				
			
		$("#listcusttype").html(content); 
	}	  	 
}

function disable_custtype_list_item(element){
	var isconf = null;
	if($(element).prop('checked')==true){
		isconf = $(element).attr('isConfigurable');
	}
	
	if(isconf != null){
		$('input[type=checkbox][isConfigurable=' + !isconf + ']').prop('disabled', true);
	}			
}

//present selected customer types to page
function present_selected_custtypes(element){		
		
	var custtype_selected_count = 0 ;
	var current_custtype = element.id;
	my_view_model["selected_custtypes"] = "";
	var data = [];
	var data = my_view_model["custtypes"];
	var index = data.indexOf(current_custtype);	 
	
    if(current_custtype == 'UserIdCreated'){
    	$('#isCheckPassword').prop("checked", false);
    }
	
	if($(element).prop('checked')==true){	
		
	    var param_input = $(element).next().val();
		
	    if(current_custtype == 'UserIdCreated'){
	    	$('#isCheckPassword').prop("checked", true);
	    }
	    
		if(current_custtype == 'AcctBalance' || current_custtype == 'AcctAge' || current_custtype== 'CreditRatingKey'){
            if(param_input == '' || param_input == null){ 
				$(element).prop("checked", false);
				
				return show_error_dialog('Please input parameters at first.');
            }
		}
			
		if(param_input != "" && param_input != null){
			var params = $(element).next().attr('placeholder');
			var params_value = param_input;
			data.push(element.id + "{" + params +  ":" + params_value + "}");
		}
		else{
			data.push(element.id);	
			custtype_selected_count++;
		}	
	}
	else{
		
		data.splice(index, 1);
		custtype_selected_count--;
	} 
		
	    my_view_model["custtypes"] = data;
	
	for(var i = 0 ; i< data.length; i++){		
		
		my_view_model["selected_custtypes"] += data[i] + '|';
		}

	my_view_model["selected_custtypes"] = my_view_model["selected_custtypes"].substring(0, my_view_model["selected_custtypes"].length-1);
	
	//check_if_custtype_conflict(current_custtype, my_view_model["selected_custtypes"]);
	
	$('#selected_cust_type').val(my_view_model["selected_custtypes"]);			
				
}

//Check If select where condition for extended Query without append query content
function check_if_no_extend_query_with_where_condition_selected(){
	
	my_view_model["extendedquery"] = "";
		
	var selected_option = $('#where_condition').val();
	
	var entend_query = $('#extended_query').val();
	
	if(entend_query == ''&& selected_option != -1){
		
		$('#where_condition').val('-1');
		
		show_error_dialog('Append Extended Query can not be null if Sql Command Selected.');
		
		return;
			
	}else if(entend_query != '' && selected_option == -1){
		
		$('#extended_query').val('');
			
	    show_error_dialog('Please select Sql Command.');
	    
	    return;
			
	}else if(entend_query != '' && selected_option != -1){
		
		my_view_model["extendedquery"] = $('#where_condition').val() + " " +  $('#extended_query').val();				
		
	}	
	
}

//check custtype conflict
/*function check_if_custtype_conflict(current_custtype, selected_custtype){
	
	var substring_custtype = "";
	
	var slice_length = - (current_custtype.length + 1);
	
	if(current_custtype.startsWith("Not") == true ){
		
		substring_custtype = current_custtype.substring(3);
			
		if(selected_custtype.includes(substring_custtype) == true){		
			
			document.getElementById(current_custtype).checked = false;									
			
			my_view_model["selected_custtypes"] = my_view_model["selected_custtypes"].slice(slice_length);
			
			return show_error_dialog('Customer Type Conflict.');
			
		}
	} 
}*/


//Present Statement with parameters
function present_statement_with_parameters(event){				
	
	var statement= "";
	
	var database = $('#database').val();
	
	var product = $('#product').val();
	
	var email = $('#email').val();
	
	var customertype = $('#selected_cust_type').val(); 
	
	var extend_query = $('#where_condition').val() + " " +  $('#extended_query').val();
	
	if(extend_query == "-1 "){
		extend_query = "";
	}
	
	if(database == "-1") {
		show_error_dialog('Please choose database.');
	    return;
	}
	
	if(product == ""){
	    show_error_dialog('Please choose product.');
	    return;
	}	
	
	if(customertype == ""){
	    show_error_dialog('Please choose customer type.');
	    return;
	}
	
	if(database == "1") {
		statement = 'Given I get customerkey use productkey as "' + product +'" and customertype as "' + customertype +'" and appendextendqueryclause "' + extend_query + '" and email like "' + email + '" and store it to variable "customerKey"'
	}
	
	if(database == "3"){
		statement = 'Given I get accountidentifier use productcode as "' + product +'" and customertype as "' + customertype +'" and appendextendqueryclause "' + extend_query + '" and email like "' + email + '" in database AWSGBOS and store it to variable "accountIdentifier"'
	}
	
	
	
	$('#statement_div').show();
	
	$('#statement').val(statement);		
	
}

//Present search result to page
function search_result_present(data){   	
     	
	$('#customerkey_result').val(data["customerKey"]);
	$('#userid_result').val(data["userId"]);
	$('#accountidentifier_result').val(data["accountIdentifier"]);
	$('#consumerprofilekey_result').val(data["consumerProfileKey"]);
	$('#email_result').val(data["email"]);
	
	if(data["sqlQuery"] != ""){
		
		$('#sql_body').remove();		

		$('#sql_panel').append("<div class='panel-body' id='sql_body'><pre>" + data["sqlQuery"] + "</pre></div>");     
       
	}			
}

//edit selected customer type
function edit_selected_custtypes(event){
	
	$('#selected_cust_type').prop('disabled', false);	
}

//Present Query 
function present_sql(data){
	
	$('#sql_body').remove();
		
	$('#sql_panel').append("<div class='panel-body' id='sql_body'><pre>" + data['sqlQuery'] + "</pre></div>");
}


//function list

//Load Environment
function load_environment(event){
	
	$.ajax({
		type:  "Get",
		url:  "../get-environment",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {
						
			present_environment(data);
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load environment error');
			ui_unlock();
			}
		});	
}

//Load Projects
function load_projects(event){				
	
	$.ajax({
		type:  "Get",
		url:  "../get-projects",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {		
			
			my_projects = data;
			present_projects(my_projects);
			ui_unlock();
			},
		
		error:  function(data) {			
			ui_unlock();
			}
		});		
}

//Load Product Map
function load_productmap(event){
	
	my_project_name = $("#project").val();
	my_database = $("#database").val();
	
	$.ajax({
		type:  "Get",
		url:  "../get-productmap/?project=" + my_project_name + "&data_Base_Id=" + my_database,
		headers:  {"X-CSRFToken": event.data.csrf_token },				
		
		success:  function(data) {			
			
			my_productmap = data;
			
			append_productmap_to_datalist(data);						
			
			ui_unlock();
			},
	    			
		error:  function(data) {		
			ui_unlock();
			}
		});		
}

//Load Email Prefix
function load_email_prefix(event){
	
	my_project_name = $("#project").val();
	my_database = $("#database").val();
	
	$.ajax({
		type:  "Get",
		url:  "../get-emailprefix/?project=" + my_project_name + "&data_Base_Id=" + my_database,
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {
			
			present_email_prefix(data);
			
			email_prefix_list = data;			
			ui_unlock();
			},
		
		error:  function(data) {		
			
			$("#email").val('');
			
			ui_unlock();
			}
		});	
}

//Load Customer Type List
function load_custtype_list(event){				
	
	my_project_name = $("#project").val();
	my_database = $("#database").val();
	
	$.ajax({
		type:  "Get",
		url:  "../get-custtypelist/?project=" + my_project_name + "&data_Base_Id=" + my_database,
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {									
			
			append_custtype_list_to_html(data);
			
			my_custtype_list = data;
			
			ui_unlock();
			},
		
		error:  function(data) {			
			ui_unlock();
			}
		});	
	
}

//Get Generated Query
function get_generated_sql(event){
	
	isValidCondition = is_valid_search_condition(event);
	
	if(isValidCondition != false){
		
		new_current_conditions(event);
	
		var data = JSON.stringify(my_view_model);	
		
		ui_lock(1);
		
		//Clear Search Result
		clear_search_result();
			
		$.ajax({
			type: "Post",
			url:  "../get-generatedsql/",
			headers:  {"X-CSRFToken": event.data.csrf_token },
			data:  {"myjsondata": data},
		
			success:  function(data) {	
				
				if(data["responseCode"] == "Success"){
							
				   present_sql(data);			
				    
				}else{
					show_error_dialog(data["errorReason"]);
				}
						 									
				ui_unlock();			
				},
			error:function(data) {			
				
				show_error_dialog("No SQL Query returned with current conditions.");			
				
				ui_unlock();
				}
			});
	}	
}

//Main Function
function get_customer(event){
			
	
    isValidCondition = is_valid_search_condition(event);
	
	if(isValidCondition != false){
		
		new_current_conditions(event);
		
	    var data = JSON.stringify(my_view_model);
		
		//Clear Search Result
		clear_search_result();
			
		ui_lock(1);
			
		$.ajax({
			type: "Post",
			url:  "../get-customer/",
			headers:  {"X-CSRFToken": event.data.csrf_token },
			data:  {"myjsondata": data},
		
			success:  function(data) {							
										
				if(data["responseCode"] == "Success"){
									
					search_result_present(data);					
					
				}else{
					show_error_dialog(data["errorReason"]);
					}									
				
				ui_unlock();			
				},
			error:function(data) {							
				
				show_error_dialog("No CustomerKey returned with current conditions.");
						
				ui_unlock();
				}
			});
		}			
}

//clear all checked custtypes from Customer Type List in the left pannel
function clear_all_checked_custtypes(event){
	
	$('#listcusttype input').prop("checked", false);
	
	$('#selected_cust_type').val("");
	
	my_view_model["selected_custtypes"] = "";
	
	my_view_model["custtypes"] = []; 
	
	$('#statement').val("");
	
	$('#statement_div').hide();
		
	clear_search_result();
}

//Clear Page Content
function clear_page(){
	//clear database 
	//$('#database').val("-1");
	
	//clear environment 
	//$('#environment').val("-1");
	
	//clear project 
	$('#project').val("-1"); 
	
	//clear product
	$('#product').val("");
	
	//clear ips 
	$('#ips').prop('checked',false);
	
	//clear email 
	$('#email').val("");
	
	//clear customer type list
	$("#listcusttype").empty();	
	
	//clear selected customer type
	$('#selected_cust_type').val("");
	
	//clear extended query
	$('#extended_query').val("");		
	
	clear_search_result();		
			
}

//Clear Page Content
function clear_page_by_project(event){	 
	
	//clear product
	$('#product').val("");
	
	//clear ips 
	$('#ips').prop('checked',false);
	
	//clear email 
	$('#email').val("");
	
	//clear customer type list
	$("#listcusttype").empty();	
	
	//clear selected customer type
	$('#selected_cust_type').val("");
	
	clear_all_checked_custtypes(event);
	
	//clear extended query
	$('#extended_query').val("");			
	
	clear_search_result();
			
}

//Clear Search Result
function clear_search_result(){

	//clear customer key result
	$('#customerkey_result').val("");
	$('#accountidentifier_result').val("");
	$('#consumerprofilekey_result').val("");
	$('#userid_result').val("");
	$('#email_result').val("");
	
	//clear query
	$('#sql_body').empty();

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
	if(loading_task <= 0)
	{
		//$('#uiLockId').remove();
		$('#please_wait_modal').modal('hide');
	}
}

//Show Success Message
function show_success_dialog(message)
{
	$('#success_message').html('<p>'+ message +'</p>');
	$('#SuccessDialog').modal();
}

//Show Error Message
function show_error_dialog(message)
{
	$('#error_message').html('<p>'+ message +'</p>');
	$('#ErrorDialog').modal();
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


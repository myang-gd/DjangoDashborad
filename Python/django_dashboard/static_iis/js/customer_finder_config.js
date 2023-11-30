/* 
 * Javascript functions for Customer Finder Configuration.
 * 
 * Author:  William Chen
 * 
 */
// Customer View Model
var my_view_model = {};
// My Projects
var my_projects = [];
//My Customer Type List
var my_custtype_list = {};
//Selected custtype id
var my_custtype_id = "";
//Selected custtype name
var selected_custtype_name = ""; 

//Current database Id
var my_database_id =-1;

//Current project Id
var my_project_name =-1;
//Current project name
var my_project_temp_name = ""; 
//productkey or product type
var my_product = [];
//Current productTypeId
var my_producttype_id = "";  
//email prefix list
var email_prefix_list = [];
//userid prefix list
var userid_prefix_list = [];
//password rules list
var my_password_rules = [];
//sub query list
var sub_query_list = [];
//current sub query id
var current_sub_query_id = -1;
//current UI status
var my_status = "none";
//Loading task count 
var loading_task = 0;
//product map node start index
var data_tt_id = 1;
//is CustomerType Configurable or not
var isConfigurable = false; 
//sorted customer type
var sorted_custType = [];
//This variable use to save is enabled status
var isEnableChecked = false;

//initialize
function initial_hide(){
	
	$('#emailprefix_panel').hide();
	$('#useridprefix_panel').hide();
	$('#leftpanel .form-group:nth-child(2)').hide();
	$('#joinCondition').hide();	
	$('#filterCondition').hide();	
	$('#filterParam').hide();	
	
	$('#EmailPrefix_Div').hide();	
	$('#UserIdPrefix_Div').hide();	
	$('#PasswordRule_Div').hide();
	$('#SelfDefinedSql_panel').hide();
	$('#productmap_collection').hide();
}

function initial_disabled(){
		
	$('#emailPrefix').prop('disabled', true);		
	$('#userIdPrefix').prop('disabled', true);
}

function initialize()
{	
	//clear database id
	my_database_id = '';
	
	//clear project id
    my_project_name = '';	
    
    //clear all page content
    clear_page_content();
    
    //initialize disabled items
    initial_disabled();         
 	
 	my_project_temp_name = get_project_name(my_projects);
	
}

//Save data into view model 
function new_search_condition(event)
{
	
	//clear view model
	//my_view_model = {};

	my_database_id = -1;
	
	my_database_id = $('#database').val();
	
	if(my_database_id == -1){
		show_error_dialog('Please select a database');
		return;
	}
	
	my_view_model["dataBaseId"] = my_database_id;
	
	//clear project id
    my_project_name = -1;	
    
	//Get Current Value from page
	my_project_name = $('#project').val();			
	
	var current_entity = $('#entity').val(); 

	//if(my_project_name == -1 && isConfigurable == true){
	if(my_project_name == -1){
		show_error_dialog('Please select a project');
		return;
	}			
		
	//Common Data
	
	
	my_view_model["projectName"] = my_project_name;	
	
	//Customer Type Info
	var my_customer_type = $('#cust_type_name').val(); 	
	//my_custtype_id = get_cust_type_id(my_custtype_list,my_customer_type);	
	
	var isConfigurable = $('#isConfigurable').prop('checked');	
	var isVisible = $('#isVisible').prop('checked');
	
	my_view_model["customerTypeId"] =  my_custtype_id;
	my_view_model["customerTypeName"] = my_customer_type;
	my_view_model["customerTypeDesc"] = $('#cust_type_desc').val();
	my_view_model["params"] = $('#params').val();
	my_view_model["paramsDesc"] = $('#paramsDesc').val();	
	
	if(isVisible == true){
		my_view_model["isVisible"] = "True";
	}else{
		my_view_model["isVisible"] = "False";
	}			
	
	//Sub Query 
	my_view_model["sqlCommand"] = $('#sqlCommand').val();
	my_view_model["selectListItem"] = $('#selectListItem').val();
	my_view_model["tableListItem"] = $('#tableListItem').val();
	my_view_model["alias"] = $('#alias').val();
	my_view_model["joinCondition"] = $('#joinCondition').val();
	my_view_model["filterCondition"] = $('#filterCondition').val();
	my_view_model["filterParam"] = $('#filterParam').val();
	my_view_model["selfDefinedSQLQuery"] = $('#selfDefinedSQLQuery').val();
	
    //Product Map			
	my_view_model["productTypeName"] = $('#product_type_name').val();
	my_view_model["productKey"] = $('input#product_key').val();
	my_view_model["ipsProductKey"] = $('input#ips_product_key').val();;
	
	//Email Prefix	
	my_view_model["emailPrefixName"] = $('#email_prefix').val();
			
	//UserId Prefix	
	my_view_model["userIdPrefixName"] = $('#userid_prefix').val();	

	//Password Rule	
	my_view_model["userIdRegex"] = $('#userId_regex').val();	
	my_view_model["userPassword"] = $('#user_password').val();	
}

function new_custtype_conditions(event){

	//clear view model
	my_view_model = {};

	my_view_model["projectName"] = my_project_name;	
	my_view_model["customerTypeName"] =	$('#new_cust_type_name').val();
	my_view_model["customerTypeDesc"] = $('#new_cust_type_desc').val();
	my_view_model["params"] = $('#new_parameter_name').val();
	my_view_model["paramsDesc"] = $('#new_parameters_desc').val();
	my_view_model["isConfigurable"] = $('#isConfigurableForNewCustType').prop('checked');
	my_view_model["isVisible"] = $('#isVisibleForNewCustType').prop('checked');
}

//new customer type enable disable conditions
function new_custtype_enable_disable_conditions(event){
			
	//clear view model
	my_view_model = {};
			
	var my_customer_type = $('#cust_type_name').val(); 			
	var current_target =  $(event.currentTarget);
	
	//Customer Type Info	
	my_view_model["projectName"] = my_project_name;
	my_view_model["customerTypeId"] =  my_custtype_id;
	my_view_model["customerTypeName"] = my_customer_type;
	my_view_model["customerTypeDesc"] = $('#cust_type_desc').val();
	my_view_model["params"] = $('#params').val();
	my_view_model["paramsDesc"] = $('#paramsDesc').val();
	//my_view_model["isConfigurable"] = $('#isConfigurable').prop('checked');
	my_view_model["isVisible"] = $('#isVisible').prop('checked');
	my_view_model["isEnable"] = $('#CustType_Div #isEnabled').prop('checked');	
	
	$('#EnableDisableDialog #enableDisableCustType').show();
	$('#EnableDisableDialog #enableDisableProductType').hide();
	$('#EnableDisableDialog #enableDisableEmailPrefix').hide();
	$('#EnableDisableDialog #enableDisableUserIdPrefix').hide();
	$('#EnableDisableDialog #enableDisablePasswordRule').hide();
	
	$('#EnableDisableDialog').modal();
}

//new sub queries save conditions
function new_sub_queries_save_conditions(event){

	//clear view model
	my_view_model["sub_queries"] = [];

	sub_query = {'subQueryId':'','sqlCommand':'', 'customerTypeName':'', 'selectListItem':'', 'tableListItem':'','alias':'','joinCondition':'','joinSequence':'','filterCondition':'','filterParam':'','selfDefinedSQLQuery':'','operationType':''};

	if($('input[name="cust_type"]:checked').attr('isconfigurable') == 'True'){

		$('#SubQuery_Div div:not([data-tt-custtypename="Default"])').each(function(index,element){	
			
			sub_query["subQueryId"] = $(element).attr("data-tt-id");
			sub_query["sqlCommand"]  = $(element).find('#sqlCommand').val();
			sub_query["customerTypeName"] = $('#cust_type_name').val();
			sub_query["selectListItem"]  = $(element).find('#selectListItem').val();
			sub_query["tableListItem"]  = $(element).find('#tableListItem').val();
			sub_query["alias"]  = $(element).find('#alias').val();
			sub_query["joinCondition"]  = $(element).find('#joinCondition').val();
			sub_query["joinSequence"]  = $(element).attr("data-tt-joinsequence");
			sub_query["filterCondition"]  = $(element).find('#filterCondition').val();
			sub_query["filterParam"]  = $(element).find('#filterParam').val();	
			sub_query["selfDefinedSQLQuery"]  = $('#selfDefinedSQLQuery').val();				
			sub_query["operationType"] = $(element).attr("data-operation-type");
			my_view_model["sub_queries"].push(sub_query);
		});
	
		//Check if has sub queries in view model	
		if(my_view_model["sub_queries"].length>0 & my_view_model["org_sub_queries"].length>0){
		check_change_with_sub_queries();	
		}
	}else{
		sub_query["subQueryId"] = $('#selfDefinedSQLQuery').attr("data-tt-id");
		sub_query["customerTypeName"] = $('#cust_type_name').val();
		sub_query["selfDefinedSQLQuery"]  = $('#selfDefinedSQLQuery').val();
		sub_query["joinSequence"]  = 1;
		sub_query["operationType"] = $('#selfDefinedSQLQuery').attr('data-operation-type');
		my_view_model["sub_queries"].push(sub_query);
	}		
}

function check_change_with_sub_queries(){
	
	for(var i=0; i<my_view_model["sub_queries"].length;i++){
		for(var j=0; j<my_view_model["org_sub_queries"].length;j++){					 					
			if((my_view_model["sub_queries"][i]["subQueryId"] == my_view_model["org_sub_queries"][j]["subQueryId"])
				& (my_view_model["sub_queries"][i]["sqlCommand"] == my_view_model["org_sub_queries"][j]["sqlCommand"])
				& (my_view_model["sub_queries"][i]["customerTypeName"] == my_view_model["org_sub_queries"][j]["customerTypeName"])
				& (my_view_model["sub_queries"][i]["selectListItem"] == my_view_model["org_sub_queries"][j]["selectListItem"])
				& (my_view_model["sub_queries"][i]["tableListItem"] == my_view_model["org_sub_queries"][j]["tableListItem"])
				& (my_view_model["sub_queries"][i]["alias"] == my_view_model["org_sub_queries"][j]["alias"])
				& (my_view_model["sub_queries"][i]["joinCondition"] == my_view_model["org_sub_queries"][j]["joinCondition"])
				& (my_view_model["sub_queries"][i]["joinSequence"] == my_view_model["org_sub_queries"][j]["joinSequence"])
				& (my_view_model["sub_queries"][i]["filterCondition"] == my_view_model["org_sub_queries"][j]["filterCondition"])
				& (my_view_model["sub_queries"][i]["filterParam"] == my_view_model["org_sub_queries"][j]["filterParam"])){
				my_view_model["sub_queries"].splice(i,1);
			}				
		}
	}
	
}


//new password rule enable disable conditions
function new_enable_disable_conditions(event){	

	//clear view model
	//my_view_model = {};
	
	//clear project id
    my_project_name = -1;	
    
	//Get Current Value from page
	my_project_name = $('#project').val();
	
	if(my_project_name == -1){
		show_error_dialog('Please select a project');
		return;
	}		
		
	my_view_model["projectName"] = my_project_name;		
	
}

//Handle with display of different entities
function handle_display_with_different_entities(event){
	
	database_id = $('#database').val();
	
	if(my_database_id == -1){
		show_error_dialog('Please select a database');
		return;
	}	
	
	var selectd_entity = $('#entity').val(); 
	
	if(selectd_entity == 'CustomerType'){
		
		//clear customer type info
		clear_custtype_info();
	
		//clear sub query content
		clear_sub_query_info();
		
		load_custtype_list(event);

		$('#leftpanel .form-group:nth-child(2)').show();		
		$('#productmap_collection').hide();	
		$('#EmailPrefix_Div').hide();	
		$('#UserIdPrefix_Div').hide();
		$('#PasswordRule_Div').hide();
		$('#emailprefix_panel').hide();	
		$('#useridprefix_panel').hide();
		$('#SelfDefinedSql_panel').hide();			
		$('#st_panel').show();		
		$('#middlepanel form:nth-child(1)').show();		
		$('#SubQuery_Div').show();
		$('#saveQuery').show();
		$('#SqlPannel_Div').show();
		$('#ShowQueryBtn_Div').show();			
	}else if(selectd_entity == 'ProductMap'){		
		load_productmap(event);
		$('#st_panel').hide();
		$('#middlepanel form:nth-child(1)').hide();		
		$('#emailprefix_panel').hide();	
		$('#useridprefix_panel').hide();
		$('#EmailPrefix_Div').hide();	
		$('#UserIdPrefix_Div').hide();
		$('#PasswordRule_Div').hide();
		$('#SubQuery_Div').hide();
		$('#saveQuery').hide();
		$('#SqlPannel_Div').hide();
		$('#ShowQueryBtn_Div').hide();							
		$('#SelfDefinedSql_panel').hide();	
		$('#productmap_collection').show();		
		$('#leftpanel .form-group:nth-child(2)').show();		
	}else if(selectd_entity == 'EmailPrefix'){
		if($("#project").val() <0){
			show_error_dialog('Please select project.');
			return;
		}
		load_email_prefix(event);
		$('#st_panel').hide();
		$('#middlepanel form:nth-child(1)').hide();					
		$('#useridprefix_panel').hide();
		$('#productmap_collection').hide();			
		$('#UserIdPrefix_Div').hide();	
		$('#PasswordRule_Div').hide();
		$('#SubQuery_Div').hide();
		$('#saveQuery').hide();
		$('#SqlPannel_Div').hide();
		$('#ShowQueryBtn_Div').hide();							
		$('#SelfDefinedSql_panel').hide();			
		$('#leftpanel .form-group:nth-child(2)').show();		
		$('#emailprefix_panel').show();
		$('#EmailPrefix_Div').show();
	}else if(selectd_entity == 'UserIDPrefix'){			
		if($("#project").val() <0){
			show_error_dialog('Please select project.');
			return;
		}
		
		load_userid_prefix(event); 
		$('#st_panel').hide();
		$('#middlepanel form:nth-child(1)').hide();		
		$('#emailprefix_panel').hide();			
		$('#productmap_collection').hide();
		$('#EmailPrefix_Div').hide();	
		$('#PasswordRule_Div').hide();
		$('#SubQuery_Div').hide();
		$('#saveQuery').hide();
		$('#SqlPannel_Div').hide();
		$('#ShowQueryBtn_Div').hide();							
		$('#SelfDefinedSql_panel').hide();			
		$('#leftpanel .form-group:nth-child(2)').show();		
		$('#UserIdPrefix_Div').show();
		$('#useridprefix_panel').show();
	}else if(selectd_entity == 'PasswordRule'){			
		if($("#project").val() <0){
			show_error_dialog('Please select project.');
			return;
		}
		
		load_password_rules(event); 
		$('#st_panel').hide();
		$('#middlepanel form:nth-child(1)').hide();		
		$('#emailprefix_panel').hide();			
		$('#productmap_collection').hide();
		$('#EmailPrefix_Div').hide();	
		$('#PasswordRule_Div').hide();
		$('#SubQuery_Div').hide();
		$('#saveQuery').hide();
		$('#SqlPannel_Div').hide();
		$('#ShowQueryBtn_Div').hide();							
		$('#SelfDefinedSql_panel').hide();							
		$('#UserIdPrefix_Div').hide();
		$('#useridprefix_panel').hide();
		$('#leftpanel .form-group:nth-child(2)').show();
		$('#PasswordRule_Div').show();
	}else{
		$('#leftpanel .form-group:nth-child(2)').hide();		
		$('#productmap_collection').hide();	
		$('#EmailPrefix_Div').hide();	
		$('#UserIdPrefix_Div').hide();
		$('#PasswordRule_Div').hide();
		$('#emailprefix_panel').hide();	
		$('#useridprefix_panel').hide();
		$('#SelfDefinedSql_panel').hide();		
		$('#st_panel').show();		
		$('#middlepanel form:nth-child(1)').show();
		$('#saveQuery').show();
		$('#SubQuery_Div').show();		
		$('#SqlPannel_Div').show();
		$('#ShowQueryBtn_Div').show();	
	}	   
}

//Handle with display of different entities
function append_sqlCondition_according_to_sqlCommand(event){

	var sqlCommand = $(event.target).val();
	
	if(sqlCommand == 'SELECT'){
		$(event.target).parent().find('#selectListItem').show();
		$(event.target).parent().find('#tableListItem').show();
		$(event.target).parent().find('#alias').show();
		$(event.target).parent().find('#joinCondition').hide();	
		$(event.target).parent().find('#filterCondition').hide();	
		$(event.target).parent().find('#filterParam').hide();		
	}else if(sqlCommand == 'JOIN' | sqlCommand == 'LEFT JOIN' | sqlCommand == 'RIGHT JOIN'){				
		$(event.target).parent().find('#selectListItem').hide();
		$(event.target).parent().find('#tableListItem').show();
		$(event.target).parent().find('#alias').show();
		$(event.target).parent().find('#joinCondition').show();	
		$(event.target).parent().find('#filterCondition').hide();	
		$(event.target).parent().find('#filterParam').hide();		
	}else if(sqlCommand == 'WHERE' | sqlCommand == 'AND' | sqlCommand == 'OR'){
		$(event.target).parent().find('#selectListItem').hide();
		$(event.target).parent().find('#tableListItem').hide();
		$(event.target).parent().find('#alias').hide();
		$(event.target).parent().find('#joinCondition').hide();	
		$(event.target).parent().find('#filterCondition').show();	
		$(event.target).parent().find('#filterParam').show();		
	}else if(sqlCommand == 'ORDER BY'){
		$(event.target).parent().find('#selectListItem').show();
		$(event.target).parent().find('#tableListItem').hide();
		$(event.target).parent().find('#alias').hide();
		$(event.target).parent().find('#joinCondition').hide();	
		$(event.target).parent().find('#filterCondition').hide();	
		$(event.target).parent().find('#filterParam').hide();	
	}else{
		$(event.target).parent().find('#selectListItem').show();
		$(event.target).parent().find('#tableListItem').show();
		$(event.target).parent().find('#alias').show();
		$(event.target).parent().find('#joinCondition').hide();	
		$(event.target).parent().find('#filterCondition').hide();	
		$(event.target).parent().find('#filterParam').hide();	
	}	   	   
}

//Show Self-Defined Query If checkbox "isConfigurable" is checked
function show_self_definded_sql_panel(isConfigurable){		
	
	if(isConfigurable == false){
		$('#leftpanel .form-group:nth-child(2)').show();
		$('#SelfDefinedSql_panel').show();
		$('#SubQuery_Div').hide();
		$('#SqlPannel_Div').hide();
		$('#ShowQueryBtn_Div').hide();	
		$('#saveQuery').hide();
	}else if(isConfigurable == true){
		$('#leftpanel .form-group:nth-child(2)').hide();
		$('#SelfDefinedSql_panel').hide();		
		$('#SubQuery_Div').show();
		$('#SqlPannel_Div').show();
		$('#ShowQueryBtn_Div').show();	
		$('#saveQuery').show();
	}
}

//Present product map table
function present_productmap_table(data){		
		
	var content = '';				
	
	var table_head = "<tr class='alert alert-warning'><th width='10%'>Product Type</th><th <th width='45%'>Product Key</th><th <th width='35%'>IPS Product Key</th><th width='7%'>Is Enable</th><th width='3%'></th></tr>";
	
	$('#product_table thead tr').remove();
	
	$('#product_table thead').append(table_head);
	
	for(var i=0; i<data.length; i++){
		
		node_id = data[i]["Id"];
		
		if(data[i]["projectName"] == my_project_temp_name | data[i]["projectName"] == 'Global'){
			
		content += product_model_to_html(data[i],node_id);																
		}				
	} 
	
	$('#product_table thead').append(content);
}

//Generate html text for one product map
function product_model_to_html(jsondata,node_id)
{
	if(jsondata == null){
		show_error_dialog('Internal model is invalid');
		return;
	}	

	//NodeId for data mapping with view
	jsondata['NodeId'] = node_id;		
	
	jsondata = convert_null_to_empty(jsondata);		
      
	var content = "<tr data-tt-id='"+ node_id +"' class='success branch expanded'>";	
    
      //content = content + "<td align='left' ><p id='bt_"+data_tt_id+"' type='button' class='btn btn-link' onclick=toggle_child_click(this)>+</p></td>";	
      content = content + "<td data-td-id='1' id='product-type'>" + jsondata['productType'] +"</td>";
      content = content + "<td data-td-id='2' id='product-key'>" + jsondata['productKey'] + "</td>";
      content = content + "<td data-td-id='3' id='ips-product-key'>" + jsondata['ipsProductKey'] + "</td>";
      
      if(jsondata['isEnable'] == "True"){
    	  content = content + "<td data-td-id='4' id='is-enable'><input type='checkbox' id='isEnabled' onclick='check_uncheck_producttype_isenable_checkbox(event);' checked/></td>";
    	  }else{
    		  content = content + "<td data-td-id='4' id='is-enable'><input type='checkbox' id='isEnabled' onclick='check_uncheck_producttype_isenable_checkbox(event);'/></td>";
    	  }
       
      content = content + "<td data-td-id='5' algin='right'><button type='button' id='edit' class='btn btn-primary btn-sm' onclick='edit_productmap_tr(event);'>Edit</button></td>";          
      
      content = content + "</tr>";       
          
      
    return content;
} 

//Edit Current row in table
function edit_productmap_tr(event){		
	
	var content = '';
	
	//get row id in table 
	var current_target =  $(event.currentTarget);
	
	var par_id = current_target.parent().parent().attr('data-tt-id');
		
	var element_index =	find_element_by_nodeid(my_product, par_id);			
	
	content = '<label for="product_type_name_lbl">Product Type Name:</label><input type="text" class="form-control" id="product_type_name" value="'+ my_product[element_index]["productType"] +'" placeholder="Product Type Name" ></br>';
	content += '<label for="product_key_lbl">Product Key:</label><input type="text" class="form-control" id="product_key" value="' + my_product[element_index]["productKey"] +'" placeholder="Product Key" ></br>';
	content += '<label for="ips_product_key_lbl">IPS Product Key:</label><input type="text" class="form-control" id="ips_product_key" value="'+ my_product[element_index]["ipsProductKey"] +'" placeholder="IPS Product Key" ></br>';
	
	$('#ProductMapDialog .modal-body').html(content);
	
	$('button#addProductMap').hide();
	
	$('button#updateProductMap').show();
		
	$('#ProductMapDialog').modal();
	
	my_view_model["productTypeId"] = par_id;
	
}

//Add new customer type
function add_one_custtype_click(event){
	
	var content = '';			
	
	content = '<label for="customer_type_name_lbl">Customer Type Name:</label><input type="text" class="form-control" id="new_cust_type_name" placeholder="Customer Type Name" ><br>';
	content += '<label for="customer_type_description_lbl">Customer Type Description:</label><input type="text" class="form-control" id="new_cust_type_desc" placeholder="Customer Type Description" ><br>';
	content += '<label for="parameter_name_lbl">Parameter Name:</label><input type="text" class="form-control" id="new_parameter_name" placeholder="Parameter Name" ><br>';
	content += '<label for="parameters_description_lbl">Parameters Description:</label><input type="text" class="form-control" id="new_parameters_desc" placeholder="Parameters Description" ><br>';
	content += '<div class="form-inline">';
	content += '<input type="checkbox" class="form-control"  id="isConfigurableForNewCustType" checked/>';
	content += '<label for="isConfigurable">isConfigurable</label><br>';
	content += '<input type="checkbox" class="form-control"  id="isVisibleForNewCustType"/>';
	content += '<label for="isVisible">isVisible</label><br>'; 
	$('#CustomerTypeDialog .modal-body').html(content);
	
    $('#CustomerTypeDialog').modal();

}

//Add Sub Query
function add_one_query_click(event){
	
	//Add Button
	var current_target =  $(event.currentTarget);
	
	//Original Selected SqlCommand Value
	var org_sqlCommand_value = current_target.parent().find('#sqlCommand').val();
	
	var clone = current_target.parent().clone(true);
	//clone.appendTo(after(current_target.parent()));
	current_target.parent().after(clone);
	//Set New Copied SqlCommand Value as Original Value
	clone.find('#sqlCommand').val(org_sqlCommand_value);
	clone.attr('data-tt-id','-1');
	clone.attr('data-tt-joinsequence','-1');
	clone.attr('data-operation-type','add');
	//Set each element of copied line as editable
	current_target.parent().children().each(function(index,element){
		$(element).prop('disabled',false);
	});
}

//Append blank Sub Query
function append_blank_sub_query(){

	var selected_cust_type = $('input[name="cust_type"]:checked').val()

	if($('#SubQuery_Div div[data-tt-id="8"]').next().attr('data-tt-id') == '9'){
		var clone = $('#SubQuery_Div div[data-tt-id="8"]').clone(true);		
		$('#SubQuery_Div div[data-tt-id="8"]').after(clone);		
		clone.attr('data-tt-id','-1');
		clone.attr('data-tt-joinsequence','-1');
		clone.attr('data-operation-type','add');
		clone.children().each(function(index,element){
			$(element).prop('disabled',false);
			$(element).val("");
		});
		clone.find('#sqlCommand').val("JOIN");
		clone.attr('data-tt-custtypename',selected_cust_type);
		clone.append('<input type="checkbox" id="isSubQueryEnabled" onclick="check_uncheck_subquery_isenable_checkbox(event);" checked> isEnabled</input>');
	}

	if($('#SubQuery_Div div[data-tt-id="9"]').next().attr('data-tt-id') == '10'){
		var clone = $('#SubQuery_Div div[data-tt-id="9"]').clone(true);	
		$('#SubQuery_Div div[data-tt-id="9"]').after(clone);		
		clone.attr('data-tt-id','-1');
		clone.attr('data-tt-joinsequence','-1');
		clone.attr('data-operation-type','add');
		clone.children().each(function(index,element){
			$(element).prop('disabled',false);
			$(element).val("");
		});	
		clone.find('#sqlCommand').val("AND");
		clone.attr('data-tt-custtypename',selected_cust_type);
		clone.append('<input type="checkbox" id="isSubQueryEnabled" onclick="check_uncheck_subquery_isenable_checkbox(event);" checked> isEnabled</input>');

	}
}

//Remove Current Sub Query
function remove_current_query_click(event){
	if($('#SubQuery_Div div').length == 1){
		return;
	}
	var current_target =  $(event.currentTarget);		
	current_target.parent().remove();
}


//Append blank productmap
function add_one_productmap_click(event){
	
	var content = '';
	
	$('button#updateProductMap').hide();
	
	$('button#addProductMap').show();
	
	content = '<label for="product_type_name_lbl">Product Type Name:</label><input type="text" class="form-control" id="product_type_name" placeholder="Product Type Name" ><br>';
	content += '<label for="product_key_lbl">Product Key:</label><input type="text" class="form-control" id="product_key" placeholder="Product Key" ><br>';
	content += '<label for="ips_product_key_lbl">IPS Product Key:</label><input type="text" class="form-control" id="ips_product_key" placeholder="IPS Product Key" ><br>';			
	
	$('#ProductMapDialog .modal-body').html(content);
	
    $('#ProductMapDialog').modal();

}

//Check Status of isEnable Checkbox
function check_uncheck_producttype_isenable_checkbox(event){

	//get row id in table 
	var current_target =  $(event.currentTarget);

	isEnableChecked = current_target.prop('checked');
	
	var par_id = current_target.parent().parent().attr('data-tt-id');			
	
	//Product View Model
	var productmap_element_index =	find_element_by_nodeid(my_product,par_id);	
	my_view_model["productTypeId"] = my_product[productmap_element_index]["Id"];
	my_view_model["productTypeName"] = my_product[productmap_element_index]["productType"];
	my_view_model["productKey"] = my_product[productmap_element_index]["productKey"];
	my_view_model["ipsProductKey"] = my_product[productmap_element_index]["ipsProductKey"];			
	
	show_confirm_dialog_by_target("product_type");
}

//Check Status of isEnable Checkbox
function check_uncheck_custtype_isenable_checkbox(event){			

	var current_target =  $(event.currentTarget);

	isEnableChecked = current_target.prop('checked');

	show_confirm_dialog_by_target("cust_type");
	
}

//Check Status of isEnable Checkbox
function check_uncheck_subquery_isenable_checkbox(event){

	//clear view model
	my_view_model = {};

	//get row id in table 
	var current_target =  $(event.currentTarget);	

	isEnableChecked = current_target.prop('checked');	 	
	
	var par_id = current_target.parent().attr('data-tt-id');
	//Email Prefix View Model
	var sub_query_index = find_element_by_nodeid(sub_query_list,par_id);

	current_sub_query_id = par_id;
	
	my_view_model["subQueryId"] = current_sub_query_id;
	my_view_model["customerType"] = sub_query_list[sub_query_index]["CustomerTypeName"];
	my_view_model["sqlCommand"] = sub_query_list[sub_query_index]["SQLCommand"];
	my_view_model["selectListItem"] = sub_query_list[sub_query_index]["SelectListItem"];		
	my_view_model["filterCondition"] = sub_query_list[sub_query_index]["FilterCondition"];
	my_view_model["filterParam"] = sub_query_list[sub_query_index]["FilterParam"];	
	my_view_model["joinCondition"] = sub_query_list[sub_query_index]["JoinCondition"];
	my_view_model["joinSequence"] = sub_query_list[sub_query_index]["JoinSequence"];		
	my_view_model["selfDefinedSQLQuery"] = sub_query_list[sub_query_index]["SelfDefinedSQLQuery"];
	my_view_model["tableListItem"] = sub_query_list[sub_query_index]["TableListItem"];
	my_view_model["alias"] = sub_query_list[sub_query_index]["Alias"];
		
	show_confirm_dialog_by_target("sub_query");
}

//Edit Current row in table
function edit_email_prefix_tr(event){		
	
	var content = '';	
	
	//get row id in table 
	var current_target =  $(event.currentTarget);
	
	var par_id = current_target.parent().parent().attr('data-tt-id');
		
	var element_index =	find_element_by_nodeid(email_prefix_list, par_id);			
			
	content = '<label for="email_prefix_lbl">Prefix Name:</label><input type="text" class="form-control" id="email_prefix" value="' + email_prefix_list[element_index]["Name"] + '" placeholder="Email Prefix Name" ></br>';	
	
	$('#EmailPrefixDialog .modal-body').html(content);
	
	$('button#addEmailPrefix').hide();
	
	$('button#updateEmailPrefix').show();
		
	$('#EmailPrefixDialog').modal();
	
	my_view_model["emailPrefixId"] = par_id;	
}

//Append blank productmap
function add_one_email_prefix_click(event){
    
	var content = '';	
	
	$('button#updateEmailPrefix').hide();
	
	$('button#addEmailPrefix').show();
	
    content = '<label for="email_prefix_lbl">Prefix Name:</label><input type="text" class="form-control" id="email_prefix" placeholder="Email Prefix Name" ></br>';	
	
	$('#EmailPrefixDialog .modal-body').html(content);
		
    $('#EmailPrefixDialog').modal();  	
}

//Check Status of isEnable Checkbox
function check_uncheck_emailprefix_isenable_checkbox(event){

	//clear view model
	my_view_model = {};

	//get row id in table 
	var current_target =  $(event.currentTarget);

	isEnableChecked = current_target.prop('checked');
	
	var par_id = current_target.parent().parent().attr('data-tt-id');			
	
	//Email Prefix View Model
	var emailprefix_element_index =	find_element_by_nodeid(email_prefix_list,par_id);
	
	my_view_model["emailPrefixId"] = email_prefix_list[emailprefix_element_index]["Id"];
	my_view_model["emailPrefixName"] = email_prefix_list[emailprefix_element_index]["Name"];		
		
	show_confirm_dialog_by_target("email_prefix");		
}

//Edit Current row in table
function edit_userid_prefix_tr(event){		
	
	var content = '';	
	
	//get row id in table 
	var current_target =  $(event.currentTarget);
	
	var par_id = current_target.parent().parent().attr('data-tt-id');
		
	var element_index =	find_element_by_nodeid(userid_prefix_list,par_id);			
	
	content = '<label for="userid_prefix_lbl">Prefix Name:</label><input type="text" class="form-control" id="userid_prefix" value="'+ userid_prefix_list[element_index]["Name"] +'" placeholder="UserID Prefix Name" ></br>';	
		
	$('#UserIdPrefixDialog .modal-body').html(content);
	
	$('button#addUserIdPrefix').hide();
	
	$('button#updateUserIdPrefix').show();
		
	$('#UserIdPrefixDialog').modal();
	
	my_view_model["userIdPrefixId"] = par_id;	
}

//Append blank productmap
function add_one_userid_prefix_click(event){
	
	var content = '';	
	
	$('button#addUserIdPrefix').show();
	
	$('button#updateUserIdPrefix').hide();
	
	content = '<label for="userid_prefix_lbl">Prefix Name:</label><input type="text" class="form-control" id="userid_prefix" placeholder="UserID Prefix Name" ></br>';
	
	$('#UserIdPrefixDialog .modal-body').html(content);
		
	$('#UserIdPrefixDialog').modal();	
}

//Check Status of isEnable Checkbox
function check_uncheck_useridprefix_isenable_checkbox(event){

	//clear view model
	my_view_model = {};

	//get row id in table 
	var current_target =  $(event.currentTarget);
	
	isEnableChecked = current_target.prop('checked');

	var par_id = current_target.parent().parent().attr('data-tt-id');			
	
	//UserID Prefix View Model
	var useridprefix_element_index = find_element_by_nodeid(userid_prefix_list,par_id);
	
	my_view_model["userIdPrefixId"] = userid_prefix_list[useridprefix_element_index]["Id"];
	my_view_model["userIdPrefixName"] = userid_prefix_list[useridprefix_element_index]["Name"];			
	
	show_confirm_dialog_by_target("userid_prefix");	
}

//Edit Current row in table
function edit_password_rule_tr(event){		
	
	var content = '';	
	
	//get row id in table 
	var current_target =  $(event.currentTarget);
	
	var par_id = current_target.parent().parent().attr('data-tt-id');
		
	var element_index =	find_element_by_nodeid(my_password_rules,par_id);			
	
	content = '<label for="userid_regex_lbl">UserId Regex:</label><input type="text" class="form-control" id="userId_regex" value="'+ my_password_rules[element_index]["UserIdRegex"] +'" placeholder="UserID Regex" ></br>';	
	content += '<label for="user_password_lbl">User Password:</label><input type="text" class="form-control" id="user_password" value="'+ my_password_rules[element_index]["UserPassword"] +'" placeholder="User Password" ></br>';	
		
	$('#PasswordRuleDialog .modal-body').html(content);
	
	$('button#addPasswordRule').hide();
	
	$('button#updatePasswordRule').show();
		
	$('#PasswordRuleDialog').modal();
	
	my_view_model["passwordRuleId"] = par_id;	
}

//Append blank productmap
function add_one_password_rule_click(event){
	
	var content = '';	
	
	$('button#addPasswordRule').show();
	
	$('button#updatePasswordRule').hide();
		
	content = '<label for="userid_regex_lbl">UserId Regex:</label><input type="text" class="form-control" id="userId_regex" placeholder="UserID Regex" ></br>';	
	content += '<label for="user_password_lbl">User Password:</label><input type="text" class="form-control" id="user_password" placeholder="User Password" ></br>';	
	
	$('#PasswordRuleDialog .modal-body').html(content);
		
	$('#PasswordRuleDialog').modal();	
}

//Check Status of isEnable Checkbox
function check_uncheck_passwordrule_isenable_checkbox(event){

	//clear view model
	my_view_model = {};

	//get row id in table 
	var current_target =  $(event.currentTarget);

	isEnableChecked = current_target.prop('checked');

	var par_id = current_target.parent().parent().attr('data-tt-id');			
	
	//UserID Prefix View Model
	var passwordrule_element_index = find_element_by_nodeid(my_password_rules,par_id);
	
	my_view_model["passwordRuleId"] = par_id;
	my_view_model["userIdRegex"] = my_password_rules[passwordrule_element_index]["UserIdRegex"];
	my_view_model["userPassword"] = my_password_rules[passwordrule_element_index]["UserPassword"];
	
	show_confirm_dialog_by_target("password_rule");
}

//Show confirm Dialog by Target
function show_confirm_dialog_by_target(dialog_type){

	$('#EnableDisableDialog #enableDisableCustType').hide();
	$('#EnableDisableDialog #enableDisableProductType').hide();
	$('#EnableDisableDialog #enableDisableEmailPrefix').hide();
	$('#EnableDisableDialog #enableDisableUserIdPrefix').hide();
	$('#EnableDisableDialog #enableDisablePasswordRule').hide();
	$('#EnableDisableDialog #enableDisableSubQuery').hide();

	if(dialog_type == 'password_rule'){
		$('#EnableDisableDialog #enableDisablePasswordRule').show();
	}else if(dialog_type == 'userid_prefix'){
		$('#EnableDisableDialog #enableDisableUserIdPrefix').show();
	}else if(dialog_type == 'email_prefix'){
		$('#EnableDisableDialog #enableDisableEmailPrefix').show();
	}else if(dialog_type == 'sub_query'){
		$('#EnableDisableDialog #enableDisableSubQuery').show();
	}else if(dialog_type == 'product_type'){
		$('#EnableDisableDialog #enableDisableProductType').show();
	}else if(dialog_type == 'cust_type'){
		$('#EnableDisableDialog #enableDisableCustType').show();
	}			

	$('#EnableDisableDialog').modal();	
}

//Set count of rows increment as node id if you click "Add New Product Map" link 
function count_rows_increment(event){
   
	var node_id = 0;

	node_id++;	
	
	node_id = document.getElementById("product_table").getElementsByTagName("tr").length -1  + node_id;	

	return node_id
}

//Find page position in view model by node id
function find_element_by_nodeid(data,nodeid)
{
	var element_index = -1;
	
	for (var i=0;i<data.length;i++){
		if(data[i]["Id"] == nodeid)
		{
			element_index = i;
			break;
		}
	}
	return element_index;
}

//Present Selected UserId Prefix
function present_selected_userid_prefix(element){
	
	var current_userid_prefix = '';
	
	var current_element = element;
	
	if($(current_element).prop('checked')==true){
	    
		current_userid_prefix = $(current_element).next().text();
		
		$('#userIdPrefix').val(current_userid_prefix);				
	} 		
}

//Present Selected Email Prefix
function present_selected_email_prefix(element){
	
	var current_email_prefix = '';
	
	var current_element = element;
	
	$('#isEnabled').prop("checked", false);
	$('#isEnabled').prop("disabled", true);
	
	if($(current_element).prop('checked')==true){
	
		current_email_prefix = $(current_element).next().text();
		
		$('#emailPrefix').val(current_email_prefix);
		
		for(var i=0; i<email_prefix_list.length; i++){
			if(email_prefix_list[i]["Name"] == current_email_prefix && email_prefix_list[i]["IsEnable"]=="True"){
				
				$('#isEnabled').prop("checked", true);
			}
		}		
	}else{
		$('#emailPrefix').val('');
		$('#isEnabled').prop("checked", false);
	}		
}

//Get Product Type Id by Product Type Name
function get_product_type_id(data,productTypeName){
	
	my_producttype_id = data[productTypeName];
	
	return my_producttype_id;	
}

//Save Sub Queries
function save_sub_queries(event){
	
	new_sub_queries_save_conditions(event);

	for(var i=0;i<my_view_model["sub_queries"].length;i++){
		if(my_view_model["sub_queries"][i]["operationType"]=='add'){
			add_query(event,my_view_model["sub_queries"][i]);
		}else if(my_view_model["sub_queries"][i]["operationType"]=='update'){
			update_query(event,my_view_model["sub_queries"][i]);
		}		
	}	
}

//Present Sub Queries By Customer Type
function present_sub_queries_by_custtype(data){	
	
	var org_sub_query = {'subQueryId':'', 'sqlCommand':'', 'customerTypeName':'', 'selectListItem':'', 'tableListItem':'','alias':'','joinSequence':'','joinCondition':'','filterCondition':'','filterParam':'','selfDefinedSQLQuery':'','operationType':''};

	my_view_model["org_sub_queries"] = [];

	//clear old sub query value
	clear_sub_query_info();
	//Remove SubQueryForm Div except first
	$('#SubQuery_Div div').first().nextAll().remove();		

	//Copy first SubQueryForm 
	for(var i=0;i<data.length-1;i++){		
		$('#SubQueryForm').clone(true).appendTo('#SubQuery_Div');		
	}		

	//Add unique id for each SubQueryForm
	$('#SubQuery_Div div').each(function(index){	
		
		$(this).attr('data-tt-id',data[index]["Id"]);		
		$(this).attr('data-tt-custtypename',data[index]["CustomerTypeName"]);	
		$(this).attr('data-tt-joinsequence',data[index]["JoinSequence"]);
		$(this).attr("data-operation-type","update");	
		$(this).find('#sqlCommand').val($.trim(data[index]["SQLCommand"]));		
		$(this).find('#sqlCommand').trigger('change');
		if(data[index]["SQLCommand"] == 'SELECT'){
			$(this).find('#selectListItem').val(data[index]["SelectListItem"]);
			$(this).find('#tableListItem').val(data[index]["TableListItem"]);
			$(this).find('#alias').val(data[index]["Alias"]);
		}else if(data[index]["SQLCommand"] == 'JOIN'| data[index]["SQLCommand"] == 'LEFT JOIN' | data[index]["SQLCommand"] == 'RIGHT JOIN'){			
			$(this).find('#tableListItem').val(data[index]["TableListItem"]);
			$(this).find('#alias').val(data[index]["Alias"]);
			$(this).find('#joinCondition').val(data[index]["JoinCondition"]);
		}else if(data[index]["SQLCommand"] == 'WHERE' | data[index]["SQLCommand"] == 'AND' | data[index]["SQLCommand"] == 'OR'){
			$(this).find('#filterCondition').val(data[index]["FilterCondition"]);
			$(this).find('#filterParam').val(data[index]["FilterParam"]);			
		}else if(data[index]["SQLCommand"] == 'ORDER BY'){
			$(this).find('#selectListItem').val(data[index]["SelectListItem"]);
		}
	

		if(data[index]["CustomerTypeName"] == 'Default'){
			$(this).children().each(function(index,element){
				if($(element).attr('id') != 'addQuery' | $(element).attr('id') != 'removeQuery'){
					$(element).prop('disabled',true);
				}				
			});
		}else{
			
			//Save Values which custtypeName is not default as original sub queries
			org_sub_query = {'subQueryId': data[index]["Id"], 'customerTypeName': data[index]["CustomerTypeName"],'sqlCommand' : data[index]["SQLCommand"], 'selectListItem': data[index]["SelectListItem"], 'tableListItem':data[index]["TableListItem"],'alias': data[index]["Alias"],'joinSequence':data[index]["joinSequence"],'joinCondition':data[index]["JoinCondition"],'filterCondition': data[index]["FilterCondition"], 'filterParam': data[index]["FilterParam"], 'selfDefinedSQLQuery': data[index]["SelfDefinedSQLQuery"],'operationType':'update'};
			my_view_model["org_sub_queries"].push(org_sub_query);

			$(this).append('<input type="checkbox" id="isSubQueryEnabled" onclick="check_uncheck_subquery_isenable_checkbox(event);" checked> isEnabled</input>');
			$(this).children().each(function(index,element){
				if($(element).attr('id') == 'removeQuery'){
					$(element).prop('disabled',true);					
				}else{
					$(element).prop('disabled',false);	
				}
			});
		}

		//Display disabled sub query
		if(data[index]["IsEnable"]=="False"){
			//$(this).prop('disabled',true);			
			$(this).children().each(function(index,element){
				if ($(element).is(':visible') === true ){
					if($(element).attr('id') == "isSubQueryEnabled"){
						$(element).prop('checked',false);
					}

					if($(element).attr('type') != "checkbox" & $(element).attr('type') != "button"){
						$(element).attr('style','color:red');					
					}			
				}				
			});		
		}else{
			$(this).children().each(function(index,element){
				if ($(element).is(':visible') === true ){
					if($(element).attr('id') == "isSubQueryEnabled"){
						$(element).prop('checked',true);
					}
					
					if($(element).attr('sytle') === 'color:red'){
						$(element).removeAttr('style');					
					}			
				}				
			});		
		}
	});	

	//Append Blank Sub Query
	append_blank_sub_query();
	
}

//Disable current sub query
function disable_current_sub_query(){
	if(current_sub_query_id!= -1){
		$("#SubQuery_Div [data-tt-id="+ current_sub_query_id+ "]").prop('disabled',true);
		$("#SubQuery_Div [data-tt-id="+ current_sub_query_id+ "]").children().each(function(index,element){
			if($(element).attr('type') != "checkbox" & $(element).attr('type') != "button"){
				$(element).attr('style','color:red');
			}			
		});		
	}		
}

//Present Query 
function present_sql(data){		
	var sql = ""; 
	
	for(var i=0; i<data.length; i++){
		
		convert_null_to_empty(data[i]);		
	
		if(data[i]["SelfDefinedSQLQuery"] != ""){
			sql = data[i]["SelfDefinedSQLQuery"];
		}else{
			if(data[i]["SQLCommand"] != null && data[i]["SQLCommand"]!= ""){
				sql += data[i]["SQLCommand"] + ' '
			}
			
			if(data[i]["SelectListItem"] != null && data[i]["SelectListItem"]!= ""){
				sql += data[i]["SelectListItem"] + ' '
			}
			
			if(data[i]["TableListItem"] != null && data[i]["TableListItem"]!= ""){
				sql += data[i]["TableListItem"] + ' '
			}
			
			if(data[i]["Alias"] != null && data[i]["Alias"]!= ""){
				sql += data[i]["Alias"] + ' '
			}
			
			if(data[i]["JoinCondition"] != null && data[i]["JoinCondition"]!= ""){
				sql += data[i]["JoinCondition"] + ' '
			}
			
			if(data[i]["FilterCondition"] != null && data[i]["FilterCondition"]!= ""){
				sql += data[i]["FilterCondition"] + ' '
			}
			
			if(data[i]["FilterParam"] != null && data[i]["FilterParam"]!= ""){
				sql += data[i]["FilterParam"] + ' '
			}
			
			sql += ' \r\n'					
		}							
	} 	
						
	$('#sql_body').remove();
	
	$('#sql_panel').append("<div class='panel-body' id='sql_body'><pre>" + sql + "</pre></div>");
}

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

//Sort Customer Types by alphabet
function sort_custtypes_alphabetical(data){
	
	sorted_custType = [];
	
	for(var i=0;i<data.length;i++){
		sorted_custType.push(data[i]["custType"]);		
	}			
	
	sorted_custType.sort();
	
	return sorted_custType;
}

//Present customer type list to page
function append_custtype_list_to_html(data){
					
	content = '';
	
	$("#listcusttype input").remove();
	
	var custtypes = sort_custtypes_alphabetical(data);   
	
	for(var i=0;i<custtypes.length;i++){			  		        
			    
		for(var j=0; j < data.length; j++){							
			
			if(data[j]["custType"] == custtypes[i]){
								
				content = content + '<input type="radio" isConfigurable="' + data[j]["isConfigurable"] + '" onclick="present_selected_custtypes(event);load_queries_by_custtype(event);" name= "cust_type" value="'+ custtypes[i] +'">'+ custtypes[i] + '</input>&nbsp;&nbsp;';
																	
			}																	 	
		}
		
		if(custtypes[i] != custtypes[custtypes.length-1][i]){					
			
			content= content + '</br>';	
		}		
			
		$("#listcusttype").html(content); 
	}	  	 
}

//Present Enable Disable Checkbox
function present_enable_disable_status(data,id){
			
	var isEnabled = data[id]["isEnable"];
	
	if(isEnabled == "True"){
		
		$('#isEnabled').prop("checked", true);
		
	}
	if(isEnabled == "False"){
		
		$('#isEnabled').prop("checked", false);
		
	}		
}

//Present Email Prefix list to page
function append_emailprefix_list_to_html(data){
					
    var content = '';
	
	for(var i=0;i<data.length;i++){							   		    		
		
		if(data[i]["Id"] != '' && data[i]["Id"] != null){
			
		    content += '<tr data-tt-id="'+ data[i]["Id"] +'" class="success branch expanded">';				
			content = content + '<td id="email_prefix_id">' + data[i]["Id"] + '</td>';
			content = content + '<td id="email_prefix_Name">' + data[i]["Name"] + '</td>';
			
			if(data[i]["IsEnable"] == "True"){
				content = content + '<td id="is-enable"><input type="checkbox" id="isEnabled" onclick="check_uncheck_emailprefix_isenable_checkbox(event);" checked/></td>';
				}
						
		    if(data[i]["IsEnable"] == "False"){
		    	content = content + '<td id="is-enable"><input type="checkbox" id="isEnabled" onclick="check_uncheck_emailprefix_isenable_checkbox(event);"/></td>';
				}								
						
			content = content + '<td algin="right"><button type="button" class="btn btn-primary btn-sm" onclick="edit_email_prefix_tr(event);">Edit</button></td></tr>';		
		}		
	}	
	
	$("#emailprefix_table tbody tr").remove();
	
	$("#emailprefix_table tbody").append(content);	
}

//Present userid prefix list to page
function append_useridprefix_list_to_html(data){
					
	var content = '';
	
	for(var i=0;i<data.length;i++){							   			   		
		
		if(data[i]["Id"] != '' && data[i]["Id"] != null){
			
		    content += "<tr data-tt-id='"+ data[i]["Id"] +"' class='success branch expanded'>";	
			content = content + '<td id="user_prefix_id">' + data[i]["Id"] + '</td>';
			content = content + '<td id="user_prefix_Name">' + data[i]["Name"] + '</td>';
			
			if(data[i]["IsEnable"] == "True"){
				content = content + '<td id="is-enable"><input type="checkbox" id="isEnabled" onclick="check_uncheck_useridprefix_isenable_checkbox(event);" checked/></td>';
			}
			
			if(data[i]["IsEnable"] == "False"){
				content = content + '<td id="is-enable"><input type="checkbox" id="isEnabled" onclick="check_uncheck_useridprefix_isenable_checkbox(event);"/></td>';
			}
			
			content = content + '<td algin="right"><button type="button" class="btn btn-primary btn-sm" onclick="edit_userid_prefix_tr(event);">Edit</button></td></tr>';	
		}				
	}	
	
	$("#useridprefix_table tbody tr").remove();
	$("#useridprefix_table tbody").append(content);			
}

//present selected customer types to page
function present_selected_custtypes(event){			
		    
	var data = my_custtype_list;	    
    
    selected_custtype_name = $('input[name="cust_type"]:checked').val();
    
    //initialize checkbox not checked
    $('#isVisible').prop("checked", false);
    $('#isEnabled').prop("checked", false);
    $('#isEnabled').prop("disabled", false);    
    $('#CustType_Div').attr('data-attr-configurable','False');
    for(var i=0;i<data.length;i++){		
    
	    if(selected_custtype_name == data[i]["custType"]){
	    	
	    	my_custtype_id = data[i]["Id"];
	    	
	    	$('#cust_type_name').val(data[i]["custType"]);
	    	
	    	$('#cust_type_desc').val(data[i]["custTypeDescription"]);
	    	
	    	$('#params').val(data[i]["Params"]);
	    	
	    	$('#paramsDesc').val(data[i]["paramDescription"]);
	    	    	
	        if(data[i]["isConfigurable"] == "True"){
	            $('#CustType_Div').attr('data-attr-configurable','True');

	        }
	        
	        if(data[i]["isVisible"] == "True"){
	        	$('#isVisible').prop("checked", true);	
	        }
	        
	        if(data[i]["isEnable"] == "True"){
	        	$('#isEnabled').prop("checked", true);
	        }    	 
	    }	
	}   

	my_view_model["isConfigurable"] = $('#CustType_Div').attr('data-attr-configurable');
}

//edit selected customer type
function edit_selected_custtypes(event){
	
	$('#selected_cust_type').prop('disabled', false);	
}

//Present new added custtype
function present_new_added_custtype(){

	var new_custtype = my_view_model["customerTypeName"];

	$('#custtype_list input[value="' + new_custtype + '"]').ready(function(){
				
		$('input[value="' + new_custtype + '"]').click();				
	});
}

//Present password rules table
function present_password_rules_table(data){		
		
	var content = '';				
	
	for(var i=0;i<data.length;i++){							   			   		
		
		if(data[i]["Id"] != '' && data[i]["Id"] != null){
			
		    content += "<tr data-tt-id='"+ data[i]["Id"] +"' class='success branch expanded'>";	
			content = content + '<td id="password_rule_id">' + data[i]["Id"] + '</td>';
			content = content + '<td id="user_id_regex">' + data[i]["UserIdRegex"] + '</td>';
			content = content + '<td id="user_password_td">' + data[i]["UserPassword"] + '</td>';
			
			if(data[i]["IsEnable"] == "True"){
				content = content + '<td id="is-enable"><input type="checkbox" id="isEnabled" onclick="check_uncheck_passwordrule_isenable_checkbox(event);" checked/></td>';
			}
			
			if(data[i]["IsEnable"] == "False"){
				content = content + '<td id="is-enable"><input type="checkbox" id="isEnabled" onclick="check_uncheck_passwordrule_isenable_checkbox(event);"/></td>';
			}
			
			content = content + '<td algin="right"><button type="button" class="btn btn-primary btn-sm" onclick="edit_password_rule_tr(event);">Edit</button></td></tr>';	
		}				
	}	
	
	$("#passwordrule_table tbody tr").remove();
	$("#passwordrule_table tbody").append(content);	
}

//get project name
function get_project_name(data){
	
	var project_name = "Global";
	
	for(var i = 0 ; i< data.length; i++){
		if(my_project_name == data[i]["projectName"]){
			project_name = data[i]["projectName"];			
		}
	}
	
	return project_name;
}

//convert null to empty
function convert_null_to_empty(data)
{	
	json = data;
	
	for (var key in json){
			if (json[key] == null){
				json[key] = "";	
			}
	}
	
	return json;
}

//Click cancel will roll back is enable checked status
/*function cancel_confirm_dialog(event){

	var current_target =  $(event.currentTarget);

	var current_confirm_btn = current_target.siblings().attr( "style", "display: inline-block;" ).id;

	//var current_enable_checkbox = 

	switch(current_confirm_btn) {
		case 'enableDisableCustType':
			$('#CustType_Div #isEnabled').prop('checked',isEnableChecked);
			break;
		case 'enableDisableProductType':
			$('#product_table #isEnabled').prop('checked',isEnableChecked);
			break;
		case 'enableDisableEmailPrefix':
			$('#EmailPrefix_Div #isEnabled').prop('checked',isEnableChecked);
			break;
		case 'enableDisableUserIdPrefix':
			$('#UserIdPrefix_Div #isEnabled').prop('checked',isEnableChecked);			
			break;
		case 'enableDisablePasswordRule':
			$('#PasswordRule_Div #isEnabled').prop('checked',isEnableChecked);			
			break;
		case 'enableDisableSubQuery':
			$('#CustType_Div #isEnabled').prop('checked',isEnableChecked);			
			break;
	}
	//isEnableChecked

}*/

//clear current custtype info
function clear_custtype_info(){
	$('#cust_type_name').val('');
	$('#params').val('');	
	$('#cust_type_desc').val('');	
	$('#paramsDesc').val('');	
	$('#isConfigurable').prop('checked',false);
	$('#isVisible').prop('checked',false);
	$('#isEnabled').prop('checked',false);
}

//clear sub query content
function clear_sub_query_info(){
	$('#sqlCommand').val('SELECT');
	$('#selectListItem').val('');
	$('#tableListItem').val('');
	$('#alias').val('');
	$('#joinCondition').val('');	
	$('#filterCondition').val('');	
	$('#filterParam').val('');		
}

//Clear Page Content 
function clear_page_content(){
	
	//clear selected entity
	$('#entity').val('-1');
	
	//clear email and userid prefix
	$('#emailPrefix').val('');
	$('#userIdPrefix').val('');
	
	//clear customer type info
	clear_custtype_info();
	
	//clear sub query content
	clear_sub_query_info();
	
}

//Main Functions

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
			show_error_dialog('Load projects error');
			ui_unlock();
			}
		});		
}

//Load Product Map
function load_productmap(event){
	
	my_project_name = $("#project").val();
	my_database_id = $("#database").val();
	
	ui_lock(1);
	
	$.ajax({
		type:  "Get",
		url:  "../get-productmap/?project=" + my_project_name + "&data_Base_Id=" + my_database_id,
		headers:  {"X-CSRFToken": event.data.csrf_token },								
		
		success:  function(data) {				
			
			my_product = data;
			
			my_project_temp_name = get_project_name(my_projects);
			present_productmap_table(data);
			
			ui_unlock();
			},
	    			
		error:  function(data) {
			show_error_dialog('Load productmap error');
			ui_unlock();
			}
		});		
}

//Load Email Prefix
function load_email_prefix(event){
	
	my_project_name = $('#project').val();
	my_database_id = $("#database").val();
	
	$.ajax({
		type:  "Get",
		url:  "../get-emailprefix/?project=" + my_project_name + "&data_Base_Id=" + my_database_id,
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {
			
			append_emailprefix_list_to_html(data);
			
			email_prefix_list = data;	
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog('Load Email Prefix error');
			ui_unlock();
			}
		});	
}

//Load UserID Prefix
function load_userid_prefix(event){
	
	my_project_name = $('#project').val();
	my_database_id = $("#database").val();
			
	$.ajax({
		type:  "Get",
		url:  "../get-useridprefix/?project=" + my_project_name + "&data_Base_Id=" + my_database_id,
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {
			
			append_useridprefix_list_to_html(data);
			
			userid_prefix_list = data;	
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog(data["message"]);
			ui_unlock();
			}
		});	
}

//Load Customer Type List
function load_custtype_list(event){		
	my_database_id = $('#database').val();
	my_project_name = $('#project').val();
	ui_lock(1);	
	$.ajax({
		type:  "Get",
		url:  "../get-custtypelist/?project=" + my_project_name + "&data_Base_Id=" + my_database_id,
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {					
			append_custtype_list_to_html(data);
			
			my_custtype_list = data;			
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog(data["message"]);
			ui_unlock();
			}
		});		
}

//Load Password Rules
function load_password_rules(event){		
	
	my_project_name = $('#project').val();
	my_database_id = $("#database").val();
	ui_lock(1);	
	$.ajax({
		type:  "Get",
		url:  "../get-passwordrule/?project=" + my_project_name + "&data_Base_Id=" + my_database_id,
		headers:  {"X-CSRFToken": event.data.csrf_token },
		
		success:  function(data) {					
			present_password_rules_table(data);
			
			my_password_rules = data;			
			
			ui_unlock();
			},
		
		error:  function(data) {
			show_error_dialog(data["message"]);
			ui_unlock();
			}
		});		
}

//Add new customer type
function add_custtype(event){

	new_custtype_conditions(event);
	
	var data = JSON.stringify(my_view_model);		
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../add-customertype/",
		headers:  {"X-CSRFToken": event.data.csrf_token },		
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			load_custtype_list(event);									

			ui_unlock();	

			//clear page content
			clear_custtype_info();
			clear_sub_query_info();

			//present_new_added_custtype();
			},
		error:function(data) {				
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});	
}

//Update current customer type
function update_custtype(event){	
	
	new_search_condition(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../update-customertype/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {
			show_success_dialog(data["message"]);  
			
			load_custtype_list(event);
			ui_unlock();	
			
			//clear page content
			clear_custtype_info();
			clear_sub_query_info();	
			},
		error:function(data) {		
			
			show_error_dialog(data["message"]);
			ui_unlock();
			}
		});	
}

//Enable and Disable Selected Customer Type
function enable_disable_current_custtype(event){
	
	new_custtype_enable_disable_conditions(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../enabledisable-custtype/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {			
			
			show_success_dialog(data["message"]);
								
			ui_unlock();			
			},
		error:function(data) {										
				
			show_error_dialog(data["message"]);
			ui_unlock();
			
			}
		});
}

//Add Query
function add_query(event,view_model){					
	
	var data = JSON.stringify(view_model);
	
	//ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../add-query/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {	
			//show_success_dialog(data["message"]);
			//ui_unlock();			
			},
		error:function(data) {
			show_error_dialog(data["message"]);
			//ui_unlock();
			}
		});
}

//Add Query
function update_query(event,view_model){					
	
	var data = JSON.stringify(view_model);
	
	//ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../update-query/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {	
			
			//ui_unlock();			
			},
		error:function(data) {
			show_error_dialog(data["message"]);
			//ui_unlock();
			}
		});
}

//Append new product map
function add_productmap(event){
	
	new_search_condition(event);	
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../add-productmap/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			load_productmap(event);
								
			ui_unlock();			
			},
		error:function(data) {				
			
			show_error_dialog(data["message"]);
			
			ui_unlock();			
			}
		});	
}

//Update a product map
function update_productmap(event){
	
	new_search_condition(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../update-productmap/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {
			
			show_success_dialog(data["message"]);
			
			load_productmap(event);
								
			ui_unlock();			
			},
		error:function(data) {
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});	
}

//Enable or Disable Selected Product Type in Product map
function enable_disable_current_producttype(event){
	
	new_enable_disable_conditions(event);
		
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../enabledisable-productmap/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {			
			
			show_success_dialog(data["message"]);
								
			ui_unlock();			
			},
		error:function(data) {										
				
			show_error_dialog(data["message"]);
			
			ui_unlock();
			
			}
		});
}	

//Add UserId Prefix
function add_userid_prefix(event){
	
	new_search_condition(event);	
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../add-useridprefix/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {
            
			show_success_dialog(data["message"]);
			
			load_userid_prefix(event);
											
			ui_unlock();			
			},
		error:function(data) {			
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});	
}

//Update UserId Prefix
function update_userid_prefix(event){			
	
	new_search_condition(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../update-useridprefix/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {

			show_success_dialog(data["message"]);
			
			load_userid_prefix(event);
								
			ui_unlock();			
			},
		error:function(data){
			
			show_error_dialog(data["message"]);
							
			ui_unlock();
			}
		});	
}

//Enable and Disable UserId Prefix
function enable_disable_current_useridprefix(event){
	
	new_enable_disable_conditions(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../enabledisable-useridprefix/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {			
			
			show_success_dialog(data["message"]);
								
			ui_unlock();			
			},
		error:function(data) {										
				
			show_error_dialog(data["message"]);
			ui_unlock();
			
			}
		});
}

//Add Email Prefix
function add_email_prefix(event){			
		
	new_search_condition(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../add-emailprefix/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {

			show_success_dialog(data["message"]);
			
			load_email_prefix(event);
								
			ui_unlock();			
			},
		error:function(data) {		
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
}

//Update Email Prefix
function update_email_prefix(event){	
	
	new_search_condition(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../update-emailprefix/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {			
			
			show_success_dialog(data["message"]);
			load_email_prefix(event);
								
			ui_unlock();			
			},
		error:function(data) {		
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
}

//Enable Disable Email Prefix
function enable_disable_current_emailprefix(event){	
	
	new_enable_disable_conditions(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../enabledisable-emailprefix/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {		
			
			show_success_dialog(data["result"]);
								
			ui_unlock();			
			},
		error:function(data) {										
				
			show_error_dialog(data["message"]);
			ui_unlock();
			
			}
		});
}

function add_password_rule(event){

	new_search_condition(event);
	my_view_model["passwordRuleId"] = -1;	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../add-passwordrule/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {

			show_success_dialog(data["message"]);
			
			load_password_rules(event);
								
			ui_unlock();			
			},
		error:function(data) {		
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
}

function update_password_rule(event){

	new_search_condition(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../update-passwordrule/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {

			show_success_dialog(data["message"]);
			
			load_password_rules(event);
								
			ui_unlock();			
			},
		error:function(data) {		
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
}

function enable_disable_current_password_rule(event){

	new_enable_disable_conditions(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../enabledisable-passwordrule/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {

			show_success_dialog(data["message"]);
			
			load_password_rules(event);
								
			ui_unlock();			
			},
		error:function(data) {		
			
			show_error_dialog(data["message"]);
			
			ui_unlock();
			}
		});
}

//Load Queries by customer type
function load_queries_by_custtype(event){			
	
	my_view_model["customerTypeName"] =  $('input[name="cust_type"]:checked').val();
	my_view_model["databaseId"] =  $('#database').val();
	
	var data = JSON.stringify(my_view_model);	
		
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../load-queries/",
		headers:  {"X-CSRFToken": event.view.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {			
			
			present_sql(data);

			if($('input[name="cust_type"]:checked').attr("isConfigurable") == "False"){	
				if(data[0]["errorReason"] != null){
					$('#selfDefinedSQLQuery').attr('data-operation-type','add');
					$('#selfDefinedSQLQuery').val('');
				}else{
					$('#selfDefinedSQLQuery').attr('data-operation-type','update');
					$('#selfDefinedSQLQuery').attr('data-tt-id',data[0]["Id"]);
		    		$('#selfDefinedSQLQuery').val(data[0]["SelfDefinedSQLQuery"]);
				}								
		    	show_self_definded_sql_panel(false);
		    }else{

		    	show_self_definded_sql_panel(true);
		    	present_sub_queries_by_custtype(data);
		    }						
			
			sub_query_list = data;
			//show_success_dialog(data["message"]);
								
			ui_unlock();			
			},
		error:function(data) {
			
			$('#SubQuery_Div div').first().nextAll().remove();			
			show_error_dialog(data["message"]);
			ui_unlock();
			}
		});
	
}

function enable_disable_current_sub_query(event){

	new_enable_disable_conditions(event);
	
	var data = JSON.stringify(my_view_model);	
	
	ui_lock(1);
		
	$.ajax({
		type: "Post",
		url:  "../enabledisable-subquery/",
		headers:  {"X-CSRFToken": event.data.csrf_token },
		data:  {"myjsondata": data},
	
		success:  function(data) {

			show_success_dialog(data["message"]);			
			disable_current_sub_query();	
			load_queries_by_custtype(event);							
			ui_unlock();			
			},
		error:function(data) {		
			
			show_error_dialog(data["message"]);
			
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
	if(loading_task <= 0)
	{
		//$('#uiLockId').remove();
		$('#please_wait_modal').modal('hide');
	}
}

//Show Error Message
function show_error_dialog(message)
{
	$('h4#error_message').html('<p>'+ message +'</p>');
	$('#ErrorDialog').modal();
}

//Show Success Message
function show_success_dialog(message)
{
	$('h4#success_message').html('<p>'+ message +'</p>');
	$('#SuccessDialog').modal();
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

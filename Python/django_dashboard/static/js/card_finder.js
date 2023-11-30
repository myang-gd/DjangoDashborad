/* 
 * Javascript functions for Card Finder.
 * 
 * Author:  William Chen
 * 
 */

//productkey or product type
var my_product = [];
var selectedproductmap = [];

//Loading task count 
var loading_task = 0;

//initialize     
function initialize(){

	if($('#isProductMap').prop("checked")== true){
		$('#isTsys').prop("disabled",false);	
		$('#isTsys').prop("checked",true);
		$('#isIPS').prop("disabled",true);		
		$('#isProductMap').prop("disabled",false);	
		$('#productmap').show(); 
		$('#product').hide(); 
		$("#load_products").val("");
		$("#load_productmap").val("true");		
		//load productmap
		$('#isProductMap').trigger('change');		
	}else{
		$('#isTsys').prop("disabled",true);	
		$('#isTsys').prop("checked",true);
		$('#isIPS').prop("disabled",true);		
		$('#isProductMap').prop("disabled",false);	
		$('#productmap').hide(); 
		$('#product').show(); 
		$("#load_products").val("true");
		$("#load_productmap").val("");
	}

}

function switch_view(event){
		
	var isProductMapChecked = $('#isProductMap').prop("checked");

	if(isProductMapChecked == true){
		$('#productmap').show();
		$('#product').hide();
		$('#isIPS').prop("disabled",false);	
		$('#isTsys').prop("disabled",false);	
		$('#isTsys').prop("checked",true);
		$('#isIPS').prop("checked",false);
		$("#load_productmap").val("true");
 		$("#load_products").val("false");
	}else{
		$('#productmap').hide();
		$('#product').show();
		$('#isIPS').prop("disabled",true);	
		$('#isIPS').prop("checked",false);	
		$('#isTsys').prop("disabled",true);	
		$('#isTsys').prop("checked",true);	
		$('#isIPS').prop("checked",false);
		$("#load_productmap").val("false");
 		$("#load_products").val("true"); 		
	}
}

function swith_tsys_ips_view(element){

	var element_id = element.id;

	if(element_id == 'isTsys' ){
		$('#isTsys').prop("checked",true);
		$('#isIPS').prop("checked",false);
	}

	if(element_id == 'isIPS' ){
		$('#isTsys').prop("checked",false);
		$('#isIPS').prop("checked",true);
	}
}


//Append product map to datalist
function append_productmap_to_datalist(){	

	var content = '<option>Product</option>'; 

	for(var i=0; i < my_product.length; i++){
		producttype = my_product[i]["productType"];
		productkey = my_product[i]["productKey"];								
					
		//content += '<option value="' + producttype +  '" title="ProductKey:' + productkey +'">' + producttype + '</option>';	
		content += '<option value="' + productkey +  '" title="ProductKey:' + productkey +'">' + producttype + '(' + productkey + ')' + '</option>';														
	}				
	

	$('#productmap option').remove();		
	$('#productmap').append(content);		
	$('#productmap option').tooltip();	
	$("#load_productmap").val("true");
	$("#load_products").val("");
}

//Append ips product map to datalist
function append_ipsproductmap_to_datalist(){
	
	var content = '<option>Product</option>';

	for(var i=0; i < my_product.length; i++){
		producttype = my_product[i]["productType"];
		ipsproductkey = my_product[i]["ipsProductKey"];							
							
		if(ipsproductkey != null){							
			//content += '<option value="' + producttype +  '" title="ProductKey:' + ipsproductkey +'">' + producttype + '</option>';
			content += '<option value="' + ipsproductkey +  '" title="ProductKey:' + ipsproductkey +'">' + producttype + '(' + ipsproductkey + ')' + '</option>';	
		}
	}				
	
	$('#productmap option').remove();	    		
	$('#productmap').append(content);		
	$('#productmap option').tooltip();
	$("#load_productmap").val("true");	
	$("#load_products").val("");
}

//Load Product Map
function load_productmap(event){	

	//ui_lock
	
	$.ajax({
		type:  "Get",
		url:  "../cardfinder/get-productmap",			
		headers:  {"X-CSRFToken": event.data.csrf_token },				

		success:  function(data) {				
			
			my_product = data;		
			
			append_productmap_to_datalist();
			
			//ui_unlock();
			},
	    			
		error:  function(data) {
			//show_error_dialog('Load productmap error');
			//ui_unlock();
			}
		});		
}


/*
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
}*/

/*//Show Success Message
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
}*/


/* ------- ajax.js starts here ------*/
var _ms_XMLHttpRequest_ActiveX = ""; // Holds type of ActiveX to instantiate

function executeReturn( AJAX, postProcess ) {
    if (AJAX.readyState == 4) {
        if (AJAX.status == 200) {
            try {
              eval(AJAX.responseText);
              if(postProcess != undefined && postProcess != null) {
                eval(postProcess);
              }
            } catch (e) {
              // if session has timed out we will throw an exception here
              // need to check that we get re-directed to login screen
              if (e.description != null && e.description == 'Syntax error'){
                //window.location = "/t3Portal/resources/jsp/t3logout.jsp";
              }
            }
        }
    }
}
            function trim(str) {
                return LTrim(RTrim(str));
                
            }
            
            function RTrim(str) {
                
                var re = /((\s*\S+)*)\s*/;
                return str.replace(re, "$1");
                
            }
            
            function LTrim(str) {
                
                var re = /\s*((\S+\s*)*)/;
                return str.replace(re, "$1");
                
            }
/*
 * AJAXRequest: An encapsulated AJAX request. To run, call
 * new AJAXRequest( method, url, data, async )
 *
 */
function AJAXRequest( method, url, data, async, postProcess) {

    // self = this; creates a pointer to the current function
    // the pointer will be used to create a "closure". A closure
    // allows a subordinate function to contain an object reference to the
    // calling function. We can't just use "this" because in our anonymous
    // function later, "this" will refer to the object that calls the function
    // during runtime, not the AJAXRequest function that is declaring the function
    // clear as mud, right?
    // Java this ain't

    var self = this;
    var isIe = false;
    // check the dom to see if this is IE or not
    if (window.XMLHttpRequest) 
    {
        // Not IE
        self.AJAX = new XMLHttpRequest();
    }
    else if (window.ActiveXObject) 
    {
        // Hello IE!
        isIe = true;
        // Instantiate the latest MS ActiveX Objects
        if (_ms_XMLHttpRequest_ActiveX) 
        {
            self.AJAX = new ActiveXObject(_ms_XMLHttpRequest_ActiveX);
        } 
        else 
        {
            // loops through the various versions of XMLHTTP to ensure we're using the latest
            var versions = ["Msxml2.XMLHTTP.7.0", "Msxml2.XMLHTTP.6.0", "Msxml2.XMLHTTP.5.0", "Msxml2.XMLHTTP.4.0", "MSXML2.XMLHTTP.3.0", "MSXML2.XMLHTTP",
                        "Microsoft.XMLHTTP"];
            //var versions = ["Msxml2.XMLHTTP", "Microsoft.XMLHTTP", "Msxml2.XMLHTTP.4.0"];
            for (var i = 0; i < versions.length ; i++) 
            {
                try 
                {
                    // try to create the object
                    // if it doesn't work, we'll try again
                    // if it does work, we'll save a reference to the proper one to speed up future instantiations
                    self.AJAX = new ActiveXObject(versions[i]);

                    if (self.AJAX) 
                    {
                        _ms_XMLHttpRequest_ActiveX = versions[i];
                        break;
                    }
                }
                catch (objException) 
                {
                // trap; try next one
                }
            }
        }
    }
    // create an anonymous function to log state changes
    
    self.AJAX.onreadystatechange = function() 
    {
        if (postProcess == 'handleHealthCheckStatus') 
        {
            handleHealthCheckStatus(self.AJAX);
        }
       // Release 6.3 -9713 Enhancement - Start
        else if (postProcess == 'handlePollCheck') 
        {
            handlePollCheck(self.AJAX);
        }
        else if (postProcess == 'handlePollResponse') 
        {
            handlePollResponse(self.AJAX);
        }
        // Release 6.3 -9713 Enhancement - End
        else if (postProcess == 'handleSendFinalDestination') 
        {
            handleSendFinalDestination(self.AJAX);
        }//added for R7.0.1 Enhancement:11980
        else if (postProcess == 'loginFlagDestResponse')
        {
            loginFlagDestResponse(self.AJAX);
        }
        else if (postProcess == 'handleFavResponse')
        {
            handleFavResponse(self.AJAX);
        }
        // Release 7.0.2 -11804 Enhancement - Start
        else if (postProcess == 'handlePotentialResponse') 
        {
            handlePotentialResponse(self.AJAX);
        }
        // Release 7.0.2 -11804 Enhancement - End
        // Release 7.1.1 -11483 Enhancement - Start
        else if (postProcess == 'handleFilterResponse') 
        {
            handleFilterResponse(self.AJAX);
        }
        else if (postProcess == 'handleFilterCommonResponse') 
        {
            handleFilterCommonResponse(self.AJAX);
        }        
        // Release 7.1.1 -11483 Enhancement - End
         // BT Enhancement - Start
        else if (postProcess == 'handleBTAccessResponse') 
        {
            handleBTAccessResponse(self.AJAX);
        } 
        // BT Enhancement - End
        else if(postProcess == 'handleAirbagResponse')
        {
        	handleAirbagResponse(self.AJAX);
        }
        else if(postProcess == 'handleRepInflResponse')
    	{
        	handleRepInflResponse(self.AJAX);
    	}
        else if(postProcess == 'handleArchiveResponse')
    	{
        	handleArchiveResponse(self.AJAX);
    	}
        else if (postProcess == 'handleTermsOfUseResponse')
        {
        	handleTermsOfUseResponse(self.AJAX);
        }
      //T300018306 BackLog Defect Fixes- Starts
        else if (postProcess == 'handleUrl')
        {
        	handleUrl(self.AJAX);
        }
      //T300018306 BackLog Defect Fixes- Ends
      //TCI-ETAS change starts
        else if (postProcess == 'handleRecPrefResponse')
        {
        	handleRecPrefResponse(self.AJAX);
        }
      //TCI-ETAS change ends
      // CY17 P3 change start
        else if (postProcess == 'handleRemoteCheckResponse') 
        {
        	handleRemoteCheckResponse(self.AJAX);
        } 
        else if (postProcess == 'handleCreateRequestParam') 
        {
        	handleCreateRequestParam(self.AJAX);
        }
        else if (postProcess == 'handleSaveManulaList') 
        {
        	handleSaveManulaList(self.AJAX);
        }
       //CY17 P3 changes end 
        else
        {
        	executeReturn(self.AJAX, postProcess);
        }
    }

    // if no method specified, then default to POST
    if (!method) {
        method = "POST";
    }

    method = method.toUpperCase();
    
    if (typeof async == 'undefined' || async == null) {
        async = true;
    }

    self.AJAX.open(method, url, async);

    if (method == "POST") {
        //self.AJAX.setRequestHeader("Connection", "close");
        self.AJAX.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        self.AJAX.setRequestHeader("Method", "POST " + url + "HTTP/1.1");
    }

    if(!isIe) {
    	self.AJAX.send(data);
    } else {
        self.AJAX.send();
    }

    return self.AJAX;
}



// Clears each select that was passed to this method
// uses Javascripts dynamic argument capability--method isn't
// declared with args, they are looped through
// in the code using the built-in arguments array
function clearSelect() {
    for (var i = 0; i < arguments.length; i++) {
        var element = arguments[i];

        if (typeof element == 'string')
            element = document.getElementsByName(element)[0];

        if (element && element.options) {
            element.options.length = 1;
            element.options[0] = new Option('ALL', 'ALL');
            element.selectedIndex = 0;
        }
    }
}

function clearElement( tagId, optionValue ) {

    var element = tagId;

    if (typeof element == 'string')
        element = document.getElementsByName(element)[0];

    if (element && element.options) {
        element.options.length = 1;
        if(optionValue != null) {
            element.options[0] = new Option(optionValue, '');
        } else {
            element.options[0] = new Option('ALL', 'ALL');
        }
        element.selectedIndex = 0;
    }
}

// TCI CHanges - Start
function clearElementByLanguage( tagId, language, optionValue ) {

    var element = tagId;

    if (typeof element == 'string')
        element = document.getElementsByName(element)[0];

    if (element && element.options) {
        element.options.length = 1;
        if(optionValue != null) {
            element.options[0] = new Option(optionValue, '');
        } else {
        	if(language == 'fr'){
        		element.options[0] = new Option('ALL', 'Tous');
        	}else{
        		element.options[0] = new Option('ALL', 'ALL');
        	}
        }
        element.selectedIndex = 0;
    }
}
// TCI CHanges - End

function clearElementNoOption( tagId ) {
    clearElement( tagId, null);
}

function toggleForm( formName, isActive ) {
	myForm = document.forms[formName];
	if(myForm != "undefined")
	{
		for (var i=0; i<myForm.length; i++) {
	        myForm.elements[i].disabled = isActive;
	    }
	}
}


function getVehicleModelDataBTActionWithPrefix( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,model,prefix ) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset +"&model="+model+"&prefix="+prefix+ "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+key, "bogusData", true, postProcess );
}


function getVehicleSelectDataBTActionWithPrefix( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,year,prefix,division ) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset +"&year="+year+"&prefix="+prefix+ "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+division, "bogusData", true, postProcess );
}

function getVehicleSelectDataBTAction( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,year,division ) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset +"&year="+year+ "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+division, "bogusData", true, postProcess );
}

// base method for calling the vehicle information
function getVehicleSelectDataAction( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,year ,division) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset+"&year="+year + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+division, "bogusData", true, postProcess );
}

function getVehicleSelectData( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,division ) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+division, "bogusData", true, postProcess );
}

function getVehicleModelReveData( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,model ) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset + "&key=" + key +"&model="+model+ "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+key, "bogusData", true, postProcess );
}

function getVehicleSelectDataCalibration( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,prefix) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&prefix=" + prefix + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+key, "bogusData", true, postProcess);
}

function getVehicleSelectDataCalibrationAction( dataset, key, target, addAll, formTagId, postProcess, isFireTarget,prefix,year,division) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset +"&year="+year + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&prefix=" + prefix + "&formTagId=" + formTagId + "&isFireTarget="+"&division="+division, "bogusData", true, postProcess);
}

// base method for calling the service category
function getSymptomSelectData( dataset, language, key, target, addAll, formTagId, postProcess ) {
    return new AJAXRequest("GET", "/t3Portal/ajax/getSymptoms.jsp?dataset=" + dataset + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&language=" + language  + "&formTagId=" + formTagId, "bogusData", true, postProcess );
}

// retrieve a technicians detail information
function getTechnicianDetailData(id, associateId) {
    return new AJAXRequest("GET", "/t3Portal/portlets/tas/reference/dealer/dealerInformation/getTechnicianDetails.jsp?associateId=" + associateId+"&tableId="+id, "bogusData", true, null);
}

function getStandardEquipmentData(vin) {
    var timeVar = new Date().getTime();
    return new AJAXRequest("GET", "/t3Portal/portlets/tas/reference/vehicle/vehicleInformation/standardEquipment.jsp?vin=" + vin+"&time="+timeVar, "bogusData", true, null);
}

//TCI-ETAS Changes starts
function getStandardEquipmentData(vin,tciIndicator) {
    var timeVar = new Date().getTime();
    return new AJAXRequest("GET", "/t3Portal/portlets/tas/reference/vehicle/vehicleInformation/standardEquipment.jsp?vin=" + vin+"&tciIndicator="+ tciIndicator+"&time="+timeVar, "bogusData", true, null);
}
//TCI-ETAS Changes ends

function  getEligibleTechs(dealerCode,detailId,index) {
	
	return new AJAXRequest("GET", "/t3Portal/portlets/tis/reference/serviceCampaign/serviceCampaignInformation/getEligibleTechs.jsp?dealerCode="+dealerCode+"&detailId="+detailId+"&index="+index);
	    //return new AJAXRequest("GET", "/t3Portal/portlets/tis/reference/serviceCampaign/serviceCampaignInformation/getEligibleTechs.jsp?vin=123");
	}

function forcedHealthCheckAjax(url,postProcess) {
    return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
function forcedHealthCheckAjax1(url,postProcess) {
    return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
function remoteDataCreateRequest(url,postProcess) {
    return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
// Release 6.3 -9713 Enhancement - Start
function pollAjax(url,postProcess) {
     return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
// Release 6.3 -9713 Enhancement - End
function getModels( division, target, addAll, formTagId, postProcess ) {
    return getVehicleSelectData( "model", division, target, addAll, formTagId, postProcess, true );
}

function getYearsAction( model, target, addAll, formTagId, postProcess,year,division ) {
    return getVehicleSelectDataAction( "year", model, target, addAll, formTagId, postProcess, true ,year,division);
}

function getModelsBTActionWithPrefix( division, target, addAll, formTagId, postProcess,model,prefix ) {
    return getVehicleModelDataBTActionWithPrefix( "model", division, target, addAll, formTagId, postProcess, true,model,prefix );
}

function getYearsBTAction( model, target, addAll, formTagId, postProcess,year ) {
    return getVehicleSelectDataBTAction( "year", model, target, addAll, formTagId, postProcess, true,year,'' );
}

function getYearsBTActionWithPrefix( model, target, addAll, formTagId, postProcess,year,prefix,division ) {
    return getVehicleSelectDataBTActionWithPrefix( "year", model, target, addAll, formTagId, postProcess, true,year,prefix,division );
}


function getYears( model, target, addAll, formTagId, postProcess,division ) {
    return getVehicleSelectData( "year", model, target, addAll, formTagId, postProcess, true ,division);
}

function getYearsReversByDivision( division, target, addAll, formTagId, postProcess ) {
    return getVehicleSelectData( "yearreverse", division, target, addAll, formTagId, postProcess, false,division );
}

function getModelReverse( division, year, target, addAll, formTagId, postProcess ) {
    return getVehicleSelectData( "modelreversebyyeardiv", division + ',' + year, target, addAll, formTagId, postProcess, false,division );
}

function getModelReverseAction( division, year, target, addAll, formTagId, postProcess,model ) {
    return getVehicleModelReveData( "modelreversebyyeardiv", division + ',' + year, target, addAll, formTagId, postProcess, false ,model);
}

function getServiceCategory( language, target, addAll, formTagId, postProcess ) {
    // Put here for proper construct of the AJAX request
    return getSymptomSelectData( "serviceCategory", language, "serCat", target, addAll, formTagId, postProcess );
}

function getServiceCategoryTIS( language, target, addAll, formTagId, postProcess ) {
    // Put here for proper construct of the AJAX request
    return getSymptomSelectData( "serviceCategoryTIS", language, "serCat", target, addAll, formTagId, postProcess );
}

function getServiceCategoryReverse( section, language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "serviceCategoryReverse", language, section, target, addAll, formTagId, postProcess);
}

function getSection( serviceCategory, language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "section", language, serviceCategory, target, addAll, formTagId, postProcess );
}

function getSectionTIS( serviceCategory, language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "sectionTIS", language, serviceCategory, target, addAll, formTagId, postProcess );
}

function getSectionReverse( subComponent, language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "sectionReverse", language, subComponent, target, addAll, formTagId, postProcess );
}

function getSubComponent( section, language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "subComponent", language, section, target, addAll, formTagId, postProcess );
}

function getSubComponentReverse( condition, language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "subComponentReverse", language, condition, target, addAll, formTagId, postProcess );
}

function getCondition( subComponent, language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "condition", language, subComponent, target, addAll, formTagId, postProcess );
}

function getConditionReverse( language, target, addAll, formTagId, postProcess  ) {
    return getSymptomSelectData( "conditionReverse", language, "conditionReverse", target, addAll, formTagId, postProcess );
}

function getDPRSubComponent( section, language, target, addAll, formTagId, postProcess  ) {
    return getDPRSelectData( "subComponentGroup", language, section, target, addAll, formTagId, postProcess );
}

function getDPRSelectData( dataset, language, key, target, addAll, formTagId, postProcess ) {
    return new AJAXRequest("GET", "/t3Portal/ajax/getDPRCodes.jsp?dataset=" + dataset + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&language=" + language  + "&formTagId=" + formTagId, "bogusData", true, postProcess );
}

function getModelsCalibration( division, target, addAll, formTagId, postProcess,prefix ) {
    return getVehicleSelectDataCalibration( "model", division, target, addAll, formTagId, postProcess, true,prefix);
}

function getYearsCalibration( model, target, addAll, formTagId, postProcess,prefix,year,division ) {
    return getVehicleSelectDataCalibrationAction( "year", model, target, addAll, formTagId, postProcess, true,prefix,year,division );
}

//9.4.1- T18308 -start

function getModelsWithPrefix( division, target, addAll, formTagId, postProcess,prefix ) {
    return getVehicleSelectDataWithPrefix( "model", division, target, addAll, formTagId, postProcess, true, prefix);
}

function getYearsReversByDivisionWithPrefix( division, target, addAll, formTagId, postProcess,prefix ) {
    return getVehicleSelectDataWithPrefix( "yearreverse", division, target, addAll, formTagId, postProcess,true, prefix );
}


function getVehicleSelectDataWithPrefix( dataset, key, target, addAll, formTagId, postProcess, isFireTarget, prefix ) {
    // USING GET because POST works very very slow on IE, but works fine on netscape
    return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset=" + dataset + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&prefix=" + prefix + "&formTagId=" + formTagId + "&isFireTarget=", "bogusData", true, postProcess);
}
function getServiceCategoryTISWithPrefix( language, target, addAll, formTagId, postProcess,prefix,prefixval ) {
    // Put here for proper construct of the AJAX request
    return getSymptomSelectDataWithPrefix( "serviceCategoryTIS", language, "serCat", target, addAll, formTagId, postProcess,prefix,prefixval );
}

function getSymptomSelectDataWithPrefix( dataset, language, key, target, addAll, formTagId, postProcess,prefix,prefixval ) {
    return new AJAXRequest("GET", "/t3Portal/ajax/getSymptoms.jsp?dataset=" + dataset + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&language=" + language  + "&formTagId=" + formTagId + "&prefix=" + prefix + "&prefixval=" + prefixval, "bogusData", true, postProcess );
}

function getSectionTISWithPrefix( serviceCategory, language, target, addAll, formTagId, postProcess,prefix,prefixval) {
    return getSymptomSelectDataWithPrefix( "sectionTIS", language, serviceCategory, target, addAll, formTagId, postProcess,prefix,prefixval );
}

//9.4.1 -180308-end

function clearElementWithPrefix( tagId, prefixval ) {

    var element = tagId;

    if (typeof element == 'string')
        element = document.getElementsByName(element)[0];

    if (element && element.options) {
        element.options.length = 1;
        if(optionValue != null) {
            element.options[0] = new Option(optionValue, '');
        } else {
            element.options[0] = new Option('ALL',prefixval+'ALL');
        }
        element.selectedIndex = 0;
    }
}

//9.4.1
//wrapper for handling Cause Component dropdown
//***Parameters****
//language = language
//target = source netuid selection dropdown tag id
//addAll = true/false for whether to add an ALL option to selection dropdown.
//formTagId = tagid associated with form (if there is a tagid on the form)
//postProcess = anonymous javascript code evaluated at runtime in a closure-ish kind of way
//*******
function getCauseComponent( language, target, addAll, formTagId, postProcess ){
    return getSymptomSelectData( "causeComponent", language, "causeComponent", target, addAll, formTagId, postProcess );
}

//function getCauseComponentReverse(subComponent, language, target, addAll, formTagId, postProcess ){
 //   return getSymptomSelectData( "causeComponentReverse", language, subComponent, target, addAll, formTagId, postProcess );
//}

//wrapper for handling cause subcomponent dropdown
//***Parameters***
//component = cause component that the retrieved subcomponents are based on
//language = language
//target = source netuid selection dropdown tag id
//addAll = true/false for whether to add an ALL option to selection dropdown.
//formTagId = tagid associated with form (if there is a tagid on the form)
//postProcess = anonymous javascript code evaluated at runtime in a closure-ish kind of way
//*********
function getCauseSubComponent(component, language, target, addAll, formTagId, postProcess ){
    return getSymptomSelectData("causeSubComponent", language, component, target, addAll, formTagId, postProcess );
}

//function getCauseSubComponentReverse(condition, language, target, addAll, formTagId, postProcess ){
//    return getSymptomSelectData("causeSubComponentReverse", language, condition, target, addAll, formTagId, postProcess );
//}

//wrapper for handling cause subcomponent dropdown
//***Parameters***
//subComponent = cause subComponent that the retrieved conditions are based on
//language = language
//target = source netuid selection dropdown tag id
//addAll = true/false for whether to add an ALL option to selection dropdown.
//formTagId = tagid associated with form (if there is a tagid on the form)
//postProcess = anonymous javascript code evaluated at runtime in a closure-ish kind of way
//*********
function getCauseCondition(subComponent, language, target, addAll, formTagId, postProcess ){
    return getSymptomSelectData("causeCondition", language, subComponent, target, addAll, formTagId, postProcess );
}

//function getCauseConditionReverse(language, target, addAll, formTagId, postProcess ){
 //   return getSymptomSelectData("causeConditionReverse", language, "causeConditionReverse", target, addAll, formTagId, postProcess );
//}


//R7.0.1 Enhancement:11980 -Start- Ajax call to mark the session variable

function setLoginFlagIndicator(url, postProcess)
{
    return new AJAXRequest("GET", url, "bogusData", false, postProcess);
}

//R7.0.1 Enhancement:11980 -End

//CY17 P3 CHANGES START
function forcedHealthCheckAjax(url,postProcess) {
    return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
//CY17 P3 CHANGES END


// Release 7.0.2 -11804 Enhancement - Start
function potentialGoSeeCandidatesAjax(url,postProcess) {
     return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
// Release 7.0.2 -11804 Enhancement - End

// BT Enhancement - Start
function populateBTAccessAjax(url,postProcess) {
     return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
// BT Enhancement - End

// Release 7.1.1 -11483 Enhancement - Start
function changeFilterAjax(url,postProcess) {
     return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}

function filterCommonAjax(url,postProcess) {
     return new AJAXRequest("GET", url, "bogusData", true, postProcess);
}
// Release 7.1.1 -11483 Enhancement - End

function setDataInSession(attName, attValue) {
    var postProcess = '';
    var timeVar = new Date().getTime();
    // need to escape any + characters in search keyword
    var newAttValue = attValue.replace(/\+/g, "__");
    
    // ensure that we are not sending more than 1000 characters
    //Commented the if loop logic to avoid tas data loss. Not to limit 1000 chars. T300020001 - Start
   /* var valueSize = newAttValue.length;
    if (valueSize > 1000){
    
      for (var i=0; i < valueSize; i=i+1001){
        var newMax = i+1000;
        var thousandChars;
        if (newMax >= valueSize){
          thousandChars = newAttValue.substring(i, valueSize);
        } else {
          thousandChars = newAttValue.substring(i, i+1000);
        }

        thousandChars = encodeURIComponent(thousandChars);

        if (i == 0) { 
          new AJAXRequest("GET", "/t3Portal/ajax/setDataInSession.jsp?clear=true&more=true&attValue=" + thousandChars + "&attName=" + attName+"&time="+timeVar, "bogusData", true, postProcess );
        } else {
          new AJAXRequest("GET", "/t3Portal/ajax/setDataInSession.jsp?more=true&attValue=" + thousandChars + "&attName=" + attName+"&time="+timeVar, "bogusData", true, postProcess );        
        }
      }
    
    } else {*/
        newAttValue = encodeURIComponent(newAttValue);
        return new AJAXRequest("GET", "/t3Portal/ajax/setDataInSession.jsp?attValue=" + newAttValue + "&attName=" + attName+"&time="+timeVar, "bogusData", true, postProcess );
    //}
        
        //T300020001 - End
}
/* ------- ajax.js ends here ------*/

/* ------- t3.js starts here ------*/

// Detect Plugins for Acrobat Reader.  Redirect to page if not found.
function detectBrowser()
{
    var missingPlugins = '';

    var browser = new BrowserDetect();
    if (navigator.appVersion.indexOf("Win") > 0) {    
        if(!(browser.isIE6up || browser.equivalentMozilla != -1))
            document.location = "/t3Portal/BrowserDetect.jsp?missingPlugins=Old_Browser";
        if(!detectPlugin("Acrobat Reader"))
            missingPlugins += "Acrobat_Reader,";
        if (!detectPlugin("JavaWebStart"))
            missingPlugins += "JavaWebStart";
        
        if(missingPlugins != '')
            document.location = "/t3Portal/BrowserDetect.jsp?missingPlugins=" + missingPlugins;
    }
    //detected mimetypes here
}

// Detect Plugins for SVG Viewer, Acrobat Reader, and Flash.  
// Redirect to page if not found.
function detectBrowserWithSVG()
{
    var missingPlugins = '';
    if (location.href.indexOf("detectPlugin=false") == -1)
    {
        var browser = new BrowserDetect();
        if(!(browser.isIE6up || browser.equivalentMozilla != -1))
            document.location = "/t3Portal/BrowserDetect.jsp?missingPlugins=Old_Browser";
        if(!detectPlugin("SVG Viewer"))
            missingPlugins += "SVG_Viewer,";
        if(!detectPlugin("Acrobat Reader"))
            missingPlugins += "Acrobat_Reader,";
        if(!detectPlugin("Shockwave Flash"))
            missingPlugins += "Shockwave_Flash,";  
                
        if (ewdver3Enabled && ewdver3Enabled == 'true') {
            var java = detectJava();
            
            if(java.indexOf("JavaWebStart") != -1)
                missingPlugins += "JavaWebStart"; 
        }
                    
        if(missingPlugins != '')
            document.location = "/t3Portal/BrowserDetect.jsp?missingPlugins=" + missingPlugins;
    }
}

// http://www.dithered.com/javascript/browser_detect/
function BrowserDetect() {
   var ua = navigator.userAgent.toLowerCase();

   // browser engine name
   this.isGecko       = (ua.indexOf('gecko') != -1 && ua.indexOf('safari') == -1);
   this.isAppleWebKit = (ua.indexOf('applewebkit') != -1);

   // browser name
   this.isKonqueror   = (ua.indexOf('konqueror') != -1);
   this.isSafari      = (ua.indexOf('safari') != - 1);
   this.isOmniweb     = (ua.indexOf('omniweb') != - 1);
   this.isOpera       = (ua.indexOf('opera') != -1);
   this.isIcab        = (ua.indexOf('icab') != -1);
   this.isAol         = (ua.indexOf('aol') != -1);
   this.isIE          = (ua.indexOf('msie') != -1 && !this.isOpera && (ua.indexOf('webtv') == -1) );
   this.isMozilla     = (this.isGecko && ua.indexOf('gecko/') + 14 == ua.length);
   this.isFirebird    = (ua.indexOf('firebird/') != -1);
   this.isNS          = ( (this.isGecko) ? (ua.indexOf('netscape') != -1) : ( (ua.indexOf('mozilla') != -1) && !this.isOpera && !this.isSafari && (ua.indexOf('spoofer') == -1) && (ua.indexOf('compatible') == -1) && (ua.indexOf('webtv') == -1) && (ua.indexOf('hotjava') == -1) ) );

   // spoofing and compatible browsers
   this.isIECompatible = ( (ua.indexOf('msie') != -1) && !this.isIE);
   this.isNSCompatible = ( (ua.indexOf('mozilla') != -1) && !this.isNS && !this.isMozilla);

   // rendering engine versions
   this.geckoVersion = ( (this.isGecko) ? ua.substring( (ua.lastIndexOf('gecko/') + 6), (ua.lastIndexOf('gecko/') + 14) ) : -1 );
   this.equivalentMozilla = ( (this.isGecko) ? parseFloat( ua.substring( ua.indexOf('rv:') + 3 ) ) : -1 );
   this.appleWebKitVersion = ( (this.isAppleWebKit) ? parseFloat( ua.substring( ua.indexOf('applewebkit/') + 12) ) : -1 );

   // browser version
   this.versionMinor = parseFloat(navigator.appVersion);

   // correct version number
   if (this.isGecko && !this.isMozilla) {
      this.versionMinor = parseFloat( ua.substring( ua.indexOf('/', ua.indexOf('gecko/') + 6) + 1 ) );
   }
   else if (this.isMozilla) {
      this.versionMinor = parseFloat( ua.substring( ua.indexOf('rv:') + 3 ) );
   }
   else if (this.isIE && this.versionMinor >= 4) {
      this.versionMinor = parseFloat( ua.substring( ua.indexOf('msie ') + 5 ) );
   }
   else if (this.isKonqueror) {
      this.versionMinor = parseFloat( ua.substring( ua.indexOf('konqueror/') + 10 ) );
   }
   else if (this.isSafari) {
      this.versionMinor = parseFloat( ua.substring( ua.lastIndexOf('safari/') + 7 ) );
   }
   else if (this.isOmniweb) {
      this.versionMinor = parseFloat( ua.substring( ua.lastIndexOf('omniweb/') + 8 ) );
   }
   else if (this.isOpera) {
      this.versionMinor = parseFloat( ua.substring( ua.indexOf('opera') + 6 ) );
   }
   else if (this.isIcab) {
      this.versionMinor = parseFloat( ua.substring( ua.indexOf('icab') + 5 ) );
   }

   this.versionMajor = parseInt(this.versionMinor);

   // dom support
   this.isDOM1 = (document.getElementById);
   this.isDOM2Event = (document.addEventListener && document.removeEventListener);

   // css compatibility mode
   this.mode = document.compatMode ? document.compatMode : 'BackCompat';

   // platform
   this.isWin    = (ua.indexOf('win') != -1);
   this.isWin32  = (this.isWin && ( ua.indexOf('95') != -1 || ua.indexOf('98') != -1 || ua.indexOf('nt') != -1 || ua.indexOf('win32') != -1 || ua.indexOf('32bit') != -1 || ua.indexOf('xp') != -1) );
   this.isMac    = (ua.indexOf('mac') != -1);
   this.isUnix   = (ua.indexOf('unix') != -1 || ua.indexOf('sunos') != -1 || ua.indexOf('bsd') != -1 || ua.indexOf('x11') != -1)
   this.isLinux  = (ua.indexOf('linux') != -1);

   // specific browser shortcuts
   this.isNS4x = (this.isNS && this.versionMajor == 4);
   this.isNS40x = (this.isNS4x && this.versionMinor < 4.5);
   this.isNS47x = (this.isNS4x && this.versionMinor >= 4.7);
   this.isNS4up = (this.isNS && this.versionMinor >= 4);
   this.isNS6x = (this.isNS && this.versionMajor == 6);
   this.isNS6up = (this.isNS && this.versionMajor >= 6);
   this.isNS7x = (this.isNS && this.versionMajor == 7);
   this.isNS7up = (this.isNS && this.versionMajor >= 7);

   this.isIE4x = (this.isIE && this.versionMajor == 4);
   this.isIE4up = (this.isIE && this.versionMajor >= 4);
   this.isIE5x = (this.isIE && this.versionMajor == 5);
   this.isIE55 = (this.isIE && this.versionMinor == 5.5);
   this.isIE5up = (this.isIE && this.versionMajor >= 5);
   this.isIE6x = (this.isIE && this.versionMajor == 6);
   this.isIE6up = (this.isIE && this.versionMajor >= 6);

   this.isIE4xMac = (this.isIE4x && this.isMac);
}

// Detect a given plugin name was not found.  The list of plugins is provided in comments below.
function detectPlugin(pluginName)
{
    //This script detects the following:
    //Flash
    //Acrobat Reader
    //SVG Viewer
    
    var agt=navigator.userAgent.toLowerCase();
    var ie  = (agt.indexOf("msie") != -1);
    var ns  = (navigator.appName.indexOf("Netscape") != -1);
    var win = ((agt.indexOf("win")!=-1) || (agt.indexOf("32bit")!=-1));
    var mac = (agt.indexOf("mac")!=-1);
    var pluginlist = "";
    if (mac)
        return true;

    if (ie && win) 
    {	
        //not sure the class id for SVG Viewer will increment by 1 for 
        //every future release greater than 3, but assume so given that it works
        //for version 2 and version 3.
        //not sure the class id for Acrobat Reader is the same for all future
        //versions greater than 7, cannot assume so given that version 7's class
        //id is completely different from its previous versions'
        //not sure the class id for Shockwave Flash will increment by 1 for 
        //every future release greater than 7, but assume so given that it works
        //for version 7 and version 8.
        pluginlist = 
            //Detect SVG Viewer 3 and above in IE
            detectSoftwareIE("Adobe.SVGCtl.","SVG Viewer", "3") +
            //Detect Flash 7 and above in IE
            detectSoftwareIE("ShockwaveFlash.ShockwaveFlash.","Shockwave Flash", "7") +
            //Detect Acrobat 7 in IE
            detectIE("AcroPDF.PDF.1","Acrobat Reader");     
            
    }
    if (ns || !win) 
    {
            nse = ""; 
            for (var i=0;i<navigator.mimeTypes.length;i++) 
                nse += navigator.mimeTypes[i].type.toLowerCase();
            pluginlist = 
                detectSoftwareNS("Adobe Acrobat","Acrobat Reader","7")+
                detectSoftwareNS("Shockwave Flash","Shockwave Flash","7") +
                detectSoftwareNS("Adobe SVG Viewer Plugin","SVG Viewer","3");
    }
   
    if(pluginlist.indexOf(pluginName) == - 1)
        return false;
    else
        return true;        
}

// Detect a plugin in IE.
function detectIE(ClassID,name)
{
    result = false;
    document.write('<SCR' + 'IPT LANGUAGE=VBScript>\n on error resume next \n result = IsObject(CreateObject("' + ClassID + '"))</SCR' + 'IPT>\n');
    if (result)
        return name+',';
    else
        return '';
}

// Detect a plugin in Netscape.
function detectNS(ClassID,name)
{
    n = "";
    if (nse.indexOf(ClassID) != -1)
        if (navigator.mimeTypes[ClassID].enabledPlugin != null)
            n = name+",";
    return n;
}

  // Detect a specific major version and up to 25 of a software plugin in IE
  function detectSoftwareIE(ClassID,name,version)
  {
    for(var i=version;i<=25;i++)
    {
        if(detectIE(ClassID+i,name) != '')
            return detectIE(ClassID+i,name);
    }
  }

  // Detect a specific major version and up to 25 of a software plugin in Netscape (Gecko)
 function detectSoftwareNS(name,returnVal, version)
 {
    var n = "";
    if (navigator.plugins != null && navigator.plugins.length > 0) {
      var plugin = navigator.plugins[name]; 
      if (typeof plugin == 'object') {
             for (i=25;i>=version;i--) {
                  if (plugin.description.indexOf(i+'.') != -1){ 
                           n = returnVal;
                  }
              }
              // If there is no version in the name, assume it is latest version (e.g Acrobat Reader 8).
              // Absence of a "." (dot) indicates no version is specified.
              if(plugin.description.indexOf('.') == -1)
                n = returnVal;
        }
      }
    return n;
  }  

 function detectJava() {
    if(!PluginDetect){var PluginDetect={getNum:function(A,_2){if(!this.num(A)){return null}var m;if(typeof _2=="undefined"){m=/[\d][\d\.\_,-]*/.exec(A)}else{m=(new RegExp(_2)).exec(A)}return m?m[0].replace(/[\.\_-]/g,","):null},hasMimeType:function(_4){var s,t,z,M=_4.constructor==String?[_4]:_4;for(z=0;z<M.length;z++){s=navigator.mimeTypes[M[z]];if(s&&s.enabledPlugin){t=s.enabledPlugin;if(t.name||t.description){return s}}}return null},findNavPlugin:function(N,_7){var _8=N.constructor==String?N:N.join(".*"),numS=_7===false?"":"\\d";var i,re=new RegExp(_8+".*"+numS+"|"+numS+".*"+_8,"i");var _a=navigator.plugins;for(i=0;i<_a.length;i++){if(re.test(_a[i].description)||re.test(_a[i].name)){return _a[i]}}return null},getAXO:function(_b){var _c,e;try{_c=new ActiveXObject(_b);return _c}catch(e){}return null},num:function(A){return (typeof A!="string"?false:(/\d/).test(A))},compareNums:function(_e,_f){if(!this.num(_e)||!this.num(_f)){return 0}if(this.plugin&&this.plugin.compareNums){return this.plugin.compareNums(_e,_f)}var m1=_e.split(","),m2=_f.split(","),x,p=parseInt;for(x=0;x<Math.min(m1.length,m2.length);x++){if(p(m1[x],10)>p(m2[x],10)){return 1}if(p(m1[x],10)<p(m2[x],10)){return -1}}return 0},formatNum:function(num){if(!this.num(num)){return null}var x,n=num.replace(/\s/g,"").replace(/[\.\_]/g,",").split(",").concat(["0","0","0","0"]);for(x=0;x<4;x++){if(/^(0+)(.+)$/.test(n[x])){n[x]=RegExp.$2}}return n[0]+","+n[1]+","+n[2]+","+n[3]},initScript:function(){var $=this,IE;$.isIE=(/*@cc_on!@*/false);$.IEver=-1;$.ActiveXEnabled=false;if($.isIE){IE=(/msie\s*\d\.{0,1}\d*/i).exec(navigator.userAgent);if(IE){$.IEver=parseFloat((/\d.{0,1}\d*/i).exec(IE[0]),10)}var _14,x;_14=["ShockwaveFlash.ShockwaveFlash","Msxml2.XMLHTTP","Microsoft.XMLDOM","Msxml2.DOMDocument","TDCCtl.TDCCtl","Shell.UIHelper","Scripting.Dictionary","wmplayer.ocx"];for(x=0;x<_14.length;x++){if($.getAXO(_14[x])){$.ActiveXEnabled=true;break}}}if($.isIE){$.head=typeof document.getElementsByTagName!="undefined"?document.getElementsByTagName("head")[0]:null}},init:function(_15){if(typeof _15!="string"){return -3}_15=_15.toLowerCase().replace(/\s/g,"");var $=this,IE,p;if(typeof $[_15]=="undefined"){return -3}p=$[_15];$.plugin=p;if(typeof p.installed=="undefined"){p.minversion={};p.installed=null;p.version=null;p.getVersionDone=null}$.garbage=false;if($.isIE&&!$.ActiveXEnabled){return -2}return 1},isMinVersion:function(_17,_18,_19){return -3},getVersion:function(_1d,_1e){var $=PluginDetect,i=$.init(_1d);if(i<0){return null}var p=$.plugin;if(typeof _1e=="undefined"){_1e=null}if(p.getVersionDone==null){p.getVersion(null,_1e);p.getVersionDone=1}$.cleanup();return p.version;return null},cleanup:function(){var $=this;if($.garbage&&typeof window.CollectGarbage!="undefined"){window.CollectGarbage()}},isActiveXObject:function(_22){var $=this,result,e,s="<object width=\"1\" height=\"1\" "+"style=\"display:none\" "+$.plugin.getCodeBaseVersion(_22)+">"+$.plugin.HTML+"</object>";if($.head.firstChild){$.head.insertBefore(document.createElement("object"),$.head.firstChild)}else{$.head.appendChild(document.createElement("object"))}$.head.firstChild.outerHTML=s;try{$.head.firstChild.classid=$.plugin.classID}catch(e){}result=false;try{if($.head.firstChild.object){result=true}}catch(e){}try{if(result&&$.head.firstChild.readyState<4){$.garbage=true}}catch(e){}$.head.removeChild($.head.firstChild);return result},codebaseSearch:function(min){var $=this;if(typeof min!="undefined"){return $.isActiveXObject(min)};var _26=[0,0,0,0],x,y,A=$.plugin.digits,t=function(x,y){var _29=(x==0?y:_26[0])+","+(x==1?y:_26[1])+","+(x==2?y:_26[2])+","+(x==3?y:_26[3]);return $.isActiveXObject(_29)};var _2a,tmp;var _2b=false;for(x=0;x<A.length;x++){_2a=A[x]*2;_26[x]=0;for(y=0;y<20;y++){if(_2a==1&&x>0&&_2b){break}if(_2a-_26[x]>1){tmp=Math.round((_2a+_26[x])/2);if(t(x,tmp)){_26[x]=tmp;_2b=true}else{_2a=tmp}}else{if(_2a-_26[x]==1){_2a--;if(!_2b&&t(x,_2a)){_2b=true}break}else{if(!_2b&&t(x,_2a)){_2b=true}break}}}if(!_2b){return null}}return _26.join(",")},dummy1:0}}PluginDetect.initScript();PluginDetect.java={mimeType:"application/x-java-applet",classID:"clsid:8AD9C840-044E-11D1-B3E9-00805F499D93",DTKclassID:"clsid:CAFEEFAC-DEC7-0000-0000-ABCDEFFEDCBA",DTKmimeType:"application/npruntime-scriptable-plugin;DeploymentToolkit",minWebStart:"1,4,2,0",JavaVersions:["1,9,1,25","1,8,1,25","1,7,1,25","1,6,1,25","1,5,0,25","1,4,2,25","1,3,1,25"],lowestPreApproved:"1,6,0,02",lowestSearchable:"1,3,1,0",searchAXOJavaPlugin:function(min,_34){var e,z,T,$=PluginDetect;var _36,C_DE,C,DE,v;var AXO=ActiveXObject;var _38=(typeof _34!="undefined")?_34:this.minWebStart;var Q=min.split(","),x;for(x=0;x<4;x++){Q[x]=parseInt(Q[x],10)}for(x=0;x<3;x++){if(Q[x]>9){Q[x]=9}}if(Q[3]>99){Q[3]=99}var _3a="JavaPlugin."+Q[0]+Q[1]+Q[2]+(Q[3]>0?("_"+(Q[3]<10?"0":"")+Q[3]):"");for(z=0;z<this.JavaVersions.length;z++){if($.compareNums(min,this.JavaVersions[z])>0){return null}T=this.JavaVersions[z].split(",");_36="JavaPlugin."+T[0]+T[1];v=T[0]+"."+T[1]+".";for(C=T[2];C>=0;C--){if($.compareNums(T[0]+","+T[1]+","+C+",0",_38)>=0){try{new AXO("JavaWebStart.isInstalled."+v+C+".0")}catch(e){continue}}if($.compareNums(min,T[0]+","+T[1]+","+C+","+T[3])>0){return null}for(DE=T[3];DE>=0;DE--){C_DE=C+"_"+(DE<10?"0"+DE:DE);try{new AXO(_36+C_DE);return v+C_DE}catch(e){}if(_36+C_DE==_3a){return null}}try{new AXO(_36+C);return v+C}catch(e){}if(_36+C==_3a){return null}}}return null},minIEver:7,HTML:"<param name=\"code\" value=\"A14999.class\" />",getCodeBaseVersion:function(v){var r=v.replace(/[\.\_]/g,",").split(","),$=PluginDetect;if($.compareNums(v,"1,4,1,02")<0){v=r[0]+","+r[1]+","+r[2]+","+r[3]}else{if($.compareNums(v,"1,5,0,02")<0){v=r[0]+","+r[1]+","+r[2]+","+r[3]+"0"}else{v=Math.round((parseFloat(r[0]+"."+r[1],10)-1.5)*10+5)+","+r[2]+","+r[3]+"0"+",0"}}return "codebase=\"#version="+v+"\""},digits:[2,8,8,32],getFromMimeType:function(_3d){var x,t,$=PluginDetect;var re=new RegExp(_3d);var tmp,v="0,0,0,0",digits="";for(x=0;x<navigator.mimeTypes.length;x++){t=navigator.mimeTypes[x];if(re.test(t.type)&&t.enabledPlugin){t=t.type.substring(t.type.indexOf("=")+1,t.type.length);tmp=$.formatNum(t);if($.compareNums(tmp,v)>0){v=tmp;digits=t}}}return digits.replace(/[\.\_]/g,",")},hasRun:false,value:null,queryJavaHandler:function(){var $=PluginDetect.java,j=window.java,e;$.hasRun=true;try{if(typeof j.lang!="undefined"&&typeof j.lang.System!="undefined"){$.value=j.lang.System.getProperty("java.version")+" "}}catch(e){}},queryJava:function(){var $=PluginDetect,t=this,nua=navigator.userAgent,e;if(typeof window.java!="undefined"&&window.navigator.javaEnabled()){if(/gecko/i.test(nua)){if($.hasMimeType("application/x-java-vm")){try{var div=document.createElement("div"),evObj=document.createEvent("HTMLEvents");evObj.initEvent("focus",false,true);div.addEventListener("focus",t.queryJavaHandler,false);div.dispatchEvent(evObj)}catch(e){}if(!t.hasRun){t.queryJavaHandler()}}}else{if(/opera.9\.(0|1)/i.test(nua)&&/mac/i.test(nua)){return null}t.queryJavaHandler()}}return t.value},getVersion:function(min,jar){if(typeof min=="undefined"){min=null}if(typeof jar=="undefined"){jar=null}var _46=null,$=PluginDetect;var dtk=this.queryDeploymentToolKit();if(dtk==-1&&$.isIE){this.installed=-1;return}if(dtk!=-1&&dtk!=null){_46=dtk}if(!$.isIE){var p1,p2,p,tmp;var _49,mt;mt=$.hasMimeType(this.mimeType);_49=(mt&&navigator.javaEnabled());if(!_46&&_49){tmp="Java[^\\d]*Plug-in";p=$.findNavPlugin(tmp);if(p){tmp=new RegExp(tmp,"i");p1=tmp.test(p.description)?$.getNum(p.description):null;p2=tmp.test(p.name)?$.getNum(p.name):null;if(p1&&p2){_46=($.compareNums($.formatNum(p1),$.formatNum(p2))>=0)?p1:p2}else{_46=p1||p2}}}if(!_46&&(_49||(mt&&/linux/i.test(navigator.userAgent)&&$.findNavPlugin("IcedTea.*Java",false)))){tmp=this.getFromMimeType("application/x-java-applet.*jpi-version.*=");if(tmp!=""){_46=tmp}}if(!_46&&_49&&/macintosh.*safari/i.test(navigator.userAgent)){p=$.findNavPlugin("Java.*\\d.*Plug-in.*Cocoa",false);if(p){p1=$.getNum(p.description);if(p1){_46=p1}}}if(!_46){p=this.queryJava();if(p){_46=p}}if(!_46&&mt){p=this.queryExternalApplet(jar);if(p[0]){_46=p[0]}}if(!_46&&_49&&!/macintosh.*ppc/i.test(navigator.userAgent)){tmp=this.getFromMimeType("application/x-java-applet.*version.*=");if(tmp!=""){_46=tmp}}this.installed=_46?1:-1;if(!_46&&_49){if(/safari/i.test(navigator.userAgent)){this.installed=0}}}else{var Q;if(!_46){if($.IEver>=this.minIEver){Q=this.findMax(this.lowestPreApproved,min);_46=this.searchAXOJavaPlugin(Q,this.lowestPreApproved)}else{Q=this.findMax(this.lowestSearchable,min);_46=this.searchAXOJavaPlugin(Q)}}if(!_46){this.JavaFix()}if(!_46){tmp=this.queryExternalApplet(jar);if(tmp[0]){_46=tmp[0]}}if(!_46&&$.IEver>=this.minIEver){if(min==null){_46=$.codebaseSearch()}else{this.minversion["a"+min]=$.codebaseSearch(min)?1:-1;return}}this.installed=_46?1:-1}this.setVersion(_46)},findMax:function(_4b,_4c){var $=PluginDetect;if(typeof _4c=="undefined"||_4c==null||$.compareNums(_4c,_4b)<0){return _4b}return _4c},setVersion:function(_4e){var $=PluginDetect;this.version=$.formatNum($.getNum(_4e));if(typeof this.version=="string"&&this.allVersions.length==0){this.allVersions[0]=this.version}},allVersions:[],queryDeploymentToolKit:function(){if(typeof this.queryDTKresult!="undefined"){return this.queryDTKresult}this.allVersions=[];var $=PluginDetect,e,x;var _51=[null,null],obj;var len=null;if($.isIE&&$.IEver>=6){_51=$.instantiate("object","","")}if(!$.isIE&&$.hasMimeType(this.DTKmimeType)){_51=$.instantiate("object","type="+this.DTKmimeType,"")}if(_51[0]&&_51[1]&&_51[1].parentNode){obj=_51[0].firstChild;if($.isIE&&$.IEver>=6){try{obj.classid=this.DTKclassID}catch(e){}try{if(obj.object&&obj.readyState<4){$.garbage=true}}catch(e){}}try{len=obj.jvms.getLength();if(len!=null&&len>0){for(x=0;x<len;x++){this.allVersions[x]=$.formatNum($.getNum(obj.jvms.get(x).version))}}}catch(e){}_51[1].parentNode.removeChild(_51[1])}this.queryDTKresult=this.allVersions.length>0?this.allVersions[this.allVersions.length-1]:(len==0?-1:null);return this.queryDTKresult},queryExternalApplet:function(jar){if(!jar||typeof jar!="string"){return [null,null]}if(typeof this.queryExternalAppletResult!="undefined"){return this.queryExternalAppletResult}var $=PluginDetect,e,version=null,vendor=null,obj;var _55;var par="<param name=\"archive\" value=\""+jar+"\" />"+"<param name=\"mayscript\" value=\"true\" />"+"<param name=\"scriptable\" value=\"true\" />";var _57=function(_58){var obj,e;if(_58[0]&&_58[1]&&_58[1].parentNode){obj=_58[0].firstChild;try{if($.isIE&&obj.object&&obj.readyState<4){$.garbage=true}}catch(e){}try{version=obj.getVersion()+" ";vendor=obj.getVendor()+" "}catch(e){}_58[1].parentNode.removeChild(_58[1])}};if($.isIE){_55=$.instantiate("object","archive=\""+jar+"\" code=\"A.class\" type=\""+this.mimeType+"\"","<param name=\"code\" value=\"A.class\" />"+par)}else{_55=$.instantiate("object","archive=\""+jar+"\" classid=\"java:A.class\" type=\""+this.mimeType+"\"",par)}_57(_55);if(!version){_55=$.instantiate("applet","archive=\""+jar+"\" code=\"A.class\" mayscript=\"true\"","<param name=\"mayscript\" value=\"true\">");_57(_55)}this.queryExternalAppletResult=[version,vendor];return this.queryExternalAppletResult},JavaFix:function(){var $=PluginDetect;if($.isIE&&window.history&&window.history.length==0&&window.location&&(/^file/).test(window.location.href)){var _5b=$.instantiate("object","codebase=\"#version=99,99,99,99\" classid=\""+this.classID+"\"",this.HTML);if(_5b[1]&&_5b[1].parentNode){_5b[1].parentNode.removeChild(_5b[1])}}}};PluginDetect.instantiate=function(_63,_64,_65){var e,d=document,tag1="<"+_63+" width=\"1\" height=\"1\" "+_64+">"+_65+"</"+_63+">",body=(d.getElementsByTagName("body")[0]||d.body),div=d.createElement("div");if(body){body.appendChild(div)}else{try{d.write("<div>o</div><div>"+tag1+"</div>");body=(d.getElementsByTagName("body")[0]||d.body);body.removeChild(body.firstChild);div=body.firstChild}catch(e){try{body=d.createElement("body");d.getElementsByTagName("html")[0].appendChild(body);body.appendChild(div);div.innerHTML=tag1;return [div,body]}catch(e){}}return [div,div]}if(div&&div.parentNode){try{div.innerHTML=tag1}catch(e){}}return [div,div]};
    result = false;
    var version = PluginDetect.getVersion('Java');
    if (version) {
        var majversion = version.split(',')[1];
        var minversion = version.split(',')[3];
        if (majversion >= 6 && minversion >= 10) {
            var date = new Date();
            date.setTime(date.getTime()+(1*24*60*60*1000));
            var expires = "; expires="+date.toGMTString();
            var ck = "JavaWebStart6Enabled=Y"+expires+"; path=/";
            document.cookie = ck;
            result = true;
        }
    }    
    if (!result)
        return 'JavaWebStart.isInstalled';
    else return '';  
 }


 function isEmpty(str) {
      var spaces = " \n\r\t";
      if (str==null || str=="" || str.length==0) return true;

      for (i = 0; i < str.length; i++)
      {
        if (spaces.indexOf(str.charAt(i)) == -1) return false;
      }

      return true;
 }
 function show(id) {
	 //setting the radioflt variable 
	 var obj = document.getElementById(id);
	    if (obj!=null && obj.style!=null) obj.style.display = "block";
 }

 function showCalibration(id) {
	 //setting the radioflt variable 
	 var obj = document.getElementById(id);
	    if (obj!=null && obj.style!=null) obj.style.display = "block";
	 var searchcriteria=id.substring(id.length-3,id.length);
	
	var searchname =getNetuiTagName('searchCriteria');
     document.forms['searchCalibration'].elements[searchname].value=searchcriteria;
     
     document.getElementById(searchcriteria).style.backgroundColor="#1d4587"; 
     document.getElementById(searchcriteria).style.color="white";
     
   
 }

 function hideCalibration(id) {
	 var obj = document.getElementById(id);
	    if (obj!=null && obj.style!=null) 
	    	obj.style.display = "none";
	    
	 var searchcriteria=id.substring(id.length-3,id.length);
	 document.getElementById(searchcriteria).style.backgroundColor="#F2F2F2"; 
     document.getElementById(searchcriteria).style.color="black";
	
 }
 function hide(id) {
	 var obj = document.getElementById(id);
	 obj.focus();
	    if (obj!=null && obj.style!=null) 
	    	obj.style.display = "none";
 }


// Function that pops up a window of a specific size on all target browsers
//    Pass the window URL, the width and the height
function popWindow(urlVal,windowName,widthVal,heightVal,scrollBars,menuBar,reSizeable,toolBar) {
    var paraString
    var wt
    var ht

    // Bug fix: we are now blanking the windowName variable
    windowName == "";

    wt = widthVal;
    ht = heightVal;

    var winl = (screen.width - wt) / 2;
    var wint = (screen.height - ht) / 2;
        
    paraString = "width=" + wt + ",height=" + ht + ",top=" + wint + ",left="+ winl +",toolbar=yes";
    if (scrollBars == 1) {
        paraString = paraString + ",scrollbars=yes";
    } else {
        paraString = paraString + ",scrollbars=no";
    }
    if (menuBar == 1) {
        paraString = paraString + ",menubar=yes";
    }
    if (reSizeable == 1) {
        paraString = paraString + ",resizable=yes";
    }
    if (toolBar == 1) {
        paraString = paraString + ",toolBar=yes";
    } else {
        paraString = paraString + ",toolBar=no";
    }
    
    
    // Ticket# 6896 - calls the openWindow method in singlelevelmenu.jsp
    if("brioReports"==windowName){
    openWindow(urlVal,windowName,paraString);
    }
    else{
    poppedWindow = window.open(urlVal,windowName,paraString);
    poppedWindow.focus();
    }
    
}

//Changes for Bluetooth
// Function that pops up a window of a specific size on all target browsers
//    Pass the window URL, the width and the height and statusBar
function popBTWindow(urlVal,windowName,widthVal,heightVal,scrollBars,menuBar,reSizeable,toolBar,statusBar) {   
    

    var paraString
    var wt
    var ht

    // Bug fix: we are now blanking the windowName variable
    windowName == "";

    wt = widthVal;
    ht = heightVal;

    var winl = (screen.width - wt) / 2;
    var wint = (screen.height - ht) / 2;
        
    paraString = "width=" + wt + ",height=" + ht + ",top=" + wint + ",left="+ winl +",toolbar=yes";
    if (scrollBars == 1) {
        paraString = paraString + ",scrollbars=yes";
    } else {
        paraString = paraString + ",scrollbars=no";
    }
    if (menuBar == 1) {
        paraString = paraString + ",menubar=yes";
    }
    if (reSizeable == 1) {
        paraString = paraString + ",resizable=yes";
    }
    if (toolBar == 1) {
        paraString = paraString + ",toolBar=yes";
    } else {
        paraString = paraString + ",toolBar=no";
    }
    if (statusBar == 1) {
        paraString = paraString + ",status=yes";
    }else{
        paraString = paraString + ",status=no";
    }

    
    // Ticket# 6896 - calls the openWindow method in singlelevelmenu.jsp
    if("brioReports"==windowName){
    openWindow(urlVal,windowName,paraString);
    }
    else{
    poppedWindow = window.open(urlVal,windowName,paraString);
    poppedWindow.focus();
    }
    
}

function popRssFeedWindow(urlVal,windowName,widthVal,heightVal,scrollBars,menuBar,reSizeable,toolBar,statusBar,resizable) {   
    

    var paraString
    var wt
    var ht

    // Bug fix: we are now blanking the windowName variable
    windowName == "";

    wt = widthVal;
    ht = heightVal;

    var winl = 300;
    var wint = 350;
        
    paraString = "width=" + wt + ",height=" + ht + ",top=" + wint + ",left="+ winl +",toolbar=no";
    if (scrollBars == 1) {
        paraString = paraString + ",scrollbars=yes";
    } else {
        paraString = paraString + ",scrollbars=no";
    }
    if (menuBar == 1) {
        paraString = paraString + ",menubar=yes";
    }
    if (reSizeable == 1) {
        paraString = paraString + ",resizable=yes";
    }
    if (toolBar == 1) {
        paraString = paraString + ",toolBar=yes";
    } else {
        paraString = paraString + ",toolBar=no";
    }
    if (statusBar == 1) {
        paraString = paraString + ",status=yes";
    }else{
        paraString = paraString + ",status=no";
    }
    if (resizable == 1) {
        paraString = paraString + ",resizable=yes";
    }else{
        paraString = paraString + ",resizable=no";
    }
    
    poppedWindow = window.open(urlVal,windowName,paraString);
    poppedWindow.focus();
    
}

// Function used to display internal TC cases on a separate popup
function popTcViewer(urlVal, number) {
    popWindow(urlVal,"tcViewer"+number,740,550,1,1,1);
}

// Function used to display brio reports sites on a separate popup
function popBrioReports(urlVal) {
    popWindow(urlVal,"brioReports",900,700,1,1,1);
}

// Function used to display webtop sites on a separate popup
function popWebtop(urlVal) {
    popWindow(urlVal,"WebtopPopup",1024,768,1,1,1);
}

// Function used to display CC Mail functionality
function popMailTo(urlVal) {
    popWindow(urlVal, "MailTo", 400, 285, 1,1,1);
}

// Deprecated.  Please see if this should be used anymore.
function goToCrumb(crumbName) {
    alert(crumbName);
    window.location = '#' + crumbName;
}

// Validates vin function
// See: http://www.fastcustom.com/content/view/18/1/
function is_valid_vin(vin)
{
    var check_digit='', check_digit_value=0, sum=0;
    var has_invalid_characters=0;
    var check_digit_position=8;

    var letter_values = "0=0,1=1,2=2,3=3,4=4,5=5,6=6,7=7,8=8,9=9,A=1,B=2,C=3,D=4,E=5,F=6,G=7,H=8,J=1,K=2,L=3,M=4,N=5,O=6,P=7,R=9,S=2,T=3,U=4,V=5,W=6,X=7,Y=8,Z=9".split(",");

    var digit_weights = "8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2".split(",");

    if(vin.length !=17 ){
        return false;
    }

    for(i=0 ; i<= 16 ; i++){

        digit=vin.substring(i,i+1).toUpperCase();
        if (i==check_digit_position){
            check_digit=digit;
        } else {
            var digit_value=-1;
            for(j=0;j<=letter_values.length-1;j++){
                if(letter_values[j].split("=")[0]==digit){
                    digit_value=
                    (parseInt(letter_values[j].split("=")[1])*
                    parseInt(digit_weights[i]));
                }

            }

            sum+= digit_value;
            if(digit_value==-1){
                return false;
            }
        }
    }

    if(check_digit=='X'){
        check_digit_value=10
    } else {
        check_digit_value=parseInt(check_digit) ;
    }



    if((sum % 11) != check_digit_value){
        return false;
    }

    return true;

}

// Used by function is_valid_vin(vin)
function get_vin_year(vin)
{
    year_digit = vin.substring(9,10);
    if (year_digit == 'A') {

        year = '1980';

    } else if (year_digit == 'B') {

        year = '1981';

    } else if (year_digit == 'C') {

        year = '1982';

    } else if (year_digit == 'D') {

        year = '1983';

    } else if (year_digit == 'E') {

        year = '1984';

    } else if (year_digit == 'F') {

        year = '1985';

    } else if (year_digit == 'G') {

        year = '1986';

    } else if (year_digit == 'H') {

        year = '1987';

    } else if (year_digit == 'I') {

        year = '';

    } else if (year_digit == 'J') {

        year = '1988';

    } else if (year_digit == 'K') {

        year = '1989';

    } else if (year_digit == 'L') {

        year = '1990';

    } else if (year_digit == 'M') {

        year = '1991';

    } else if (year_digit == 'N') {

        year = '1992';

    } else if (year_digit == 'O') {

        year = '';

    } else if (year_digit == 'P') {

        year = '1993';

    } else if (year_digit == 'Q') {

        year = '';

    } else if (year_digit == 'R') {

        year = '1994';

    } else if (year_digit == 'S') {

        year = "1995";

    } else if (year_digit == 'T') {

        year = "1996";

    } else if (year_digit == 'V') {

        year = "1997";

    } else if (year_digit == 'W') {

        year = "1998";

    } else if (year_digit == 'X') {

        year = "1999";

    } else if (year_digit == 'Y') {

        year = "2000";

    } else if (year_digit == '1') {

        year = "2001";

    } else if (year_digit == '2') {

        year = "2002";

    } else if (year_digit == '3') {

        year = "2003 ";

    } else if (year_digit == '4') {

        year = "2004";

    } else if (year_digit == '5') {

        year = "2005";

    } else if (year_digit == '6') {

        year = "2006";

    } else if (year_digit == '7') {

        year = "2007";

    } else if (year_digit == '8') {

        year = "2008";

    } else if (year_digit == '9') {

        year = "2009";

    } else {

        year = "";
    }

    return(year);
}

// Used by function is_valid_vin(vin)
function get_vin_make(vin)
{
    make_digit=vin.substring(1,2).toUpperCase();
    if (make_digit=='0') {
        make='Cadillac';
    } else if (make_digit=='6') {
        make='Articat';
    } else if (make_digit=='7') {
        make='Honda';
    } else if (make_digit=='9') {
        make='Acura';
    } else if (make_digit=='A') {
        make='Audi';
    } else if (make_digit=='B') {
        make='BMW';
    } else if (make_digit=='C') {
        make='Chrysler';
    } else if (make_digit=='D') {
        make='Ducati';
    } else if (make_digit=='F') {
        make='Ford';
    } else if (make_digit=='G') {
        make='Chevrolet';
    } else if (make_digit=='H') {
        make='Honda';
    } else if (make_digit=='J') {
        make='Jeep';
    } else if (make_digit=='K') {
        make='Kawasaki';
    } else if (make_digit=='L') {
        make='Lincoln';
    } else if (make_digit=='M') {
        make='Buell';
    } else if (make_digit=='N') {
        make='Nissan';
    } else if (make_digit=='P') {
        make='Porsche';
    } else if (make_digit=='R') {
        make='Red Horse';
    } else if (make_digit=='S') {
        make='Suzuki';
    } else if (make_digit=='T') {
        make='Toyota';
    } else if (make_digit=='U') {
        make='BMW';
    } else if (make_digit=='V') {
        make='Volkswagen';
    } else if (make_digit=='X') {
        make='Polaris';
    } else if (make_digit=='Y') {
        make='Yamaha';
    } else if (make_digit=='Z') {
        make='Bombardier';
    }
    return(make);
}

function jstl_vinTab1(vinBox, textBox1, textBox2, textBox3, event) {
    if (vinBox.value.length > 3) {
    	textBox2.focus();
        textBox2.value = vinBox.value.substr(3,5);
        if (vinBox.value.length > 8) {
            textBox3.focus();
            textBox3.value = vinBox.value.substr(8,9);
        } else {
            textBox2.focus();
            textBox2.value = vinBox.value.substr(3,5);
        }
        textBox1.value = vinBox.value.substr(0,3);
    } else if (vinBox.value.length == 0 && getKeyCode(event) == 9) {
        textBox1.focus();
    }
}

function jstl_vinTab2(vinBox, textBox1, textBox2, textBox3, event) {

    if (vinBox.value.length > 16) {
        textBox1.value = vinBox.value.substr(0,17);
        jstl_vinTab1(textBox1, textBox1, textBox2, textBox3, event);
    } else {
        if (vinBox.value.length > 5) {
            textBox3.focus();
            textBox3.value = vinBox.value.substr(5,9);
            textBox2.value = vinBox.value.substr(0,5);
        }
    }
    if (vinBox.value.length == 0) {
        if ((getKeyCode(event) == 9) || (event.shiftKey && getKeyCode(event) ==9) || (getKeyCode(event) == 16)) {
            textBox2.focus();
        } else {
            textBox1.focus();
            textBox1.value = textBox1.value;
        }
    }
}

function jstl_vinTab3(vinBox, textBox1, textBox2, textBox3, event) {
    if (vinBox.value.length > 16) {
        textBox1.value = vinBox.value.substr(0,17);
        jstl_vinTab1(textBox1, textBox1, textBox2, textBox3, event);
    } else {
        if (vinBox.value.length > 9) {
            textBox3.focus();
            textBox3.value = vinBox.value.substr(0,9);
        }
    }

    if (vinBox.value.length == 0) {
        if (getKeyCode(event) == 9) {
            textBox3.focus();
        } 
    }
}

/* SOURCE FILE: AnchorPosition.js */
function getAnchorPosition(anchorname){var useWindow=false;var coordinates=new Object();var x=0,y=0;var use_gebi=false, use_css=false, use_layers=false;if(document.getElementById){use_gebi=true;}else if(document.all){use_css=true;}else if(document.layers){use_layers=true;}if(use_gebi && document.all){x=AnchorPosition_getPageOffsetLeft(document.all[anchorname]);y=AnchorPosition_getPageOffsetTop(document.all[anchorname]);}else if(use_gebi){var o=document.getElementById(anchorname);x=AnchorPosition_getPageOffsetLeft(o);y=AnchorPosition_getPageOffsetTop(o);}else if(use_css){x=AnchorPosition_getPageOffsetLeft(document.all[anchorname]);y=AnchorPosition_getPageOffsetTop(document.all[anchorname]);}else if(use_layers){var found=0;for(var i=0;i<document.anchors.length;i++){if(document.anchors[i].name==anchorname){found=1;break;}}if(found==0){coordinates.x=0;coordinates.y=0;return coordinates;}x=document.anchors[i].x;y=document.anchors[i].y;}else{coordinates.x=0;coordinates.y=0;return coordinates;}coordinates.x=x;coordinates.y=y;return coordinates;}
function getAnchorWindowPosition(anchorname){var coordinates=getAnchorPosition(anchorname);var x=0;var y=0;if(document.getElementById){if(isNaN(window.screenX)){x=coordinates.x-document.body.scrollLeft+window.screenLeft;y=coordinates.y-document.body.scrollTop+window.screenTop;}else{x=coordinates.x+window.screenX+(window.outerWidth-window.innerWidth)-window.pageXOffset;y=coordinates.y+window.screenY+(window.outerHeight-24-window.innerHeight)-window.pageYOffset;}}else if(document.all){x=coordinates.x-document.body.scrollLeft+window.screenLeft;y=coordinates.y-document.body.scrollTop+window.screenTop;}else if(document.layers){x=coordinates.x+window.screenX+(window.outerWidth-window.innerWidth)-window.pageXOffset;y=coordinates.y+window.screenY+(window.outerHeight-24-window.innerHeight)-window.pageYOffset;}coordinates.x=x;coordinates.y=y;return coordinates;}
function AnchorPosition_getPageOffsetLeft(el){var ol=el.offsetLeft;while((el=el.offsetParent) != null){ol += el.offsetLeft;}return ol;}
function AnchorPosition_getWindowOffsetLeft(el){return AnchorPosition_getPageOffsetLeft(el)-document.body.scrollLeft;}
function AnchorPosition_getPageOffsetTop(el){var ot=el.offsetTop;while((el=el.offsetParent) != null){ot += el.offsetTop;}return ot;}
function AnchorPosition_getWindowOffsetTop(el){return AnchorPosition_getPageOffsetTop(el)-document.body.scrollTop;}

/* SOURCE FILE: date.js */
var MONTH_NAMES=new Array('January','February','March','April','May','June','July','August','September','October','November','December','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');var DAY_NAMES=new Array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sun','Mon','Tue','Wed','Thu','Fri','Sat');
function LZ(x){return(x<0||x>9?"":"0")+x}
function isDate(val,format){var date=getDateFromFormat(val,format);if(date==0){return false;}return true;}
function compareDates(date1,dateformat1,date2,dateformat2){var d1=getDateFromFormat(date1,dateformat1);var d2=getDateFromFormat(date2,dateformat2);if(d1==0 || d2==0){return -1;}else if(d1 > d2){return 1;}return 0;}
function formatDate(date,format){format=format+"";var result="";var i_format=0;var c="";var token="";var y=date.getYear()+"";var M=date.getMonth()+1;var d=date.getDate();var E=date.getDay();var H=date.getHours();var m=date.getMinutes();var s=date.getSeconds();var yyyy,yy,MMM,MM,dd,hh,h,mm,ss,ampm,HH,H,KK,K,kk,k;var value=new Object();if(y.length < 4){y=""+(y-0+1900);}value["y"]=""+y;value["yyyy"]=y;value["yy"]=y.substring(2,4);value["M"]=M;value["MM"]=LZ(M);value["MMM"]=MONTH_NAMES[M-1];value["NNN"]=MONTH_NAMES[M+11];value["d"]=d;value["dd"]=LZ(d);value["E"]=DAY_NAMES[E+7];value["EE"]=DAY_NAMES[E];value["H"]=H;value["HH"]=LZ(H);if(H==0){value["h"]=12;}else if(H>12){value["h"]=H-12;}else{value["h"]=H;}value["hh"]=LZ(value["h"]);if(H>11){value["K"]=H-12;}else{value["K"]=H;}value["k"]=H+1;value["KK"]=LZ(value["K"]);value["kk"]=LZ(value["k"]);if(H > 11){value["a"]="PM";}else{value["a"]="AM";}value["m"]=m;value["mm"]=LZ(m);value["s"]=s;value["ss"]=LZ(s);while(i_format < format.length){c=format.charAt(i_format);token="";while((format.charAt(i_format)==c) &&(i_format < format.length)){token += format.charAt(i_format++);}if(value[token] != null){result=result + value[token];}else{result=result + token;}}return result;}
function _isInteger(val){var digits="1234567890";for(var i=0;i < val.length;i++){if(digits.indexOf(val.charAt(i))==-1){return false;}}return true;}
function _getInt(str,i,minlength,maxlength){for(var x=maxlength;x>=minlength;x--){var token=str.substring(i,i+x);if(token.length < minlength){return null;}if(_isInteger(token)){return token;}}return null;}
function getDateFromFormat(val,format){val=val+"";format=format+"";var i_val=0;var i_format=0;var c="";var token="";var token2="";var x,y;var now=new Date();var year=now.getYear();var month=now.getMonth()+1;var date=1;var hh=now.getHours();var mm=now.getMinutes();var ss=now.getSeconds();var ampm="";while(i_format < format.length){c=format.charAt(i_format);token="";while((format.charAt(i_format)==c) &&(i_format < format.length)){token += format.charAt(i_format++);}if(token=="yyyy" || token=="yy" || token=="y"){if(token=="yyyy"){x=4;y=4;}if(token=="yy"){x=2;y=2;}if(token=="y"){x=2;y=4;}year=_getInt(val,i_val,x,y);if(year==null){return 0;}i_val += year.length;if(year.length==2){if(year > 70){year=1900+(year-0);}else{year=2000+(year-0);}}}else if(token=="MMM"||token=="NNN"){month=0;for(var i=0;i<MONTH_NAMES.length;i++){var month_name=MONTH_NAMES[i];if(val.substring(i_val,i_val+month_name.length).toLowerCase()==month_name.toLowerCase()){if(token=="MMM"||(token=="NNN"&&i>11)){month=i+1;if(month>12){month -= 12;}i_val += month_name.length;break;}}}if((month < 1)||(month>12)){return 0;}}else if(token=="EE"||token=="E"){for(var i=0;i<DAY_NAMES.length;i++){var day_name=DAY_NAMES[i];if(val.substring(i_val,i_val+day_name.length).toLowerCase()==day_name.toLowerCase()){i_val += day_name.length;break;}}}else if(token=="MM"||token=="M"){month=_getInt(val,i_val,token.length,2);if(month==null||(month<1)||(month>12)){return 0;}i_val+=month.length;}else if(token=="dd"||token=="d"){date=_getInt(val,i_val,token.length,2);if(date==null||(date<1)||(date>31)){return 0;}i_val+=date.length;}else if(token=="hh"||token=="h"){hh=_getInt(val,i_val,token.length,2);if(hh==null||(hh<1)||(hh>12)){return 0;}i_val+=hh.length;}else if(token=="HH"||token=="H"){hh=_getInt(val,i_val,token.length,2);if(hh==null||(hh<0)||(hh>23)){return 0;}i_val+=hh.length;}else if(token=="KK"||token=="K"){hh=_getInt(val,i_val,token.length,2);if(hh==null||(hh<0)||(hh>11)){return 0;}i_val+=hh.length;}else if(token=="kk"||token=="k"){hh=_getInt(val,i_val,token.length,2);if(hh==null||(hh<1)||(hh>24)){return 0;}i_val+=hh.length;hh--;}else if(token=="mm"||token=="m"){mm=_getInt(val,i_val,token.length,2);if(mm==null||(mm<0)||(mm>59)){return 0;}i_val+=mm.length;}else if(token=="ss"||token=="s"){ss=_getInt(val,i_val,token.length,2);if(ss==null||(ss<0)||(ss>59)){return 0;}i_val+=ss.length;}else if(token=="a"){if(val.substring(i_val,i_val+2).toLowerCase()=="am"){ampm="AM";}else if(val.substring(i_val,i_val+2).toLowerCase()=="pm"){ampm="PM";}else{return 0;}i_val+=2;}else{if(val.substring(i_val,i_val+token.length)!=token){return 0;}else{i_val+=token.length;}}}if(i_val != val.length){return 0;}if(month==2){if( ((year%4==0)&&(year%100 != 0) ) ||(year%400==0) ){if(date > 29){return 0;}}else{if(date > 28){return 0;}}}if((month==4)||(month==6)||(month==9)||(month==11)){if(date > 30){return 0;}}if(hh<12 && ampm=="PM"){hh=hh-0+12;}else if(hh>11 && ampm=="AM"){hh-=12;}var newdate=new Date(year,month-1,date,hh,mm,ss);return newdate.getTime();}
function parseDate(val){var preferEuro=(arguments.length==2)?arguments[1]:false;generalFormats=new Array('y-M-d','MMM d, y','MMM d,y','y-MMM-d','d-MMM-y','MMM d');monthFirst=new Array('M/d/y','M-d-y','M.d.y','MMM-d','M/d','M-d');dateFirst =new Array('d/M/y','d-M-y','d.M.y','d-MMM','d/M','d-M');var checkList=new Array('generalFormats',preferEuro?'dateFirst':'monthFirst',preferEuro?'monthFirst':'dateFirst');var d=null;for(var i=0;i<checkList.length;i++){var l=window[checkList[i]];for(var j=0;j<l.length;j++){d=getDateFromFormat(val,l[j]);if(d!=0){return new Date(d);}}}return null;}

/* SOURCE FILE: PopupWindow.js */
function PopupWindow_getXYPosition(anchorname){var coordinates;if(this.type == "WINDOW"){coordinates = getAnchorWindowPosition(anchorname);}else{coordinates = getAnchorPosition(anchorname);}this.x = coordinates.x+75;this.y = coordinates.y-10;}
function PopupWindow_setSize(width,height){this.width = width;this.height = height;}
function PopupWindow_populate(contents){this.contents = contents;this.populated = false;}
function PopupWindow_setUrl(url){this.url = url;}
function PopupWindow_setWindowProperties(props){this.windowProperties = props;}
function PopupWindow_refresh(){if(this.divName != null){if(this.use_gebi){document.getElementById(this.divName).innerHTML = this.contents;}else if(this.use_css){document.all[this.divName].innerHTML = this.contents;}else if(this.use_layers){var d = document.layers[this.divName];d.document.open();d.document.writeln(this.contents);d.document.close();}}else{if(this.popupWindow != null && !this.popupWindow.closed){if(this.url!=""){this.popupWindow.location.href=this.url;}else{this.popupWindow.document.open();this.popupWindow.document.writeln(this.contents);this.popupWindow.document.close();}this.popupWindow.focus();}}}
function PopupWindow_showPopup(anchorname){this.getXYPosition(anchorname);this.x += this.offsetX;this.y += this.offsetY;if(!this.populated &&(this.contents != "")){this.populated = true;this.refresh();}if(this.divName != null){if(this.use_gebi){document.getElementById(this.divName).style.left = this.x + "px";document.getElementById(this.divName).style.top = this.y + "px";document.getElementById(this.divName).style.visibility = "visible";}else if(this.use_css){document.all[this.divName].style.left = this.x;document.all[this.divName].style.top = this.y;document.all[this.divName].style.visibility = "visible";}else if(this.use_layers){document.layers[this.divName].left = this.x;document.layers[this.divName].top = this.y;document.layers[this.divName].visibility = "visible";}}else{if(this.popupWindow == null || this.popupWindow.closed){if(this.x<0){this.x=0;}if(this.y<0){this.y=0;}if(screen && screen.availHeight){if((this.y + this.height) > screen.availHeight){this.y = screen.availHeight - this.height;}}if(screen && screen.availWidth){if((this.x + this.width) > screen.availWidth){this.x = screen.availWidth - this.width;}}var avoidAboutBlank = window.opera ||( document.layers && !navigator.mimeTypes['*']) || navigator.vendor == 'KDE' ||( document.childNodes && !document.all && !navigator.taintEnabled);this.popupWindow = window.open(avoidAboutBlank?"":"about:blank","window_"+anchorname,this.windowProperties+",width="+this.width+",height="+this.height+",screenX="+this.x+",left="+this.x+",screenY="+this.y+",top="+this.y+"");}this.refresh();}}
function PopupWindow_hidePopup(){if(this.divName != null){if(this.use_gebi){document.getElementById(this.divName).style.visibility = "hidden";}else if(this.use_css){document.all[this.divName].style.visibility = "hidden";}else if(this.use_layers){document.layers[this.divName].visibility = "hidden";}}else{if(this.popupWindow && !this.popupWindow.closed){this.popupWindow.close();this.popupWindow = null;}}}
function PopupWindow_isClicked(e){if(this.divName != null){if(this.use_layers){var clickX = e.pageX;var clickY = e.pageY;var t = document.layers[this.divName];if((clickX > t.left) &&(clickX < t.left+t.clip.width) &&(clickY > t.top) &&(clickY < t.top+t.clip.height)){return true;}else{return false;}}else if(document.all){var t = window.event.srcElement;while(t.parentElement != null){if(t.id==this.divName){return true;}t = t.parentElement;}return false;}else if(this.use_gebi && e){var t = e.originalTarget;while(t.parentNode != null){if(t.id==this.divName){return true;}t = t.parentNode;}return false;}return false;}return false;}
function PopupWindow_hideIfNotClicked(e){if(this.autoHideEnabled && !this.isClicked(e)){this.hidePopup();}}
function PopupWindow_autoHide(){this.autoHideEnabled = true;}
function PopupWindow_hidePopupWindows(e){for(var i=0;i<popupWindowObjects.length;i++){if(popupWindowObjects[i] != null){var p = popupWindowObjects[i];p.hideIfNotClicked(e);}}}
function PopupWindow_attachListener(){if(document.layers){document.captureEvents(Event.MOUSEUP);}window.popupWindowOldEventListener = document.onmouseup;if(window.popupWindowOldEventListener != null){document.onmouseup = new Function("window.popupWindowOldEventListener();PopupWindow_hidePopupWindows();");}else{document.onmouseup = PopupWindow_hidePopupWindows;}}
function PopupWindow(){if(!window.popupWindowIndex){window.popupWindowIndex = 0;}if(!window.popupWindowObjects){window.popupWindowObjects = new Array();}if(!window.listenerAttached){window.listenerAttached = true;PopupWindow_attachListener();}this.index = popupWindowIndex++;popupWindowObjects[this.index] = this;this.divName = null;this.popupWindow = null;this.width=0;this.height=0;this.populated = false;this.visible = false;this.autoHideEnabled = false;this.contents = "";this.url="";this.windowProperties="toolbar=no,location=no,status=no,menubar=no,scrollbars=auto,resizable,alwaysRaised,dependent,titlebar=no";if(arguments.length>0){this.type="DIV";this.divName = arguments[0];}else{this.type="WINDOW";}this.use_gebi = false;this.use_css = false;this.use_layers = false;if(document.getElementById){this.use_gebi = true;}else if(document.all){this.use_css = true;}else if(document.layers){this.use_layers = true;}else{this.type = "WINDOW";}this.offsetX = 0;this.offsetY = 0;this.getXYPosition = PopupWindow_getXYPosition;this.populate = PopupWindow_populate;this.setUrl = PopupWindow_setUrl;this.setWindowProperties = PopupWindow_setWindowProperties;this.refresh = PopupWindow_refresh;this.showPopup = PopupWindow_showPopup;this.hidePopup = PopupWindow_hidePopup;this.setSize = PopupWindow_setSize;this.isClicked = PopupWindow_isClicked;this.autoHide = PopupWindow_autoHide;this.hideIfNotClicked = PopupWindow_hideIfNotClicked;}


/* SOURCE FILE: CalendarPopup.js */

function CalendarPopup(){var c;if(arguments.length>0){c = new PopupWindow(arguments[0]);}else{c = new PopupWindow();c.setSize(150,175);}c.offsetX = -152;c.offsetY = 25;c.autoHide();c.monthNames = new Array("January","February","March","April","May","June","July","August","September","October","November","December");c.monthAbbreviations = new Array("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");c.dayHeaders = new Array("S","M","T","W","T","F","S");c.returnFunction = "CP_tmpReturnFunction";c.returnMonthFunction = "CP_tmpReturnMonthFunction";c.returnQuarterFunction = "CP_tmpReturnQuarterFunction";c.returnYearFunction = "CP_tmpReturnYearFunction";c.weekStartDay = 0;c.isShowYearNavigation = false;c.displayType = "date";c.disabledWeekDays = new Object();c.disabledDatesExpression = "";c.yearSelectStartOffset = 2;c.currentDate = null;c.todayText="Today";c.cssPrefix="";c.isShowNavigationDropdowns=false;c.isShowYearNavigationInput=false;window.CP_calendarObject = null;window.CP_targetInput = null;window.CP_dateFormat = "MM/dd/yyyy";c.copyMonthNamesToWindow = CP_copyMonthNamesToWindow;c.setReturnFunction = CP_setReturnFunction;c.setReturnMonthFunction = CP_setReturnMonthFunction;c.setReturnQuarterFunction = CP_setReturnQuarterFunction;c.setReturnYearFunction = CP_setReturnYearFunction;c.setMonthNames = CP_setMonthNames;c.setMonthAbbreviations = CP_setMonthAbbreviations;c.setDayHeaders = CP_setDayHeaders;c.setWeekStartDay = CP_setWeekStartDay;c.setDisplayType = CP_setDisplayType;c.setDisabledWeekDays = CP_setDisabledWeekDays;c.addDisabledDates = CP_addDisabledDates;c.setYearSelectStartOffset = CP_setYearSelectStartOffset;c.setTodayText = CP_setTodayText;c.showYearNavigation = CP_showYearNavigation;c.showCalendar = CP_showCalendar;c.hideCalendar = CP_hideCalendar;c.getStyles = getCalendarStyles;c.refreshCalendar = CP_refreshCalendar;c.getCalendar = CP_getCalendar;c.select = CP_select;c.setCssPrefix = CP_setCssPrefix;c.showNavigationDropdowns = CP_showNavigationDropdowns;c.showYearNavigationInput = CP_showYearNavigationInput;c.copyMonthNamesToWindow();return c;}
function CP_copyMonthNamesToWindow(){if(typeof(window.MONTH_NAMES)!="undefined" && window.MONTH_NAMES!=null){window.MONTH_NAMES = new Array();for(var i=0;i<this.monthNames.length;i++){window.MONTH_NAMES[window.MONTH_NAMES.length] = this.monthNames[i];}for(var i=0;i<this.monthAbbreviations.length;i++){window.MONTH_NAMES[window.MONTH_NAMES.length] = this.monthAbbreviations[i];}}}
function CP_tmpReturnFunction(y,m,d){if(window.CP_targetInput!=null){var dt = new Date(y,m-1,d,0,0,0);if(window.CP_calendarObject!=null){window.CP_calendarObject.copyMonthNamesToWindow();}window.CP_targetInput.value = formatDate(dt,window.CP_dateFormat);}else{alert('Use setReturnFunction() to define which function will get the clicked results!');}}
function CP_tmpReturnMonthFunction(y,m){alert('Use setReturnMonthFunction() to define which function will get the clicked results!\nYou clicked: year='+y+' , month='+m);}
function CP_tmpReturnQuarterFunction(y,q){alert('Use setReturnQuarterFunction() to define which function will get the clicked results!\nYou clicked: year='+y+' , quarter='+q);}
function CP_tmpReturnYearFunction(y){alert('Use setReturnYearFunction() to define which function will get the clicked results!\nYou clicked: year='+y);}
function CP_setReturnFunction(name){this.returnFunction = name;}
function CP_setReturnMonthFunction(name){this.returnMonthFunction = name;}
function CP_setReturnQuarterFunction(name){this.returnQuarterFunction = name;}
function CP_setReturnYearFunction(name){this.returnYearFunction = name;}
function CP_setMonthNames(){for(var i=0;i<arguments.length;i++){this.monthNames[i] = arguments[i];}this.copyMonthNamesToWindow();}
function CP_setMonthAbbreviations(){for(var i=0;i<arguments.length;i++){this.monthAbbreviations[i] = arguments[i];}this.copyMonthNamesToWindow();}
function CP_setDayHeaders(){for(var i=0;i<arguments.length;i++){this.dayHeaders[i] = arguments[i];}}
function CP_setWeekStartDay(day){this.weekStartDay = day;}
function CP_showYearNavigation(){this.isShowYearNavigation =(arguments.length>0)?arguments[0]:true;}
function CP_setDisplayType(type){if(type!="date"&&type!="week-end"&&type!="month"&&type!="quarter"&&type!="year"){alert("Invalid display type! Must be one of: date,week-end,month,quarter,year");return false;}this.displayType=type;}
function CP_setYearSelectStartOffset(num){this.yearSelectStartOffset=num;}
function CP_setDisabledWeekDays(){this.disabledWeekDays = new Object();for(var i=0;i<arguments.length;i++){this.disabledWeekDays[arguments[i]] = true;}}
function CP_addDisabledDates(start, end){if(arguments.length==1){end=start;}if(start==null && end==null){return;}if(this.disabledDatesExpression!=""){this.disabledDatesExpression+= "||";}if(start!=null){start = parseDate(start);start=""+start.getFullYear()+LZ(start.getMonth()+1)+LZ(start.getDate());}if(end!=null){end=parseDate(end);end=""+end.getFullYear()+LZ(end.getMonth()+1)+LZ(end.getDate());}if(start==null){this.disabledDatesExpression+="(ds<="+end+")";}else if(end  ==null){this.disabledDatesExpression+="(ds>="+start+")";}else{this.disabledDatesExpression+="(ds>="+start+"&&ds<="+end+")";}}
function CP_setTodayText(text){this.todayText = text;}
function CP_setCssPrefix(val){this.cssPrefix = val;}
function CP_showNavigationDropdowns(){this.isShowNavigationDropdowns =(arguments.length>0)?arguments[0]:true;}
function CP_showYearNavigationInput(){this.isShowYearNavigationInput =(arguments.length>0)?arguments[0]:true;}
function CP_hideCalendar(){if(arguments.length > 0){window.popupWindowObjects[arguments[0]].hidePopup();}else{this.hidePopup();}}
function CP_refreshCalendar(index){var calObject = window.popupWindowObjects[index];if(arguments.length>1){calObject.populate(calObject.getCalendar(arguments[1],arguments[2],arguments[3],arguments[4],arguments[5]));}else{calObject.populate(calObject.getCalendar());}calObject.refresh();}
function CP_showCalendar(anchorname){if(arguments.length>1){if(arguments[1]==null||arguments[1]==""){this.currentDate=new Date();}else{this.currentDate=new Date(parseDate(arguments[1]));}}this.populate(this.getCalendar());this.showPopup(anchorname);}
function CP_select(inputobj, linkname, format){var selectedDate=(arguments.length>3)?arguments[3]:null;if(!window.getDateFromFormat){alert("calendar.select: To use this method you must also include 'date.js' for date formatting");return;}if(this.displayType!="date"&&this.displayType!="week-end"){alert("calendar.select: This function can only be used with displayType 'date' or 'week-end'");return;}if(inputobj.type!="text" && inputobj.type!="hidden" && inputobj.type!="textarea"){alert("calendar.select: Input object passed is not a valid form input object");window.CP_targetInput=null;return;}if(inputobj.disabled){return;}window.CP_targetInput = inputobj;window.CP_calendarObject = this;this.currentDate=null;var time=0;if(selectedDate!=null){time = getDateFromFormat(selectedDate,format)}else if(inputobj.value!=""){time = getDateFromFormat(inputobj.value,format);}if(selectedDate!=null || inputobj.value!=""){if(time==0){this.currentDate=null;}else{this.currentDate=new Date(time);}}window.CP_dateFormat = format;this.showCalendar(linkname);}
function getCalendarStyles(){var result = "";var p = "";if(this!=null && typeof(this.cssPrefix)!="undefined" && this.cssPrefix!=null && this.cssPrefix!=""){p=this.cssPrefix;}result += "<STYLE>\n";result += "."+p+"cpYearNavigation,."+p+"cpMonthNavigation{background-color:#C0C0C0;text-align:center;vertical-align:center;text-decoration:none;color:#000000;font-weight:bold;}\n";result += "."+p+"cpDayColumnHeader, ."+p+"cpYearNavigation,."+p+"cpMonthNavigation,."+p+"cpCurrentMonthDate,."+p+"cpCurrentMonthDateDisabled,."+p+"cpOtherMonthDate,."+p+"cpOtherMonthDateDisabled,."+p+"cpCurrentDate,."+p+"cpCurrentDateDisabled,."+p+"cpTodayText,."+p+"cpTodayTextDisabled,."+p+"cpText{font-family:arial;font-size:8pt;}\n";result += "TD."+p+"cpDayColumnHeader{text-align:right;border:solid thin #C0C0C0;border-width:0px 0px 1px 0px;}\n";result += "."+p+"cpCurrentMonthDate, ."+p+"cpOtherMonthDate, ."+p+"cpCurrentDate{text-align:right;text-decoration:none;}\n";result += "."+p+"cpCurrentMonthDateDisabled, ."+p+"cpOtherMonthDateDisabled, ."+p+"cpCurrentDateDisabled{color:#D0D0D0;text-align:right;text-decoration:line-through;}\n";result += "."+p+"cpCurrentMonthDate, .cpCurrentDate{color:#000000;}\n";result += "."+p+"cpOtherMonthDate{color:#808080;}\n";result += "TD."+p+"cpCurrentDate{color:white;background-color: #C0C0C0;border-width:1px;border:solid thin #800000;}\n";result += "TD."+p+"cpCurrentDateDisabled{border-width:1px;border:solid thin #FFAAAA;}\n";result += "TD."+p+"cpTodayText, TD."+p+"cpTodayTextDisabled{border:solid thin #C0C0C0;border-width:1px 0px 0px 0px;}\n";result += "A."+p+"cpTodayText, SPAN."+p+"cpTodayTextDisabled{height:20px;}\n";result += "A."+p+"cpTodayText{color:black;}\n";result += "."+p+"cpTodayTextDisabled{color:#D0D0D0;}\n";result += "."+p+"cpBorder{border:solid thin #808080;}\n";result += "</STYLE>\n";return result;}
function CP_getCalendar(){var now = new Date();if(this.type == "WINDOW"){var windowref = "window.opener.";}else{var windowref = "";}var result = "";if(this.type == "WINDOW"){result += "<HTML><HEAD><TITLE>Calendar</TITLE>"+this.getStyles()+"</HEAD><BODY style='margin:0;'>\n";result += '<div class="center-align"><TABLE style="width:100%;" BORDER=0 BORDERWIDTH=0 CELLSPACING=0 CELLPADDING=0>\n';}else{result += '<TABLE CLASS="'+this.cssPrefix+'cpBorder" WIDTH=144 BORDER=1 BORDERWIDTH=1 CELLSPACING=0 CELLPADDING=1>\n';result += '<TR><TD ALIGN=CENTER>\n';result += '<div class="center-align">\n';}if(this.displayType=="date" || this.displayType=="week-end"){if(this.currentDate==null){this.currentDate = now;}if(arguments.length > 0){var month = arguments[0];}else{var month = this.currentDate.getMonth()+1;}if(arguments.length > 1 && arguments[1]>0 && arguments[1]-0==arguments[1]){var year = arguments[1];}else{var year = this.currentDate.getFullYear();}var daysinmonth= new Array(0,31,28,31,30,31,30,31,31,30,31,30,31);if( ((year%4 == 0)&&(year%100 != 0) ) ||(year%400 == 0) ){daysinmonth[2] = 29;}var current_month = new Date(year,month-1,1);var display_year = year;var display_month = month;var display_date = 1;var weekday= current_month.getDay();var offset = 0;offset =(weekday >= this.weekStartDay) ? weekday-this.weekStartDay : 7-this.weekStartDay+weekday ;if(offset > 0){display_month--;if(display_month < 1){display_month = 12;display_year--;}display_date = daysinmonth[display_month]-offset+1;}var next_month = month+1;var next_month_year = year;if(next_month > 12){next_month=1;next_month_year++;}var last_month = month-1;var last_month_year = year;if(last_month < 1){last_month=12;last_month_year--;}var date_class;if(this.type!="WINDOW"){result += "<TABLE WIDTH=144 BORDER=0 BORDERWIDTH=0 CELLSPACING=0 CELLPADDING=0>";}result += '<TR>\n';var refresh = windowref+'CP_refreshCalendar';var refreshLink = 'javascript:' + refresh;if(this.isShowNavigationDropdowns){result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:78px" COLSPAN="3"><select CLASS="'+this.cssPrefix+'cpMonthNavigation" name="cpMonth" onChange="'+refresh+'('+this.index+',this.options[this.selectedIndex].value-0,'+(year-0)+');">';for( var monthCounter=1;monthCounter<=12;monthCounter++){var selected =(monthCounter==month) ? 'SELECTED' : '';result += '<option value="'+monthCounter+'" '+selected+'>'+this.monthNames[monthCounter-1]+'</option>';}result += '</select></TD>';result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:10px;">&nbsp;</TD>';result += '<TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:56px" COLSPAN="3"><select CLASS="'+this.cssPrefix+'cpYearNavigation" name="cpYear" onChange="'+refresh+'('+this.index+','+month+',this.options[this.selectedIndex].value-0);">';for( var yearCounter=year-this.yearSelectStartOffset;yearCounter<=year+this.yearSelectStartOffset;yearCounter++){var selected =(yearCounter==year) ? 'SELECTED' : '';result += '<option value="'+yearCounter+'" '+selected+'>'+yearCounter+'</option>';}result += '</select></TD>';}else{if(this.isShowYearNavigation){result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:10px;"><A CLASS="'+this.cssPrefix+'cpMonthNavigation" HREF="'+refreshLink+'('+this.index+','+last_month+','+last_month_year+');">&lt;</A></TD>';result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:58px"><SPAN CLASS="'+this.cssPrefix+'cpMonthNavigation">'+this.monthNames[month-1]+'</SPAN></TD>';result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:10px;"><A CLASS="'+this.cssPrefix+'cpMonthNavigation" HREF="'+refreshLink+'('+this.index+','+next_month+','+next_month_year+');">&gt;</A></TD>';result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:10px;">&nbsp;</TD>';result += '<TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:10px;"><A CLASS="'+this.cssPrefix+'cpYearNavigation" HREF="'+refreshLink+'('+this.index+','+month+','+(year-1)+');">&lt;</A></TD>';if(this.isShowYearNavigationInput){result += '<TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:36px;"><INPUT NAME="cpYear" CLASS="'+this.cssPrefix+'cpYearNavigation" SIZE="4" MAXLENGTH="4" VALUE="'+year+'" onBlur="'+refresh+'('+this.index+','+month+',this.value-0);"></TD>';}else{result += '<TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:36px"><SPAN CLASS="'+this.cssPrefix+'cpYearNavigation">'+year+'</SPAN></TD>';}result += '<TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:10px;"><A CLASS="'+this.cssPrefix+'cpYearNavigation" HREF="'+refreshLink+'('+this.index+','+month+','+(year+1)+');">&gt;</A></TD>';}else{result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:22px"><A CLASS="'+this.cssPrefix+'cpMonthNavigation" HREF="'+refreshLink+'('+this.index+','+last_month+','+last_month_year+');">&lt;&lt;</A></TD>\n';result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:100px; "><SPAN CLASS="'+this.cssPrefix+'cpMonthNavigation">'+this.monthNames[month-1]+' '+year+'</SPAN></TD>\n';result += '<TD CLASS="'+this.cssPrefix+'cpMonthNavigation" style="width:22px"><A CLASS="'+this.cssPrefix+'cpMonthNavigation" HREF="'+refreshLink+'('+this.index+','+next_month+','+next_month_year+');">&gt;&gt;</A></TD>\n';}}result += '</TR></TABLE>\n';result += '<TABLE WIDTH=120 BORDER=0 CELLSPACING=0 CELLPADDING=1 ALIGN=CENTER>\n';result += '<TR>\n';for(var j=0;j<7;j++){result += '<TD CLASS="'+this.cssPrefix+'cpDayColumnHeader" style="width:14%;"><SPAN CLASS="'+this.cssPrefix+'cpDayColumnHeader">'+this.dayHeaders[(this.weekStartDay+j)%7]+'</TD>\n';}result += '</TR>\n';for(var row=1;row<=6;row++){result += '<TR>\n';for(var col=1;col<=7;col++){var disabled=false;if(this.disabledDatesExpression!=""){var ds=""+display_year+LZ(display_month)+LZ(display_date);eval("disabled=("+this.disabledDatesExpression+")");}var dateClass = "";if((display_month == this.currentDate.getMonth()+1) &&(display_date==this.currentDate.getDate()) &&(display_year==this.currentDate.getFullYear())){dateClass = "cpCurrentDate";}else if(display_month == month){dateClass = "cpCurrentMonthDate";}else{dateClass = "cpOtherMonthDate";}if(disabled || this.disabledWeekDays[col-1]){result += '   <TD CLASS="'+this.cssPrefix+dateClass+'"><SPAN CLASS="'+this.cssPrefix+dateClass+'Disabled">'+display_date+'</SPAN></TD>\n';}else{var selected_date = display_date;var selected_month = display_month;var selected_year = display_year;if(this.displayType=="week-end"){var d = new Date(selected_year,selected_month-1,selected_date,0,0,0,0);d.setDate(d.getDate() +(7-col));selected_year = d.getYear();if(selected_year < 1000){selected_year += 1900;}selected_month = d.getMonth()+1;selected_date = d.getDate();}result += ' <TD CLASS="'+this.cssPrefix+dateClass+'"><A HREF="javascript:'+windowref+this.returnFunction+'('+selected_year+','+selected_month+','+selected_date+');'+windowref+'CP_hideCalendar(\''+this.index+'\');" CLASS="'+this.cssPrefix+dateClass+'">'+display_date+'</A></TD>\n';}display_date++;if(display_date > daysinmonth[display_month]){display_date=1;display_month++;}if(display_month > 12){display_month=1;display_year++;}}result += '</TR>';}var current_weekday = now.getDay() - this.weekStartDay;if(current_weekday < 0){current_weekday += 7;}result += '<TR>\n';result += '    <TD COLSPAN=7 ALIGN=CENTER CLASS="'+this.cssPrefix+'cpTodayText">\n';if(this.disabledDatesExpression!=""){var ds=""+now.getFullYear()+LZ(now.getMonth()+1)+LZ(now.getDate());eval("disabled=("+this.disabledDatesExpression+")");}if(disabled || this.disabledWeekDays[current_weekday+1]){result += '      <SPAN CLASS="'+this.cssPrefix+'cpTodayTextDisabled">'+this.todayText+'</SPAN>\n';}else{result += '      <A CLASS="'+this.cssPrefix+'cpTodayText" HREF="javascript:'+windowref+this.returnFunction+'(\''+now.getFullYear()+'\',\''+(now.getMonth()+1)+'\',\''+now.getDate()+'\');'+windowref+'CP_hideCalendar(\''+this.index+'\');">'+this.todayText+'</A>\n';}result += '       <BR>\n';result += ' </TD></TR></TABLE></div></TD></TR></TABLE>\n';}if(this.displayType=="month" || this.displayType=="quarter" || this.displayType=="year"){if(arguments.length > 0){var year = arguments[0];}else{if(this.displayType=="year"){var year = now.getFullYear()-this.yearSelectStartOffset;}else{var year = now.getFullYear();}}if(this.displayType!="year" && this.isShowYearNavigation){result += "<TABLE WIDTH=144 BORDER=0 BORDERWIDTH=0 CELLSPACING=0 CELLPADDING=0>";result += '<TR>\n';result += '   <TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:22px"><A CLASS="'+this.cssPrefix+'cpYearNavigation" HREF="javascript:'+windowref+'CP_refreshCalendar('+this.index+','+(year-1)+');">&lt;&lt;</A></TD>\n';result += '    <TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:100px;">'+year+'</TD>\n';result += ' <TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="width:22px"><A CLASS="'+this.cssPrefix+'cpYearNavigation" HREF="javascript:'+windowref+'CP_refreshCalendar('+this.index+','+(year+1)+');">&gt;&gt;</A></TD>\n';result += '</TR></TABLE>\n';}}if(this.displayType=="month"){result += '<TABLE WIDTH=120 BORDER=0 CELLSPACING=1 CELLPADDING=0 ALIGN=CENTER>\n';for(var i=0;i<4;i++){result += '<TR>';for(var j=0;j<3;j++){var monthindex =((i*3)+j);result += '<TD WIDTH=33% ALIGN=CENTER><A CLASS="'+this.cssPrefix+'cpText" HREF="javascript:'+windowref+this.returnMonthFunction+'('+year+','+(monthindex+1)+');'+windowref+'CP_hideCalendar(\''+this.index+'\');" CLASS="'+date_class+'">'+this.monthAbbreviations[monthindex]+'</A></TD>';}result += '</TR>';}result += '</TABLE></div></TD></TR></TABLE>\n';}if(this.displayType=="quarter"){result += '<BR><TABLE WIDTH=120 BORDER=1 CELLSPACING=0 CELLPADDING=0 ALIGN=CENTER>\n';for(var i=0;i<2;i++){result += '<TR>';for(var j=0;j<2;j++){var quarter =((i*2)+j+1);result += '<TD style="width:50%;" ALIGN=CENTER><BR><A CLASS="'+this.cssPrefix+'cpText" HREF="javascript:'+windowref+this.returnQuarterFunction+'('+year+','+quarter+');'+windowref+'CP_hideCalendar(\''+this.index+'\');" CLASS="'+date_class+'">Q'+quarter+'</A><BR><BR></TD>';}result += '</TR>';}result += '</TABLE></div></TD></TR></TABLE>\n';}if(this.displayType=="year"){var yearColumnSize = 4;result += "<TABLE WIDTH=144 BORDER=0 BORDERWIDTH=0 CELLSPACING=0 CELLPADDING=0>";result += '<TR>\n';result += '   <TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="WIDTH:50%"><A CLASS="'+this.cssPrefix+'cpYearNavigation" HREF="javascript:'+windowref+'CP_refreshCalendar('+this.index+','+(year-(yearColumnSize*2))+');">&lt;&lt;</A></TD>\n';result += '  <TD CLASS="'+this.cssPrefix+'cpYearNavigation" style="WIDTH:50%"><A CLASS="'+this.cssPrefix+'cpYearNavigation" HREF="javascript:'+windowref+'CP_refreshCalendar('+this.index+','+(year+(yearColumnSize*2))+');">&gt;&gt;</A></TD>\n';result += '</TR></TABLE>\n';result += '<TABLE WIDTH=120 BORDER=0 CELLSPACING=1 CELLPADDING=0 ALIGN=CENTER>\n';for(var i=0;i<yearColumnSize;i++){for(var j=0;j<2;j++){var currentyear = year+(j*yearColumnSize)+i;result += '<TD style="width:50%;" ALIGN=CENTER><A CLASS="'+this.cssPrefix+'cpText" HREF="javascript:'+windowref+this.returnYearFunction+'('+currentyear+');'+windowref+'CP_hideCalendar(\''+this.index+'\');" CLASS="'+date_class+'">'+currentyear+'</A></TD>';}result += '</TR>';}result += '</TABLE></div></TD></TR></TABLE>\n';}if(this.type == "WINDOW"){result += "</BODY></HTML>\n";}return result;}


// ********************************************************************** //
//                     JAVASCRIPT VALIDATION FRAMEWORK                    //
// ********************************************************************** //
function getNetuiElement(tagId)
{
    return document.getElementById(getNetuiTagName(tagId));

}

function getNetuiElement(tagId,form)
{
    return document.getElementsByName(getNetuiTagName(tagId,form));
}

function validateWithHighlight(validationObject)
{
    validateWithHighlight(validationObject, null);
}

function validateWithHighlight(validationObject,presentationClass)
{
    var valid = validate(validationObject);
    var targetElement = document.getElementById(validationObject.label);

    if(!valid)
    {
        if(presentationClass != null) {
            targetElement.className = presentationClass;
        } else {
            targetElement.className = 'portlet-msg-error';
        }
    }
    else
    {
        targetElement.className = '';
    }

    return valid;
}

function validate(validationObject)
{
    // Check to see if the field is required
    if(validationObject.required == true)
    {
        if(isEmpty(validationObject.value))
            return false;
        else if(validationObject.value == "netui_null") // netui_null is radio button null value
            return false;
    }
    else if(isEmpty(validationObject.value))
    {
        return true;
    }

    // Check Minimum Length
    if(validationObject.value.length < validationObject.minlength)
        return false;

    // Check Maximum Length
    if(validationObject.value.length > validationObject.maxlength)
        return false;

    // Check Integer Type
    if(validationObject.type == 'integer')
    {
        if(isNaN(validationObject.value) || Math.floor(validationObject.value) != validationObject.value )
            return false;
    }

    // Check Alpha Numeric Type
    else if(validationObject.type == 'alphanumeric')
    {
        var alphanumericRegex = /\w+/;
        if(validationObject.value.match(alphanumericRegex) != validationObject.value)
            return false;
    }

    // Check VIN Type
    else if(validationObject.type == 'vin')
    {
        if(!is_valid_vin(validationObject.value))
            return false;
    }

    // Check Email Type
    else if(validationObject.type == 'email')
    {
        var emailRegex = /^\w[\.\-\w]*@\w[\.\-\w]*\.\w+$/;
        if(!validationObject.value.match(emailRegex))
            return false;
    }

    // Check Phone Type
    else if(validationObject.type == 'phone')
    {
        var phoneRegex = /^\d{3}-\d{3}-\d{4}$/;
        if(!validationObject.value.match(phoneRegex))
            return false;
    }
    
    else if(validationObject.type == 'feedbackphone')
    {
        var phoneRegex = /^\(?([0-9]{3})\)?[-.\/ \\]?([0-9]{3})[-.\/\\ ]?([0-9]{4})$/;
        if(!validationObject.value.match(phoneRegex))
            return false;
    }

    // Check Phone Type
   
    else if(validationObject.type == 't3Phone')
    {
    	 //Release 15.06 - T300019177 enhancement changes start
    	var phoneRegex      = /^[\(]{0,}\d{3}[-,\)]{1}[\s]?\d{3}[-]{1}\d{4}[\s]{0,}[-,x,]{1}\d{1,}$/;
        var phoneRegexNoExt = /^[\(]?\d{3}[-,\)]{1}[\s]?\d{3}[-]{1}\d{4}$/;
        //Release 15.06 - T300019177 enhancement changes end

        var pattern = phoneRegexNoExt;
        if(validationObject.value.length > 14) {
            pattern = phoneRegex;
        }

        if(!validationObject.value.match(pattern)) {
            return false;
        } else {
            return true;
        }
    }

    // Check calibration id type
    else if(validationObject.type == 'calibration')
    {
        //R6.4 T300010193 - Start
        // cal id is 5 or 8 or 12 chars long
        //if(validationObject.value.length != 5  && validationObject.value.length != 8  &&  validationObject.value.length != 12) {
         //   return false;
        //}
        //R6.4 T300010193 - End
        // cal id is alphanumeric
        //R6.9 T300011553 - Start
    	 var calRegex = /^([0-9]|[A-Z]|[a-z]|[.]|[_]|[-]|[\]]|[\[])+$/;
         //R6.9 T300011553 - End
             //validation for allowing [,],- 
 		 if(!validationObject.value.match(calRegex))
             return false;
    }

    // Check VDS Type
    else if(validationObject.type == 'VDS')
    {
        // vds is 5 chars long
        if(validationObject.value.length != 5) {
            return false;
        }
        // vds is alphanumeric
        var vdsRegex = /^([0-9]|[A-Z]|[a-z])+$/;
        if(!validationObject.value.match(vdsRegex))
            return false;
    }

    // Check Repair Date
    else if(validationObject.type == 'RepairDate')
    {
        return checkdate(validationObject.value,'B');
    }
    
    // Check Regular Date
    else if(validationObject.type == 'RegularDate')
    {
        return checkdate(validationObject.value,'Y');
    }
    
    else if(validationObject.type == 'Attachment') {
        return
    }
    
    return true;
}
// ********************************************************************** //

/**--------------------------
//* Validate Date Field script- By JavaScriptKit.com
//* For this script and 100s more, visit http://www.javascriptkit.com
//* This notice must stay intact for usage
---------------------------**/
//Modified to add range checking
function checkdate(value,range){
    //Basic check for format validity
    var validformat=/^\d{2}\/\d{2}\/\d{4}$/ 
    var returnval=false;
    if (!validformat.test(value)) {
        returnval=false;
    }else{ 
        //Detailed check for valid date ranges
        var monthfield=value.split("/")[0]
        var dayfield=value.split("/")[1]
        var yearfield=value.split("/")[2]
        var dayobj = new Date(yearfield, monthfield-1, dayfield)
        if ((dayobj.getMonth()+1!=monthfield)||(dayobj.getDate()!=dayfield)||(dayobj.getFullYear()!=yearfield))
            returnval=false;
        else
            returnval=true;
        if(returnval && range != null)
        {
            var now = new Date();
            var today = new Date(now.getFullYear(),now.getMonth(),now.getDate());
           //Any time
            if(range == 'Y') {
                returnval = true;
            //After today (including today)
            } else if(range == 'A') {
                if(dayobj >= today)
                    returnval = true;
                else
                    returnval = false;
            //Before today (including today)
            } else if(range == 'B') {
                if(dayobj <= today)
                    returnval = true;   
                else
                    returnval = false;        
            }
        }
    }
    return returnval;
}

function setAllOptionsToSelected( selectBox )
{
    var optionList = selectBox.options;
    var i;
    
    for ( i = 0; i < optionList.length; i++ )
    {
        optionList[ i ].selected=true;
    }
}

function removeAllOptions(selectBox)
{
    var i;
    for(i=selectBox.options.length-1;i>=0;i--)
    {
        selectBox.remove(i);
    }
}

// DTC Validation rules:
// #1 - Set all letters to CAP only
// #2 - Do not allow letters O or I
// #3 - Upon entry of 6th digit, automatically enter a / into the string (e.g., P0A41/245)
// #4 - Expand the size of each DTC to accomodate 9 characters
/*function validateDTC(dtc)
{
	//R 8.6.1 - T30017299 - Start

        var newDtcFlag = 0;
        var keyMatch = 'false';
        
    var formval;

        formval = dtc.value;
        formval = formval.toUpperCase(); // Convert to Uppercase
        formval = formval.replace(/O+/gi, '');  // Erase all O 
        //formval = formval.replace(/_+/g, '');  //Erase Underscore
    formval = formval.replace(/\W+/g, ''); // Erase all non-alphanumeric
        if(formval.charAt(formval.length-1) == '_')
        {
             formval = formval.substring(0,formval.length-1);
        }
    if(formval.charAt(0) == 'I')
        {
        formval = formval.replace(/I+/gi, '');
        }

        dtc.value = formval;
              
        var frstLetter = formval.charAt(0);
        var success = 'false';
        var keyFound = -1;

        if(dtcFormatsMap != null && dtcFormatsMap.hasOwnProperty(frstLetter))
        {
            //alert(frstLetter);
            var scndLetter = formval.charAt(1);
        //var fourthLetter = formval.charAt(3);
            //Getting the Second & fourth Character and Performing the checks
        if(scndLetter != "" && !isNaN(scndLetter))
            {
            formval = formval.replace(/I+/gi, '');                
                //alert("inside check");
                var value = dtcFormatsMap[frstLetter];
                var dtcFormatvalues = value.split("~");
                var preChar = dtcFormatvalues[0];
                var symbol = dtcFormatvalues[1];
                var postChar = dtcFormatvalues[2];
                if(preChar != 0 )
                {
                if(formval.length > preChar)
    			{
                    formval = formval.substr(0, preChar) + symbol + formval.substr(preChar, postChar);
                    dtc.value = formval;
                }
              
                
                if(formval.length == preChar || formval.length == parseInt(preChar) + 1 + parseInt(postChar))
                {
                    //alert("No Error found in length : normal");
                    success = 'true';
                }
                }
                else
                {
                newDtcFlag = 1;
                }
            }
            else if (scndLetter != "")
            {
                newDtcFlag = 1;
            }
        }
        else 
        {
              newDtcFlag = 1;
    }    
            if(newDtcFlag == 1 && dtcFormatsMap != null)
            {
                for (key in dtcFormatsMap)
                {
                    keyFound = formval.search(key);
                    if(keyFound != -1)
                    { 
                        var value = dtcFormatsMap[key];
                        var dtcFormatvalues = value.split("~");
                        var preChar = dtcFormatvalues[0];
                        var symbol = dtcFormatvalues[1];
                        var postChar = dtcFormatvalues[2];
    
                            if(preChar == 0)
                            {
                                if(formval.length > key.length)
                                     { 
                                        if(key == formval.substring(0, key.length))
                                        {
                                            formval = formval.replace(symbol,'');
                                 
                                 if(formval.substring(0, key.length) == "DI")
                                 {
                                     var val = formval.substring(key.length, formval.length);
                                     val = val.replace(/I+/gi, '');
                                     formval = formval.substring(0, key.length) + val;
                                 }
                                 else
                                 {
                                     formval = formval.replace(/I+/gi, ''); 
                                 }
                                            formval = formval.replace(/_+/g, '');  //Erase Underscore
                                            formval = formval.replace(/\W+/g, ''); // Erase all non-alphanumeric
                                 if(formval == "DI")
                                 {
                                     formval = key;
                                 }
                                 else
                                 {
                                            formval = key + symbol + formval.substr(key.length, postChar); 
                                 }
                                            dtc.value = formval;
                                            if(formval.length == key.length + 1 + parseInt(postChar))
                                            {
                                                success = 'true';
                                            } 
                                            keyMatch = 'true';
                                        }
                                     }
                             }
                     }
             } 
            if(keyMatch == 'false')
            {
                formval = formval.replace(/_+/g, '');  //Erase Underscore
                formval = formval.replace(/\W+/g, ''); // Erase all non-alphanumeric
         if(formval != "DI")
         {
             formval = formval.replace(/I+/gi, '');
         }
         else if(formval == "DI" && dtcFormatsMap != null && !dtcFormatsMap.hasOwnProperty("DI"))
         {
             formval = formval.replace(/I+/gi, '');
         }
            }
    }
        dtcSuccess = success;
        formval = formval.substring(0,9);
        dtc.value = formval;
        //R 8.6.1 - T30017299 - End
}*/
function validateDTC(dtc)
{
    var formval;
    formval = dtc.value;
    formval = formval.toUpperCase(); // Convert to Uppercase
    dtc.value = formval;
    dtcSuccess = 'true';

}

function add( source, dest )
{
    validateDTC(source);

    var finalValue = source.value;

    if(isEmpty(finalValue)) return;
    
    var firstOption = dest.options[0];

    try 
    {
        dest.add( new Option(finalValue, finalValue), firstOption);
    } 
    catch(ex) 
    {
        if(firstOption != null)
            dest.add( new Option(finalValue, finalValue), 0);
        else dest.add( new Option(finalValue, finalValue) );
    }

    source.value = '';
}

function remove( textBox )
{   
    for( index = textBox.length - 1; index >= 0; index-- )
    {   
        if(textBox.options[index].selected)
            textBox.remove(index);
    }
}        
/* ------- t3.js ends here ------*/

/* ------- search.js starts here ------*/
    function handleOnChangeDivision( div, model ) {
        clearSelect(getNetuiTagName('serviceInfoModel'), getNetuiTagName('serviceInfoServiceCategory'));
        clearElement(getNetuiTagName('serviceInfoSymptomSection'));
        toggleForm( getNetuiTagName('searchDocument'), true);
        document.getElementById('lastYear').value = '';
        document.getElementById('lastModel').value = '';

        var postProcess = null;
        if (model != null) {
            postProcess = 'setSelected(getNetuiTagName("serviceInfoModel"), "' +  model + '");';
        }
        new getModels( div, getNetuiTagName('serviceInfoModel'), true,getNetuiTagName('searchDocument'), postProcess);
        new getYearsReversByDivision( div, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'));

        document.getElementById('lastChanged').value = "division";

        servicecategory();
    }

    function handleOnChangeDivisionWhenErrorOccurs( div, model ) {
        toggleForm( getNetuiTagName('searchDocument'), true);
        document.getElementById('lastYear').value = '';
        document.getElementById('lastModel').value = '';

        var postProcess = null;
        if (model != null) {
            postProcess = 'setSelected(getNetuiTagName("serviceInfoModel"), "' +  model + '");';
        }
        //new getModels( div, getNetuiTagName('serviceInfoModel'), true,getNetuiTagName('searchDocument'), postProcess);
        //new getYearsReversByDivision( div, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'));

        document.getElementById('lastChanged').value = "division";

        servicecategoryWithError();
       // var servCat = document.getElementById(getNetuiTagName('serviceInfoSymptomSection')).value;
       // handleOnChangeServiceCategoryWithError (servCat);
        toggleForm( getNetuiTagName('searchDocument'), false);
    }


    function handleOnChangeYear( division, model, year ) {
        toggleForm( getNetuiTagName('searchDocument'), true);
        document.getElementById('lastModel').value = document.getElementsByName(getNetuiTagName('serviceInfoModel'))[0].value;
        document.getElementById('lastYear').value = document.getElementsByName(getNetuiTagName('serviceInfoYear'))[0].value;

        if( year == 'ALL' ) {
            new getModels( division, getNetuiTagName('serviceInfoModel'), true,getNetuiTagName('searchDocument'), postProcess);
            new getYearsReversByDivision( division, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'));
            setAttributeInSession('SEARCH_MODEL', 'ALL');
        } else {
            var postProcess = 'setSelected(getNetuiTagName("serviceInfoYear"), "' +  document.getElementById('lastYear').value + '");'
                        + 'setSelected(getNetuiTagName("serviceInfoModel"), "' +  document.getElementById('lastModel').value + '");';
            new getModelReverse(division, year, getNetuiTagName('serviceInfoModel'), true, getNetuiTagName('searchDocument'), postProcess);
        }
    }
    
    function handleOnChangeYearAction( division, model, year ) {
        toggleForm( getNetuiTagName('searchDocument'), true);
        document.getElementById('lastModel').value = document.getElementsByName(getNetuiTagName('serviceInfoModel'))[0].value;
        document.getElementById('lastYear').value = document.getElementsByName(getNetuiTagName('serviceInfoYear'))[0].value;

        if( year == 'ALL' ) {
            new getModelsWithPrefix( division, getNetuiTagName('serviceInfoModel'), true,getNetuiTagName('searchDocument'), postProcess,true);
            new getYearsReversByDivisionWithPrefix( division, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'),postProcess,true);
            setAttributeInSession('SEARCH_MODEL', 'ALL');
        } else {
            var postProcess = 'setSelected(getNetuiTagName("serviceInfoYear"), "' +  document.getElementById('lastYear').value + '");'
                        + 'setSelected(getNetuiTagName("serviceInfoModel"), "' +  document.getElementById('lastModel').value + '");';
            new getModelReverseAction(division, year, getNetuiTagName('serviceInfoModel'), true, getNetuiTagName('searchDocument'), postProcess,model);
        }
    }

    function handleOnChangeModel( division, model, year ) {
        toggleForm( getNetuiTagName('searchDocument'), true);
        document.getElementById('lastModel').value = document.getElementsByName(getNetuiTagName('serviceInfoModel'))[0].value;
        document.getElementById('lastYear').value = document.getElementsByName(getNetuiTagName('serviceInfoYear'))[0].value;
        clearSelect(getNetuiTagName('serviceInfoYear'));

        var postProcess = null;

        if(model == 'ALL') {
            new getModels( division, getNetuiTagName('serviceInfoModel'), true,getNetuiTagName('searchDocument'), postProcess);
            new getYearsReversByDivision( division, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'));
            setAttributeInSession('SEARCH_YEAR', 'ALL');            
        } else {
            //alert ('year == |'+ year + '|');
            if (year != null && year != true && year != '') {
                postProcess = 'setSelected(getNetuiTagName("serviceInfoYear"), "' +  document.getElementById('lastYear').value + '");'
                            + 'setSelected(getNetuiTagName("serviceInfoModel"), "' +  document.getElementById('lastModel').value + '");';
                setAttributeInSession('SEARCH_YEAR', document.getElementById('lastYear').value);
            } else {
               setAttributeInSession('SEARCH_YEAR', 'ALL');
            }
            
            new getYears(model, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'), postProcess );
        }
    }
    
    function handleOnChangeModelAction( division, model, year ) {
        toggleForm( getNetuiTagName('searchDocument'), true);
        document.getElementById('lastModel').value = document.getElementsByName(getNetuiTagName('serviceInfoModel'))[0].value;
        document.getElementById('lastYear').value = document.getElementsByName(getNetuiTagName('serviceInfoYear'))[0].value;
        clearSelect(getNetuiTagName('serviceInfoYear'));

        var postProcess = null;

        if(model == 'ALL') {
            new getModelsWithPrefix( division, getNetuiTagName('serviceInfoModel'), true,getNetuiTagName('searchDocument'), postProcess,true);
            new getYearsReversByDivisionWithPrefix( division, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'),postProcess,true);
            setAttributeInSession('SEARCH_YEAR', 'ALL');            
        } else {
            //alert ('year == |'+ year + '|');
            if (year != null && year != true && year != '') {
                postProcess = 'setSelected(getNetuiTagName("serviceInfoYear"), "' +  document.getElementById('lastYear').value + '");'
                            + 'setSelected(getNetuiTagName("serviceInfoModel"), "' +  document.getElementById('lastModel').value + '");';
                setAttributeInSession('SEARCH_YEAR', document.getElementById('lastYear').value);
            } else {
               setAttributeInSession('SEARCH_YEAR', 'ALL');
            }
            
            new getYearsAction(model, getNetuiTagName('serviceInfoYear'), true, getNetuiTagName('searchDocument'), postProcess,year,division );
        }
        return false;
    }

    function handleOnChangeServiceCategory(value ) {
        clearElement(getNetuiTagName('serviceInfoSymptomSection'));
    	//alert(sectionPrefix);
    	//clearElementWithPrefix(getNetuiTagName('serviceInfoSymptomSection'),prefix);
        toggleForm( getNetuiTagName('searchDocument'), true);
        if( value == 'ALL' ) {
            toggleForm( getNetuiTagName('searchDocument'), false);
        } else {
            section(value);
        }
    }

    function handleOnChangeServiceCategoryWithError( value ) {
        //clearElement(getNetuiTagName('serviceInfoSymptomSection'));
        //toggleForm( getNetuiTagName('searchDocument'), true);
        if( value == 'ALL' ) {
            toggleForm( getNetuiTagName('searchDocument'), false);
        } else {
            section(value);
        }
    }

    function handleOnLoadForm(isSearched) {
        try {
        	
            if(isSearched=='false'){
            document.getElementsByName(getNetuiTagName('serviceInfoMake'))[0].onchange();
            }
            if(isSearched=='true'){
                var optLen = document.getElementById("serviceInfoServiceCategory").options.length;
                var options=document.getElementById("serviceInfoServiceCategory").options;
             	 var selectedIndex=document.getElementById("serviceInfoServiceCategory").selectedIndex;
               var value=document.getElementById("serviceInfoServiceCategory").options[selectedIndex].value;

           	for (var i = 0; i < optLen; i++){
	        	 options[i].text=options[i].text.replace(servicePrefix,"");
	        	if(options[i].value==value){
	        		 options[i].text = servicePrefix + options[i].text;
	        	}
            }
               }
            
            setAttributeInSession('SEARCH_CHANGED_OPTION','false');
            
            /*if( screen.width<=1024 && screen.height<=768 ) {
                for(var i=1;i<7;i++) {
                    var currentDmy = 'dmy' + i;
                    document.getElementById(currentDmy).className="search-tablet-cell";
                }

                for(var i=1;i<5;i++) {
                    var current = 'scs' + i;
                    document.getElementById(current).className="search-tablet-cell";
                }
            } else {
                for(var i=1;i<7;i++) {
                    var currentDmy = 'dmy' + i;
                    document.getElementById(currentDmy).className="search-normal-cell";
                }

                for(var i=1;i<5;i++) {
                    var current = 'scs' + i;
                    document.getElementById(current).className="search-normal-cell";
                }
            }*/
        } catch(e){
            /*catching to workaround IE issue of error handling*/
        }
    }

    function writeResultsOnTitleBar(divName, results) {
        div = document.getElementById('results-div-' + divName);
        textElement = document.createTextNode(results);
        div.appendChild(textElement);
    }

    function setSelected( formName, value ) {

        var element = formName;

        if (typeof element == 'string')
            element = document.getElementsByName(element)[0];

        if (element && element.options) {
            for (var i=0; i<element.options.length; i++) {
                if (element.options[i].text == value) element.options[i].selected = true;
            }
        }
    }
    
    function setAttributeInSession(attName, attValue) {
        new setDataInSession (attName, attValue);
    }
/* ------- search.js ends here ------*/

/* ------- t3taseditor.js starts here ------*/

function tas_clearSelect( tagId, optionLabel, optionValue ) {

    var element = tagId;

    if (typeof element == 'string')
        element = document.getElementsByName(element)[0];

    if (element && element.options) {
        element.options.length = 1;
        element.options[0] = new Option(optionLabel, optionValue);
        element.selectedIndex = 0;
    }
}

/* ------- t3taseditor.js ends here ------*/

    function getKeyCode (e) {
        var key;
        if( !e ) { e = window.event; }
        key=e.keyCode;
        if( null == key ) {
            key = e.which; //window.event.keyCode;
        }
        return key;
    }   
        
  function popupFlatRateManualWindow(urlVal,windowName,scrollBars,menuBar,reSizeable,toolBar,statusBar,resizable,fullscreen,errorMessage) {   
	    

	    var paraString
	    var wt
	    var ht

	    // Bug fix: we are now blanking the windowName variable
	    windowName == "";

	    wt = 900; 
	    ht = 650; 

	   
	    var winl = (screen.width - wt) / 2;
	    var wint = (screen.height - ht) / 2;
	        
	    paraString = "width=" + wt + ",height=" + ht + ",top=" + wint + ",left="+ winl +",toolbar=yes";
	    
	    if (scrollBars == 1) {
	        paraString = paraString + ",scrollbars=yes";
	    } else {
	        paraString = paraString + ",scrollbars=no";
	    }
	    if (menuBar == 1) {
	        paraString = paraString + ",menubar=yes";
	    }
	    if (reSizeable == 1) {
	        paraString = paraString + ",resizable=yes";
	    }
	    if (toolBar == 1) {
	        paraString = paraString + ",toolBar=yes";
	    } else {
	        paraString = paraString + ",toolBar=no";
	    }
	    if (statusBar == 1) {
	        paraString = paraString + ",status=yes";
	    }else{
	        paraString = paraString + ",status=no";
	    }
	    if (resizable == 1) {
	        paraString = paraString + ",resizable=yes";
	    }else{
	        paraString = paraString + ",resizable=no";
	    }
	    
	    var frmWindow = window.open('','flatratemanual',paraString);
	    
		if(frmWindow.location == 'about:blank') {
		    frmWindow.location.href=urlVal;
		    frmWindow.focus();
		} else {
			alert(errorMessage);
		}
    }
  
  
  function addLoadEvent(func) {
	    var old = window.onload;
	    window.onload = function() {
	      if (old) old();
	      func();
	    };
	  }
  
  function getDivisionVDS( year,division,model, target, addAll, formTagId, postProcess ) {
	    return getVdsData( "divisionvds", year, division, model, target, addAll, formTagId, postProcess, true );
	}
  function getDMVDS( year,division,model, target, addAll, formTagId, postProcess ) {
	    return getVdsData( "divisionmodelvds", year, division, model, target, addAll, formTagId, postProcess, true );
	}
  function getDMYVDS( year,division,model, target, addAll, formTagId, postProcess ) {
	    return getVdsData( "dmyvds", year, division, model, target, addAll, formTagId, postProcess, true );
	}
  
//base method for calling the vehicle information
  function getVdsData( dataset,year,division,model, target, addAll, formTagId, postProcess, isFireTarget ) {
      // USING GET because POST works very very slow on IE, but works fine on netscape
      return new AJAXRequest("GET", "/t3Portal/ajax/getVehicle.jsp?dataset="+dataset+"&year=" + year +"&division="+division +"&model="+model + "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget=", "bogusData", true, postProcess );
  }

  function getYearsByDivision( division, target, addAll, formTagId, postProcess ) {
	    return getVehicleSelectData( "divisionyears", division, target, addAll, formTagId, postProcess, false);
	}
  //R 9.4.1 T300018250
  function validateDtcData(dtc,obj)
  {
	  //var xmlhttp= AJAXRequest("GET","/t3Portal/ajax/InvalidDtc.jsp?dtc="+dtc,true);
         var actionJsp="/t3Portal/ajax/InvalidDtc.jsp?dtc="+dtc;
	   var http_request = new XMLHttpRequest();
	   try{
	      // Opera 8.0+, Firefox, Chrome, Safari
	      http_request = new XMLHttpRequest();
	   }catch (e){
	      // Internet Explorer Browsers
	      try{
	         http_request = new ActiveXObject("Msxml2.XMLHTTP");
	      }catch (e) {
	         try{
	            http_request = new ActiveXObject("Microsoft.XMLHTTP");
	         }catch (e){
	            // Something went wrong
	            alert("Your browser broke!");
	            return false;
	         }
	      }
	   }
	   http_request.open("GET", actionJsp, false);
	   http_request.send(null);
	   if (http_request.readyState == 4 )
       {
 		  if(http_request.status==200)
 			  {
 		// Javascript function JSON.parse to parse JSON data
 			 var response=http_request.responseText;
			  response=response.replace(/\n/g,'');
			  response=response.replace(/\r/g,'');
			  response=response.replace(/\t/g,'');
 		        obj.value=response;
 			  }
         
       }
	 
	}
//end R 9.4.1 T300018250
  function validateNumberOfVinLookup(formName)
  {	

		var xmlRequest = false;

		if (window.XMLHttpRequest) 
		{
			xmlRequest = new XMLHttpRequest();
	        
	    	if(xmlRequest.overrideMimeType) 
	  		{
				xmlRequest.overrideMimeType('text/xml');
	    	}			
		} 
		else if (window.ActiveXObject) 
		{
			xmlRequest = new ActiveXObject("Microsoft.XMLHTTP");
		}
     
    	var url = '/t3Portal/ajax/getVINLookupCount.jsp';
     
    	alert(url);
    	xmlRequest.open('GET', url, true);
    	xmlRequest.onreadystatechange = function() 
    	{ 
          progressResponse(xmlRequest); 
    	};
    	xmlRequest.send('');

    	function progressResponse(xmlRequest) 
    	{
        
    		if (xmlRequest.readyState == 4) 
        	{
        	
          	if (xmlRequest.status == 200) 
              {
					var vinLookupEventStatus = xmlRequest.responseText;
	              	if('false' == trim(vinLookupEventStatus) || trim(vinLookupEventStatus) == false
	              			|| "false" == trim(vinLookupEventStatus))
	              		alert("You have exceeded the total number of VIN lookups allowed for a user in a day. Please try again tomorrow");
	              	else
	              		document.forms[getNetuiTagName(formName, this)].submit();
              }
    	 	}
       }
   } 
//  Rel 9.3.1 Techinfo prelogin Enhancement - 17758 Start
  function getTechInfoPreloginVehicleSelectData( dataset, key, target, addAll, formTagId, postProcess, isFireTarget ) {
	    // USING GET because POST works very very slow on IE, but works fine on netscape
	    return new AJAXRequest("GET", "/techInfoPortal/ajax/getVehicle.jsp?dataset=" + dataset + "&key=" + key + "&target=" + target + "&addAll=" + addAll + "&formTagId=" + formTagId + "&isFireTarget=", "bogusData", true, postProcess );
	}

function getTechInfoPreloginModels( division, target, addAll, formTagId, postProcess ) {
	    return getTechInfoPreloginVehicleSelectData( "model", division, target, addAll, formTagId, postProcess, true );
	}

	function getTechInfoPreloginYears( model, target, addAll, formTagId, postProcess ) {
	    return getTechInfoPreloginVehicleSelectData( "year", model, target, addAll, formTagId, postProcess, true );
	}

	function getTechInfoPreloginYearsReversByDivision( division, target, addAll, formTagId, postProcess ) {
	    return getTechInfoPreloginVehicleSelectData( "yearreverse", division, target, addAll, formTagId, postProcess, false );
	}

	function getTechInfoPreloginModelReverse( division, year, target, addAll, formTagId, postProcess ) {
	    return getTechInfoPreloginVehicleSelectData( "modelreversebyyeardiv", division + ',' + year, target, addAll, formTagId, postProcess, false );
	}
	//Rel 9.3.1 Techinfo prelogin Enhancement - 17758 End

	//Rel14.10 DTC Help message pop screen size - start
	var dtcpopupleft = (screen.width - 640) / 2;
  	var dtcpopuptop = (screen.height - 360) / 2;
  	
  	function openDtcHelpPopup(){
  		t3popup_staticcontent('/html/dtchelpmessage.html', 'DTC Help Message', 'no', 'DTCMSG', 'width=640,height=360,scrollbars=yes,menubar=no,resizable=yes,left='+dtcpopupleft+',top='+dtcpopuptop);
  	}
	//Rel14.10 DTC Help message pop screen size - end
	
  //T300018306 BackLog Defect Fixes- Starts
    function loadHtmlUl(hrefVal,language)
    {
  	  //var xmlhttp= AJAXRequest("GET","/t3Portal/ajax/InvalidDtc.jsp?dtc="+dtc,true);
           var actionJsp="/t3Portal/ajax/getHtmlUrlAjax.jsp?hrefVal="+hrefVal;
  	   var http_request = new XMLHttpRequest();
  	   try{
  	      // Opera 8.0+, Firefox, Chrome, Safari
  	      http_request = new XMLHttpRequest();
  	   }catch (e){
  	      // Internet Explorer Browsers
  	      try{
  	         http_request = new ActiveXObject("Msxml2.XMLHTTP");
  	      }catch (e) {
  	         try{
  	            http_request = new ActiveXObject("Microsoft.XMLHTTP");
  	         }catch (e){
  	            // Something went wrong
  	            alert("Your browser broke!");
  	            return false;
  	         }
  	      }
  	   }
  	   http_request.open("GET", actionJsp, false);
  	   http_request.send(null);
  	   if (http_request.readyState == 4 )
         {
   		  if(http_request.status==200)
   			  {
   		// Javascript function JSON.parse to parse JSON data
   			 var response=http_request.responseText;
   			 var resp=trim(response);
   			 if(language=='en')
   				processEnglishLanguage(resp);
   			 else if(language=='fr')
   				processFrenchLanguage(resp);
   			 else if(language=='es')
   			 processSpanishLanguage(resp);
   			  }
           
         }
  	 
  	}
    
  //T300018306 BackLog Defect Fixes- Ends
  
    //T300020157 - Solr Search Defect Fix - Starts
    function openSolrSearchHelpPopup(){
    	var searchpopupleft = (screen.width - 640) / 2;
      	var searchpopuptop = (screen.height - 360) / 2;
  		t3popup_staticcontent('/html/solrSearchhelpmessage.html', 'Solr Search Help Message', 'no', 'SEARCHMSG', 'width=844,height=1014,scrollbars=yes,menubar=no,resizable=yes,left='+searchpopupleft+',top='+searchpopuptop);
  	}
    //T300020157 - Solr Search Defect Fix - Ends
    
    // TCI Changes - Start
    function openVinHelpContentPopup(){
    	var searchpopupleft = (screen.width - 640) / 2;
    	var searchpopuptop = (screen.height - 360) / 2;
    	t3popup_staticcontent('/tis/html/vehicleinquiry/vinInquiryHelpmessage.html', 'Vin Inquiry Help Message', 'no', 'VININQUIRY', 'width=844,height=1014,scrollbars=yes,menubar=no,resizable=yes,left='+searchpopupleft+',top='+searchpopuptop);
    }
    // TCI Changes - End
    //EWD T300020226 Enhancement Changes R17.04 - Starts
    function ewdLinkFormation(link){
     	//alert("SUCCESS");
     	 
     	//alert(window.parent.location.href);
     	//alert(document.title);
     	//alert(document.getElementById("prod").innerHTML);
     	//parent.navigation_frame.document.getElementById("pcd").value;
     	var pubNum = '';
     	var locale = '';
     	var ewd_type = '';
     	var ewd = '';
     	var type = '';
     	var code = '';
     	var pinno = '';
     	var url = '/t3Portal/ewdAppRedirect/';
     	for(i=0;i<window.parent.location.href.split('?')[1].split('&').length;i++){
     		if('publicationNumber' == window.parent.location.href.split('?')[1].split('&')[i].split('=')[0]){
     			pubNum = window.parent.location.href.split('?')[1].split('&')[i].split('=')[1];
     			//alert(pubNum);
     			}
     		if('locale' == window.parent.location.href.split('?')[1].split('&')[i].split('=')[0]){
     			locale = window.parent.location.href.split('?')[1].split('&')[i].split('=')[1];
     			//alert(locale);
     			}
     		}
     	for(i=0;i<link.split('?')[1].split('&').length;i++){
     		if('ewd_type' == link.split('?')[1].split('&')[i].split('=')[0]){
     			ewd_type = link.split('?')[1].split('&')[i].split('=')[1];
     			//alert(ewd_type);
     			}
     		if('ewd' == link.split('?')[1].split('&')[i].split('=')[0]){
     			ewd = link.split('?')[1].split('&')[i].split('=')[1];
     			//alert(ewd);
     			}
     		if('type' == link.split('?')[1].split('&')[i].split('=')[0]){
     			type = link.split('?')[1].split('&')[i].split('=')[1];
     			//alert(type);
     			}
     		if('code' == link.split('?')[1].split('&')[i].split('=')[0]){
     			code = link.split('?')[1].split('&')[i].split('=')[1];
     			//alert(code);
     			}
     		if('pinno' == link.split('?')[1].split('&')[i].split('=')[0]){
     			pinno = link.split('?')[1].split('&')[i].split('=')[1];
     			//alert(pinno);
     			}
     	}
     	
     	if (null != parent.navigation_frame.document.getElementById("pcd")){
         	//alert("start");
         	//alert(parent.navigation_frame.document.getElementById("pcd").value);
         	pcdValue = parent.navigation_frame.document.getElementById("pcd").value;
         	pcdValue = pcdValue.substring(3,7) + pcdValue.substring(0,2);

         	url = url + pubNum + '/' + pcdValue + '/' + locale + '/' + ewd_type + '/' + ewd + '/' + type + '/' + code + '/' + pinno;
         	} else {
         		url = url + pubNum + '/' + new Date().getFullYear() + '/' + locale + '/' + ewd_type + '/' + ewd + '/' + type + '/' + code + '/' + pinno;
         	}
     	window.open(url, 'ewdAppRedirect', 'width=1018,height=718,top=45,left=210,toolbar=yes,scrollbars=no,resizable=yes,toolBar=no');
     }
    //EWD T300020226 Enhancement Changes R17.04 - Ends

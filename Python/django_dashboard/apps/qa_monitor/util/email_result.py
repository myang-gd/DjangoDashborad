from django.conf import settings
from apps.healthcheck.util.mail_util import sendMail
from xml.dom.minidom import parseString
from common_utils.str_util import StrUtil
from common_utils.constant import Constant

STRICT, LOOSE = (
    'strict', 'loose'
)
JSON, XML = (
    'json', 'xml'
)
def sendMonitorResult(toaddr, monitorName, runResult, runID):
    sender = getattr(settings, "MONITOR_SENDER")
    toaddrList = toaddr.split(",")
    application_url = getattr(settings, "APPLICATION_URL")
    run_url = application_url + "/monitor/monitor_run_result/?id=" + str(runID)
    doc_link = 'https://confluence/display/QAAR/Dashboard+Portal+-+QA+Infrastructure+Monitor+System'
    print("sending mail to " + str(toaddrList))
    message = """\
        <html>
          <head></head>
          <body>
            <h3>QA Monitor System</h3>
            <p>
                Finished checking for monitor <b>{0}</b> with <b>{1}</b> result
                <br>
                Login to <a href="{2}">Monitor Application</a> to view detail result
                <br>
                Learn more about Monitor at <a href="{3}">Monitor Document</a> 
            </p>
          </body>
        </html>
    """.format(monitorName, runResult, run_url, doc_link)
    sendMail(sender, toaddrList, [], "QA Monitor Alert " + monitorName + ' ' + runResult, message)
def sendMonitorResultWithResponse(toaddr, monitorName, runResult, response, validationResultMap, request=None, url=None ,headers=None, **kwargs):
    sender = getattr(settings, "MONITOR_SENDER")
    toaddrList = toaddr.split(",")
    doc_link = 'https://confluence/display/QAAR/Dashboard+Portal+-+QA+Infrastructure+Monitor+System'
    measure = STRICT
    print("sending mail to " + str(toaddrList))
    try:
        responseMessage = parseString(response).toprettyxml(indent='  ')#newl='',
    except:
        responseMessage = response
        measure = LOOSE
        
    url_html = """  <br>
                <b>Url:</b>
                <br>
                <br>
                <pre>{0}</pre> """.format(url) if url else ""
    headers_html = """  <br>
                <b>Headers:</b>
                <br>
                <br>
                <pre>{0}</pre> """.format(headers) if headers else ""
    if request:
        measureRequest = STRICT
        try:
            requestMessage = parseString(request).toprettyxml(indent='  ')#newl='',
        except:
            requestMessage = request
            measureRequest = LOOSE
        
        message = """\
            <html>
              <head></head>
              <body>
                <h3>QA Monitor System</h3>
                <p>
                    Finished checking for monitor <b>{0}</b> with <b>{1}</b> result
                    <br>
                    Learn more about Monitor at <a href="{2}">Monitor Document</a>
                    <br>
                    <b>Assertion:</b>
                    <br>
                    <br>
                    <pre>{3}</pre>
                    {6}
                    <br>
                    <b>Response:</b>
                    <br>
                    <br>
                    <pre>{4}</pre>
                    {7}  
                    <br>
                    <b>Request:</b>
                    <br>
                    <br>
                    <pre>{5}</pre>  
                </p>
              </body>
            </html> 
        """.format(monitorName, runResult, doc_link, get_validationResult_for_html_fromMap(validationResultMap, measure), html_escape(responseMessage, measure),
                   html_escape(requestMessage, measureRequest),url_html, headers_html)
    else: 
        message = """\
            <html>
              <head></head>
              <body>
                <h3>QA Monitor System</h3>
                <p>
                    Finished checking for monitor <b>{0}</b> with <b>{1}</b> result
                    <br>
                    Learn more about Monitor at <a href="{2}">Monitor Document</a>
                    <br>
                    <b>Assertion:</b>
                    <br>
                    <br>
                    <pre>{3}</pre>
                    {5}
                    <br>
                    <b>Response:</b>
                    <br>
                    <br>
                    <pre>{4}</pre>  
                    {6}
                </p>
              </body>
            </html> 
        """.format(monitorName, runResult, doc_link, get_validationResult_for_html_fromMap(validationResultMap, measure), html_escape(responseMessage, measure), url_html, headers_html)
    email_title = "QA Monitor Alert " + monitorName + ' ' + runResult
    if kwargs.get('email_title'):
        email_title = kwargs.get('email_title')
    sendMail(sender, toaddrList, [], email_title, message)

html_escape_table_strict = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }
html_escape_table_loose = {
    "&": "&amp;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text, measure):
    """Produce entities within text."""
    if measure == STRICT :
        return "".join(html_escape_table_strict.get(c,c) for c in text)
    elif measure == LOOSE :
        return "".join(html_escape_table_loose.get(c,c) for c in text) 

def get_validationResult_for_html(validation_result_str):
    validation_result_map = StrUtil.validation_result_to_map(validation_result_str)
    return get_validationResult_for_html_fromMap(validation_result_map)

def get_validationResult_for_html_fromMap(validation_result_map, measure):
    result_html = """<table class=MsoNormalTable border=1 cellspacing=3 cellpadding=0
                         style='mso-cellspacing:2.2pt;border:solid black 1.0pt;mso-yfti-tbllook:1184;
                         mso-padding-alt:0in 0in 0in 0in;border-spacing: 5px'>
                         <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes'>
                          <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                          <p class=MsoNormal><b>Validation<o:p></o:p></b></p>
                          </td>
                          <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                          <p class=MsoNormal><b>Result<o:p></o:p></b></p>
                          </td>
                         </tr>
                         """
    result_header_with_expected = """<table class=MsoNormalTable border=1 cellspacing=3 cellpadding=0
                         style='mso-cellspacing:2.2pt;border:solid black 1.0pt;mso-yfti-tbllook:1184;
                         mso-padding-alt:0in 0in 0in 0in;border-spacing: 5px'>
                         <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes'>
                          <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                          <p class=MsoNormal><b>Validation<o:p></o:p></b></p>
                          </td>
                          <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                          <p class=MsoNormal><b>Expected<o:p></o:p></b></p>
                          </td>
                          <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                          <p class=MsoNormal><b>Actual<o:p></o:p></b></p>
                          </td>
                          <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                          <p class=MsoNormal><b>Result<o:p></o:p></b></p>
                          </td>
                         </tr>
                         """
    response_format = XML
    if len(validation_result_map) >= 1 and type(list(validation_result_map.values())[0]) == type({}):
        response_format = JSON
        result_html = result_header_with_expected

    for validation, result in validation_result_map.items():
        if response_format == JSON:
            result_str = str(result[Constant.RESULT])
            expected = str(result[Constant.EXPECTED])
            actual = str(result[Constant.ACTUAL])
            if result_str == Constant.FAILED:
                bgcolor = '#FF0000'
            elif result_str == Constant.PASSED:
                bgcolor = '#7FFF00'
            else:
                bgcolor = '' 
            result_html += """
            <tr style='mso-yfti-irow:1'>
              <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                <p class=MsoNormal>{0}</p>
              </td>
              <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                <p class=MsoNormal>{1}</p>
              </td>
              <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                <p class=MsoNormal>{2}</p>
              </td>
              <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt' bgcolor="{3}">
                  <p class=MsoNormal>{4}</p>
              </td>
            </tr>""".format(html_escape(validation, measure), expected, actual, bgcolor, result_str)
        else:
            if result == Constant.FAILED:
                bgcolor = '#FF0000'
            elif result == Constant.PASSED:
                bgcolor = '#7FFF00'
            else:
                bgcolor = '' 
            result_html += """
            <tr style='mso-yfti-irow:1'>
              <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt'>
                <p class=MsoNormal>{0}</p>
              </td>
              <td style='border:solid black 1.0pt;padding:3.75pt 3.75pt 3.75pt 3.75pt' bgcolor="{1}">
                  <p class=MsoNormal>{2}</p>
              </td>
            </tr>""".format(html_escape(validation, measure), bgcolor, result)
    
    result_html += """</table>"""
    
    return result_html
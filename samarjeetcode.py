import requests
from bs4 import BeautifulSoup
import re
from unicodedata import normalize
import simplematch
import pendulum

def normalize_text(raw_text):
    return re.sub("\s\s+", " ", normalize("NFKD", raw_text.strip()))

def strTOsnake(input_string):
    # Remove special characters from the left and right sides of the string
    input_string = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', input_string)
    # Convert the string to snake case
    snake_case_string = re.sub(r'\W+', '_', input_string).strip('_').lower()
    return snake_case_string

def add_string_list(string_list):
    result = ""
    for string in string_list:
        result += string
    return result

def get_html_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.prettify()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

def splitMystirng(text):
    lSting = text.split('\n')
    tempL = []
    for i in lSting:
        tempS = i.strip()
        if tempS!="":
            tempL.append(tempS)
    return tempL 
def detailstrToList(keyDict,cells):
    col_no = len(keyDict)
    temp_i = 0
    tempDict = {}
    output = []
    temp_l = len(cells)
    # print(temp_l)
    for i in range(temp_l):
        tempDict[keyDict[temp_i]] = cells[i]
        # print(tempDict)
        if not (temp_i+1)<col_no:
            output.append(tempDict)
            temp_i = -1
            tempDict = {}
        temp_i= temp_i+1
    return output
def parseCaseStatus(soup):
    ansDict = {}
    table = soup.find(class_="table table-bordered table-extra-condensed")
    for i in table.find_all("tr"):
        if(normalize_text(i.text)=="CASE LISTING DETAILS (Tentative)"):
            break
        tds = i.find_all("td")
        if len(tds)==2:
            ansDict[strTOsnake(normalize_text(tds[0].text))] = normalize_text(tds[1].text)
    print(ansDict)        
    return ansDict

def caseDetailStatus(soup):
    ansDict = {}
    tempFlag = False
    table = soup.find(class_="table table-bordered table-extra-condensed")
    for i in table.find_all("tr"):
        if(normalize_text(i.text)=="CASE LISTING DETAILS (Tentative)"):
            tempFlag = True
        elif (normalize_text(i.text)=="PETITIONER/APPLICANT DETAIL"):
            break    
        tds = i.find_all("td")
        if tempFlag and len(tds)==2:
            ansDict[strTOsnake(normalize_text(tds[0].text))] = normalize_text(tds[1].text)
    print(ansDict)        
    return ansDict
def petDetailStatus(rawStr):
    petDetailKeys = [
    "Petitioner Name -{pname} "
    "Petitioner/Applicant Address: {petitioners_address}*",
    "Additional Party: {additional_pet_party}*" ,
    "Advocate Name: {pet_adv}*",
    "Additional Advocate:*{additional_pet_adv}"
    ]
    return simplematch.match(add_string_list(petDetailKeys),rawStr)
def resDetailStatus(rawStr):
    resDetailKeys =[
    "Respondent Name -{rname} ",
    "Respondent/Defendent Address:{respondent_address} ",
    "Additional Party:*{additional_party} ",
    "Advocate Name -*{res_adv} ",
    "Additional Advocate:*{additional_res_adv}"
    ]
    return simplematch.match(add_string_list(resDetailKeys),rawStr)
def rcTcsCseCurrentStatus(rewstr):
    rcTcsCseCurrentStatuskey =[
    "Court Name:*{courtName} ",
    "Next Listing Date:*{nextListingDate} ",
    "Next Listing Purpose:*{nextListingPurpose}"
    ]
    return simplematch.match(add_string_list(rcTcsCseCurrentStatuskey),rewstr)
def propertyDetailList(soup):
    proDetailTable = soup.find(class_="table table-striped")
    cells = []
    rows = proDetailTable.find_all('td')
    for row in rows:
        cells.append(normalize_text(row.text))
    keyDict = ["property_type","detail_of_property"]
    return detailstrToList(keyDict,cells[len(keyDict)+1:])


def caseProceedingDetaillist(soup):
    tempTable = soup.find_all(class_="table table-bordered")
    cells = []
    for i in tempTable:
        if i.find_all("tr") and normalize_text(i.find_all("tr")[0].text) == "CASE PROCEEDING DETAILS":
            caseProceedingTable = i
    for i in caseProceedingTable.find_all('td'):
        c = normalize_text(i.text)
        if c=="RC/TRC CASE CURRENT STATUS":
            break
        cells.append(c)
        # print(c)
    keyDict =["court_name","couselist_date","purpose"]    
    # return detailstrToList(keyDict,cells[len(keyDict):])
    # print(cells)
    col_no = len(keyDict)
    temp_i = 0
    tempDict = {}
    output = []
    temp_l = len(cells)
    for i in range(col_no,temp_l):
        tempDict[keyDict[temp_i]] = cells[i]
        # print(tempDict)
        if (temp_i+1)==col_no:
            output.append(tempDict)
            temp_i = -1
            tempDict = {}
        temp_i= temp_i+1
    return output

def rcCaseProceedingDetailList(soup):
    tempTable = soup.find_all(class_="table table-bordered")
    cells = []
    for i in tempTable:
        if i.find_all("tr") and normalize_text(i.find_all("tr")[0].text) == "CASE PROCEEDING DETAILS":
            caseProceedingTable = i
    tempFlag = False # after RC/TRC case wae get list        
    for i in caseProceedingTable.find_all('td'):
        c = normalize_text(i.text)
        if tempFlag:
            cells.append(c)
            # print(c)
        if c=="RC CASE PROCEEDING DETAILS":
            tempFlag = True
 
    keyDict =["court_no","couselist_date","purpose"]
    return detailstrToList(keyDict,cells[len(keyDict):])
def parse_table(rawHtml):
    boundry = [
    "CASE STATUS {caseStatus} ",
    "CASE LISTING DETAILS (Tentative) {caseDetail} ", 
    "PETITIONER/APPLICANT DETAIL {petDetail} ",
    "RESPONDENTS/DEFENDENT DETAILS {resDetail} ",
    "PROPERTY DETAILS {propertyDetailList} ",
    "CASE PROCEEDING DETAILS {caseProceedingDetaillist} ",
    "RC/TRC CASE CURRENT STATUS {rcTcsCaseCurrentStatus} ",
    "RC CASE PROCEEDING DETAILS {rcCaseProceedingDetailList}",
    ]
    table_dic = {}
    soup = BeautifulSoup(rawHtml,'html.parser')
    table = soup.find(class_="table table-bordered table-extra-condensed")           
    rawString = normalize_text(table.text)
    dataByBoundry = simplematch.match(add_string_list(boundry),rawString)

    caseStatus = parseCaseStatus(soup)
    caseDetail = caseDetailStatus(soup)
    petDetail = petDetailStatus(dataByBoundry['petDetail'])
    resDetail = resDetailStatus(dataByBoundry['resDetail'])
    propertyDetailListDic = propertyDetailList(soup)
    # print("property detail",propertyDetailListDic)
    caseProceedingDetaillistDic = caseProceedingDetaillist(soup)
    # print("Case proceeding detail",caseProceedingDetaillistDic)
    rcTcsCaseCurrentStatusDic = rcTcsCseCurrentStatus(dataByBoundry['rcTcsCaseCurrentStatus'])
    # print("rc/tcsCaseProceeding",rcTcsCaseCurrentStatusDic)
    rcCaseProceedingDetailListDic = rcCaseProceedingDetailList(soup)
    # print("rcCaseProceedingDetail",rcCaseProceedingDetailListDic)
    # print(caseStatus)
    # print(caseDetail)
    # print(petDetail)
    # print(resDetail)
    table_dic.update(caseStatus)
    # print(dataByBoundry)
    case_no_type_yearDic = simplematch.match("{case_type}/{case_number:int}/{case_year:int}",caseStatus['case_type_case_no_year'])
    table_dic['case_status'] = caseStatus['case_status'].upper()
    table_dic['case_detail'] = caseDetail
    table_dic.update(case_no_type_yearDic)
    table_dic['petioner_advocates'] = petDetail['pet_adv']
    table_dic.update(petDetail)
    table_dic['petitioner_advocates'] = [petDetail['pname'],"Advocate - "+petDetail['pet_adv']]
    table_dic['respondent_advocates'] = [resDetail['rname'],"Advocate - "+resDetail['res_adv']]
    table_dic['title'] =  '{} vs {}'.format(petDetail['pname'],resDetail['rname'])
    table_dic['listing_details'] = caseProceedingDetaillistDic
    table_dic['petitioner_details'] = petDetail
    table_dic['respondent_details'] = resDetail
    table_dic['property_details'] = propertyDetailListDic
    table_dic['rc_tcs_case_current_status'] = rcTcsCaseCurrentStatusDic
    table_dic['rc_proceeding_detail'] = rcCaseProceedingDetailListDic
    table_dic['unique_id'] = "tribunal-drt-" + caseStatus['case_type_case_no_year'] # to be dynamic
    if(caseDetail.get('next_listing_date')):
        table_dic['hearing_date'] = [pendulum.from_format(normalize_text(caseDetail['next_listing_date']),'DD/MM/YYYY')]
    else:
        table_dic['hearing_date'] = ''    
    return table_dic
    # table_dic.update()
def main():
    # url = "https://drt.etribunals.gov.in/drtlive/Misdetailreport.php?no=MDkwMTIwMDAxMDEyMDIyL2x1Y2tub3c="
    # url = "https://drt.etribunals.gov.in/drtlive/Misdetailreport.php?no=MDkwMTIwMDA5MTgyMDIzL2x1Y2tub3c="
    # url ="https://drt.etribunals.gov.in/drtlive/Misdetailreport.php?no=MDkwMTIwMDAwODUyMDIyL2x1Y2tub3c="
    # url ="https://drt.etribunals.gov.in/drtlive/Misdetailreport.php?no=MDkwMTIwMDAwOTAyMDIyL2x1Y2tub3c="
    # url ="https://drt.etribunals.gov.in/drtlive/Misdetailreport.php?no=MDkwMTIwMDAwOTAyMDIyL2x1Y2tub3c="
    # url ="https://drt.etribunals.gov.in/drtlive/Misdetailreport.php?no=MDkwMTIwMDAxMDcyMDIyL2x1Y2tub3c="
    url ="https://drt.etribunals.gov.in/drtlive/Misdetailreport.php?no=MDkwMTIwMDA1NjAyMDIyL2x1Y2tub3c="
    html_ = get_html_from_url(url)
    # with open('code.html','w+') as f:
    #     f.write(html_)
    print(parse_table(html_))    
        # f.close()

main()


# case_details
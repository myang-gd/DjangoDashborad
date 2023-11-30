import pyodbc
import requests
import uuid


class CardRetrieverdbDatabase(object):
    def execute_sp(self, query, values):
        conn_string = 'Driver={SQL Server Native Client 11.0};Server=GDCQAAUTOSQL201;' \
                      'Database=card_retriever_db;uid=qa_automation;pwd=Gr33nDot!;'

        data = []
        SQL_ATTR_CONNECTION_TIMEOUT = 113
        login_timeout = 60
        connection_timeout = 180
        with pyodbc.connect(conn_string, timeout=login_timeout,
                            attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout}) as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                data.append({columns[i]: str(row[i]) for i in range(len(columns))})
            # getCVV and update CVV
            print("Env: " + values[0])
            print("IsPersonalized: " + values[2])
            print("CardNo: " + data[0]['CardNo'])
            cvv = self.aci_getCVV_byService(values[0], data[0]['CardNo'], values[2])
            data[0].update({'CardCVV2': cvv})
            # getDOB and updated DOB
            dob = self.aci_getDOB(data[0]['DOBEncryptionKey'])
            data[0].update({'DOBEncryptionKey': dob})
            # getSSN and updated SSN
            ssn = self.aci_getSSN(data[0]['SSNToken'])
            data[0].update({'SSNToken': ssn})
        return data

    def aci_cardinfo_sp(self, env, serialNbr, isPersonalized):
        sql = """\
        EXEC [card_retriever_db].[dbo].[GetdCardInfo_ACI] @pDestinationDatabase=?, @pSerialNbr=?, @pIsPersonalized=?;
        """
        values = (env, serialNbr, isPersonalized)
        return self.execute_sp(sql, values)

    def aci_getCVV_byService(self, env, PAN, isPersonalized):
        url_id = "https://qa-gen-apim.go2bankonline.net/aciproxy/v1/account-management/accounts/" + PAN
        SubscriptionKey = "7d084c488a774591a85c9865c6d95cc2"

        if (env == "QA3") | (env == "PIE"):
            url_id = "https://pie-gen-apim.go2bankonline.net/aciproxy/v1/account-management/accounts/" + PAN
            SubscriptionKey = "3db7a1d79c444c4a973fb15fbb438c54"
        headers = {'X-Request-Id': str(uuid.uuid4()), 'Ocp-Apim-Subscription-Key': SubscriptionKey}
        # get id
        response = requests.get(url_id, headers=headers)
        jsonResponse = response.json()
        id = jsonResponse["rawResponse"]["GR008011"]["repeatingGroupOut-1"]["repeatingGroupInstanceOut-1"][0][
            "GeDmAccountGR008011Subset0001"]["id"]
        print("card_id: " + id)

        # get cvv
        url_cvv = "https://qa-gen-apim.go2bankonline.net/aciproxy/v1/card-management/cards/" + id + "/cvv"
        if (env == "QA3") | (env == "PIE"):
            url_cvv = "https://pie-gen-apim.go2bankonline.net/aciproxy/v1/card-management/cards/" + id + "/cvv"
        headers = {'X-Request-Id': str(uuid.uuid4()), 'Ocp-Apim-Subscription-Key': SubscriptionKey}
        response = requests.get(url_cvv, headers=headers)
        jsonResponse = response.json()
        cardVerification2 = \
        jsonResponse["rawResponse"]["DR010004"]["repeatingGroupOut-1"]["repeatingGroupInstanceOut-1"][int(isPersonalized)][
            "GeDmApplicationDR010004Subset0001"]["cardVerification2"]
        print("CVV: " + cardVerification2)
        return cardVerification2

    def aci_getSSN(self, SSNToken):
        url_SSN = "https://tknsvc/PersonalIdTokenizer/v1/Detokenize"
        headers = {'Accept-Encoding': 'gzip,deflate,br', 'Content-Type': 'application/json'}
        bodys = {'PersonalIdToken': SSNToken}
        response = requests.post(url_SSN, headers=headers, json=bodys, verify=False)
        ssn = response.json()["PersonalId"]
        print("ssn: " + ssn)
        return ssn

    def aci_getDOB(self, DOBEncryptionKey):
        url_DOB = "http://gdqaenvtools/DBAssistant/DBAssistantService.svc/rest/QA4/DecryptDOB/" + DOBEncryptionKey
        response = requests.get(url_DOB, verify=False)
        DOB = response.json()["DOB"]
        print("DOB: " + DOB)
        return DOB


tr = CardRetrieverdbDatabase()
print(tr.aci_cardinfo_sp('QA4', 'KW o/Zz>qD', '1'))
#print(tr.aci_cardinfo_sp('QA4', 'KW o/Zz>qD', '0'))

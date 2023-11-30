from common_utils.encryption import EncryptionUtil
from common_utils.processor import request_processor 
from apps.qa_monitor.models import Operation
from common_utils.json_util import JsonUtil
from io import BytesIO
import base64 
import json
import uuid
class FWUtil:
    
    @classmethod
    def GenerateEncodedString(cls, source, target, amount, currencyCode, transferIdentifier) -> str:       
        bytesIo  = BytesIO()
        encode_str = 'utf-8'
        bytesIo.write(source.encode(encode_str))
        bytesIo.write(target.encode(encode_str))
        bytesIo.write(amount.encode(encode_str))
        bytesIo.write(currencyCode.encode(encode_str))
        bytesIo.write(transferIdentifier.encode(encode_str))
        
        return base64.urlsafe_b64encode(EncryptionUtil.ComputeSHA256Bytes(bytesIo.getvalue())).decode(encode_str).replace('_','/').replace('-','+')
    
    @classmethod
    def GetSignature(cls, encodedstring, env_id):
        signature = ''
        operationObj = Operation.objects.get(name="ComputeSignature",environment__id=env_id)
        request_json =json.loads(operationObj.requestMessage)
        request_json['requestHeader']['requestId'] = str(uuid.uuid1())
        request_json['data'] = encodedstring
        request_msg = json.dumps(request_json, indent=4, sort_keys=True)
        result = request_processor(10, operationObj.id, surpass_msg=request_msg) 
        response = JsonUtil.safe_loads(result.response)
        if 'signature' in response:
            signature = response['signature']
        return signature
    
    @classmethod
    def changeTransfersP2PMessage(cls, operation_id, env_id):
        operationObj = Operation.objects.get(id=operation_id)
        request_json =json.loads(operationObj.requestMessage)
        source = request_json['components'][0]['source']['accountIdentifier'] 
        target = request_json['components'][0]['target']['accountIdentifier'] 
        amount = request_json['components'][0]['transactionAmount']
        currencyCode = request_json['components'][0]['currencyCode'] 
        transferIdentifier = str(uuid.uuid1())
        encodedstring = cls.GenerateEncodedString(source, target, amount, currencyCode, transferIdentifier)
        
        signature = cls.GetSignature(encodedstring, env_id)
        
        if transferIdentifier:
            request_json['components'][0]['transferIdentifier'] = transferIdentifier
        if signature:
            request_json['components'][0]['signature'] = signature
        request_msg = json.dumps(request_json, indent=4, sort_keys=True)
        
        return request_msg
        
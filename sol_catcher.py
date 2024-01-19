import json
import requests
import base64
import os
import time
from abstract_utilities import safe_dump_to_file,safe_read_from_json
def break_down_find_existing(path):
    test_path = ''
    for part in path.split(os.sep):
        test_path = os.path.join(test_path, part)
        if not os.path.exists(test_path):
            return test_path if test_path else None
    return test_path

def string_in_keys(strings, kwargs):
    return next((key for key in kwargs if any(s in key for s in strings)), None)

def get_path(paths):
    for path in paths:
        if isinstance(path,str):
            if os.path.splitext(path)[1]:
                return break_down_find_existing(path)
    return None

def check_read_write_params(file_path=None, contents=None, *args, **kwargs):
    if file_path == None:
        file_path = string_in_keys(['file_path', 'path'], kwargs) or get_path(args)
    if contents==None:
        contents_key = string_in_keys(['contents', 'data','json_data', 'text', 'content', 'string'], kwargs)
        contents = kwargs.get(contents_key) if contents_key else next((arg for arg in args if arg != file_path), None) 
    return file_path,contents
def safe_read_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading from JSON: {e}")
        return safe_json_loads(read_from_file(file_path))
def all_try(function=None, data=None, var_data=None, error=False, error_msg=None, error_value=Exception, attach=None, attach_var_data=None):
    try:
        if not function:
            raise ValueError("Function is required")

        if var_data and not data:
            result = function(**var_data)
        elif data and not var_data:
            if attach and attach_var_data:
                result = function(data).attach(**attach_var_data)
            else:
                result = function(data).attach() if attach else function(data)
        elif data and var_data:
            raise ValueError("Both data and var_data cannot be provided simultaneously")
        else:
            result = function()

        return result
    except error_value as e:
        if error:
            raise e
        elif error_msg:
            print_error_msg(error_msg, f': {e}')
        return False
def all_try_json_loads(data, error=False, error_msg=None, error_value=(json.JSONDecodeError, TypeError)):
    return all_try(data=data, function=json.loads, error=error, error_msg=error_msg, error_value=error_value)

def safe_json_loads(data, default_value=None, error=False, error_msg=None): 
    """ Safely attempts to load a JSON string. Returns the original data or a default value if parsing fails.
    Args:
        data (str): The JSON string to parse.
        default_value (any, optional): The value to return if parsing fails. Defaults to None.
        error (bool, optional): Whether to raise an error if parsing fails. Defaults to False.
        error_msg (str, optional): The error message to display if parsing fails. Defaults to None.
    
    Returns:
        any: The parsed JSON object, or the original data/default value if parsing fails.
    """
    if isinstance(data,dict):
        return data
    try_json = all_try_json_loads(data=data, error=error, error_msg=error_msg)
    if try_json:
        return try_json
    if default_value:
        data = default_value
    return data
def safe_dump_to_file(file_path:str=None, data:(dict or list or str)=None, ensure_ascii=False, indent=4,*args, **kwargs):
    params = check_read_write_params(file_path=file_path,contents=data, *args, **kwargs)
    if params:
        if isinstance(params[1], (dict, list, tuple)):
            with open(params[0], 'w', encoding='utf-8') as file:
                json.dump(params[1], file, ensure_ascii=ensure_ascii, indent=indent)
        else:
            with open(params[0], 'w', encoding='utf-8') as file:
                file.write(str(params[1]))
def exponent(integer,exp):
    return float(integer)*float(10**(-int(exp)))
def get_values(obj,chase=[]):
    for key,value in obj.items():
        chase.append(key)
        if isinstance(value,dict):
            get_values(value,chase)
        else:
            if key == 'postBalances':
                chase=[]
            print(key,':',value)
def get_acct_index(txn_details,acct_index):
    for each in txn_details:
        if each['accountIndex'] == acct_index:
            return each
def get_token_amount(txn_details=None):
    txn_details = txn_details or self.txn_details
    amount = txn_details['uiTokenAmount']['amount']
    decimals = txn_details['uiTokenAmount']['decimals']
    return exponent(amount,decimals) 
class requestManager:
    def __init__(self):
        self.rest = 5
        self.last_call= time.time()
    def get_rest_time(self):
        difference = time.time()-self.last_call
        sleep_time = 5 - difference
        if sleep_time>0:
            time.sleep(sleep_time)
    def solana_rpc_call(self,method, params=None):
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params if params is not None else [],
        }
        rpc_url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        self.get_rest_time()
        response = requests.post(url=rpc_url, data=json.dumps(request_data), headers=headers)
        self.last_call=time.time()
        return response.json()

class solCatcher:
    def __init__(self,program_id,liquidity_pool,program_executable_data=None,authority=None,upgrade_authority=None,entity_name="raydium",request_mgr=None,open_scanner=False,print_different = True,file_path = os.path.join(os.getcwd(),'sol_catcher.json')):
        self.request_mgr = request_mgr or requestManager()
        self.file_path = file_path
        self.print_different =print_different
        self.open_scanner= open_scanner
        self.program_id = program_id
        self.liquidity_pool = liquidity_pool
        self.program_executable_data = program_executable_data
        self.authority = authority
        self.upgrade_authority = upgrade_authority
        self.entity_name = 'Raydium'
        self.Solana_mint = 'So11111111111111111111111111111111111111112'
        self.all_known = {"program_id":self.program_id,"liquidity_pool":self.liquidity_pool,"program_executable_data":self.program_executable_data,"authority":self.authority,"upgrade_authority":self.upgrade_authority,"Sol":self.Solana_mint}
        self.all_known_lower={}
        for key,value in self.all_known.items():
            self.all_known_lower[key]=value.lower()
        self.fetch_transactions(self.upgrade_authority, self.program_id)
    def label_addresses(self,address,owner=None,programId=None,mint=None):
        variables_js = {"address":address,"owner":owner,"programId":programId,"mint":mint}
        for subject_key,subject_value in variables_js.items():
            if subject_value:
                if subject_value.lower() in list(self.all_known_lower.values()):
                    for known_key,known_value in self.all_known_lower.items():
                        if subject_value.lower() == known_value:
                            variables_js[subject_key] = known_key
                   
                            break
        
	#print(f"token: {mint}, owner: {owner}, programId:{programId}")
	#print(f'in: {before}\nout: {after}\nchange: {difference}')
        return variables_js["address"],variables_js["owner"],variables_js["programId"],variables_js["mint"]
    def fetch_transaction_details(self,signature=None):
        response = self.request_mgr.solana_rpc_call("getTransaction", params=[self.signature,{"maxSupportedTransactionVersion":0}])
        if response and response.get('result'):
            return response.get('result')
        else:
            print(f"Failed to fetch details for transaction: {signature}")
            return None
    def relay_token_balances(self):
        tally = []
        totals_js={}
        if not os.path.isfile(self.file_path):
            safe_dump_to_file(data = {'sol_txns':{"headers":"Address\tBalance Before\tBalance After\tChange".split('\t') ,"txns":[]},'token_txns':{'headers':'Address\tOwner\tBalance Before\tBalance After\tChange\tToken'.split('\t'),"txns":[]}},file_path  = self.file_path)
        self.all_txns= safe_read_from_json(file_path = self.file_path)
        balance=[]
        sums=0
        for token in ['', 'Token']:
            pre_tok = self.meta[f'pre{token}Balances']
            post_tok = self.meta[f'post{token}Balances']
            if token == '':
                sums=0
                balance = []
                print(f"block_number {self.txn_details['slot']}")
                print("SOLANA TXNS:")
                print(self.all_txns['sol_txns']["headers"])
                for i, amt in enumerate(pre_tok):
                    totals_js={}
                    balance.append([exponent(amt ,9),-exponent(post_tok[i] ,9)])
                    if len(self.acct_keys)==i:
                        add_acct_keys = self.txn_details['meta'].get('loadedAddresses')
                        if 'readonly' in add_acct_keys:
                            add_acct_keys=add_acct_keys.get('readonly',add_acct_keys)
                        self.acct_keys+=add_acct_keys
                    address = self.acct_keys[i]
                    if self.print_different:
                        address,owner,programId,token=self.label_addresses(address)
                    totals_js['Address']=address
                    totals_js['Balance Before']=balance[-1][0]
                    totals_js['Balance After']=balance[-1][1]
                    totals_js['Change']= sum(balance[-1])
                    self.all_txns['sol_txns']["txns"].append(totals_js)
                    print(list(self.all_txns['sol_txns']["txns"][-1].values()))
            else:
                print("TOKEN TXNS:")
                print(self.all_txns['token_txns']["headers"])
                for each in pre_tok:
                    totals_js={}
                    index = each["accountIndex"]
                    address = self.all_txns['sol_txns']["txns"][index]['Address']
                    if each['owner'].lower() == self.upgrade_authority.lower() and each['mint']==self.Solana_mint:
                        input('new_pair')
                    if self.print_different:
                        address,each['owner'],each['programId'],each['mint']=self.label_addresses(address,each['owner'],each['programId'],each['mint'])
                    totals_js['Address']=self.all_txns['sol_txns']["txns"][index]['Address']
                    totals_js['owner']=each['owner']
                    totals_js['Balance Before']=get_token_amount(each)
                    totals_js['Balance After']=get_token_amount(get_acct_index(post_tok,index))
                    totals_js['Change']= totals_js['Balance Before']-totals_js['Balance After']
                    totals_js['token']=each['mint']
                    self.all_txns['token_txns']["txns"].append(totals_js)
                    if totals_js['owner'].lower() == self.upgrade_authority.lower():
                       new_pair = True
                       input(totals_js)     	
                       os.system(f"open https://solscan.io/tx/{txn['signature']}")
                       input(all_txns['token_txns']["txns"][-1])
                    
                    #print_different(totals_js['owner'],each['programId'],total_js['token'],totals_js['Balance Before'],totals_js['Balance After'],totals_js['Change'])
                    print(list(self.all_txns['token_txns']["txns"][-1].values()))
        print('\n\n')
        safe_dump_to_file(data = self.all_txns,file_path  =  self.file_path)
    def fetch_transactions(self,address=None, program_id=None):
        params = [
            address or self.iquidity_pool,
            {"limit": 1000}
        ]
        response = request_mgr.solana_rpc_call("getSignaturesForAddress", params)
        
        txn_list = response['result']
        
        spl_transactions = []
        for txn in txn_list:
            self.signature = txn['signature']
            self.txn_details = self.fetch_transaction_details()
            if self.txn_details:
                if self.open_scanner:
                        os.system(f"open https://solscan.io/tx/{txn['signature']}")
                self.meta = self.txn_details.get('meta')
                self.acct_keys = self.txn_details.get('transaction',{}).get('message',{}).get('accountKeys')
                self.relay_token_balances()
        return spl_transactions
program_id = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
liquidity_pool = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"  
program_executable_data = 'A7ZG7ByDi8DpzT9Ab7CiXhvgYTJQmaDPJkMDoPitaCQV'
authority = '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1'
upgrade_authority = 'GThUX1Atko4tqhN2NaiTazWSeFWMuiUvfFnyJyUghFMJ'
request_mgr = requestManager()

solCatcher(program_id=program_id,liquidity_pool=liquidity_pool,program_executable_data=program_executable_data,authority=authority,upgrade_authority=upgrade_authority,request_mgr=request_mgr,print_different=False)

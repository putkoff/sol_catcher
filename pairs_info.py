from solana.rpc.commitment import Commitment
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts
from abstract_security import get_env_value
def load_from_private_key(env_key='AMM_P'):
    env_value = get_env_value(key=env_key)
    if env_value:
        return Keypair.from_base58_string(env_value)
def get_user_pub_key():
    return load_from_private_key('AMM_P').pubkey()
def load_keypair_from_file(filename):
    curr = os.path.join(sys.path[0], 'data',  filename)
    with open(curr, 'r') as file:
        secret = json.load(file)
        secret_key = bytes(secret)
        # print(base58.b58encode(secret_key))
        return Keypair.from_bytes(secret_key)
def get_pub_key(address):
    if pubkey_type() != type(address):
        try:
            tokenPk = Pubkey.from_string(address)
            return tokenPk
        except Exception as e:
            print("public key could not be derived: {e}")
            return None
    return address
def pubkey_type():
    return type(Pubkey.from_string("6fvys6PkSCgZcrDCCkYp56BjLMKZ41ySZK6qtgzX49Hg"))
import requests, json, os, sys
"""I modified it to dexscreener, forgot to change the filename"""
def get_base_token(pair):
    if pair and isinstance(pair,list):
        pair=pair[0]
    if isinstance(pair,dict):
        return pair.get('baseToken')
def get_quote_token(pair):
    if pair and isinstance(pair,list):
        pair=pair[0]
    if isinstance(pair,dict):
        return pair.get('quoteToken')
def get_pair_address(pair):
    if pair and isinstance(pair,list):
        pair=pair[0]
    if isinstance(pair,dict):
        return pair.get('pairAddress')
def get_price_usd(pair):
    if pair and isinstance(pair,list):
        pair=pair[0]
    if isinstance(pair,dict):
        return pair.get('priceUsd')
def get_symbol(obj):
    if isinstance(obj,dict):
        return obj.get('symbol')
def get_address(obj):
    if isinstance(obj,dict):
        return obj.get('address')
def get_name(obj):
    if isinstance(obj,dict):
        return obj.get('name')
def get_pair_pairs(url):
    response = requests.get(url).json()
    if isinstance(response,dict):
        return response.get('pair'),response.get('pairs')
    return None,None
def api_call_pairs(token_address):
    url =  f"https://api.dexscreener.com/latest/dex/pairs/solana/{token_address}"
    return get_pair_pairs(url)
def api_call_tokens(token_address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    return get_pair_pairs(url)
def api_call_token(token):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token}"
    return get_pair_pairs(url)
"""
USDT and USDC prices will be excluded
"""
def get_price(token_address):
    exclude = ['EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB']
    pair,pairs = api_call_tokens(token_address)
    if pairs and token_address not in exclude:
        for pair in pairs:
            if get_address(get_quote_token(pair)) == 'So11111111111111111111111111111111111111112':
                return float(get_price_usd(pair))
    elif pair:
        return float(get_price_usd(pair))
    return None
def getBaseToken(pair_address):
    pair,pairs=api_call_pairs(pair_address)
    return get_base_token(pair)


"""Common addresses like usdc and usdt will be excluded as we know their symbols"""
def getSymbol(token):
    # usdc and usdt
    exclude = ['EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB']
    if token not in exclude:
        Token_Symbol = ""
        Sol_symbol=""
        try:
            # Check if the request was successful (status code 200)
            pair,pairs = api_call_token(token)
            if pairs and isinstance(pairs,list):
                base_token = get_symbol(get_base_token(pairs))
                for pair in pairs:
                    quoteToken = get_symbol(get_quote_token(pair))
                    if quoteToken == 'SOL':
                        Token_Symbol = get_symbol(get_base_token(pair))
                        Sol_symbol = quoteToken
                        return Token_Symbol, Sol_symbol


            else:
                print(f"[getSymbol] Request failed with status code {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[getSymbol] error occurred: {e}")
        except: 
            a = 1

        return Token_Symbol, Sol_symbol
    else:
        if token == 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v':
            return "USDC", "SOL"
        elif token == 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v':
            return "USDT", "SOL"

def print_json(json_obj):
    for key,value in json_obj.items():
        if isinstance(value,dict):
            print_json(value)
        else:
            print(f"{key}: {value}")
def get_token_specs(obj):
    json_dict = {"address":get_address(obj),"name":get_name(obj),"symbol":get_symbol(obj)}
    print_json(json_dict)
    return json_dict
def get_pair_objs(address):
    pair,pairs = api_call_pairs(address)
    obj = pair or pairs
    json_dict = {"pair_address":get_pair_address(obj),"quote_token":get_quote_token(obj),"base_token":get_base_token(obj)}
    print_json(json_dict)
    return json_dict
rpc="https://api.mainnet-beta.solana.com/"
ctx = Client(rpc, commitment=Commitment("confirmed"), timeout=30, blockhash_cache=True)
def get_pair_info(address):
    public_key = get_pub_key(address)
    accountProgramId = ctx.get_account_info_json_parsed(public_key)
    programid = accountProgramId.value.owner
    print_json({"address":address,"public_key":public_key,"programid":programid})
    return getBaseToken(pair_address)
def get_price_info(token_address):
    symbol = getSymbol(token_address)
    price = get_price(token_address)
    print_json({"symbol":symbol,"price":price})
def get_all_info(address):
    json_dict=get_pair_objs(address)
    return checkB(get_address(get_base_token(json_dict)), payer=load_from_private_key('AMM_P'), ctx=ctx)
def checkB(TOKEN_TO_SWAP_SELL, payer, ctx):
    if TOKEN_TO_SWAP_SELL:
        tokenPk = get_pub_key(TOKEN_TO_SWAP_SELL)
        accountProgramId = ctx.get_account_info_json_parsed(tokenPk)
        programid = accountProgramId.value.owner
        accounts = ctx.get_token_accounts_by_owner_json_parsed(payer.pubkey()  ,TokenAccountOpts(program_id=programid)).value
        for account in accounts:
            tokenBalanceLamports = int(account.account.data.parsed['info']['tokenAmount']['amount'])
            decimals = account.account.data.parsed['info']['tokenAmount']['decimals']
            mint = account.account.data.parsed['info']['mint']
            if tokenBalanceLamports > 0 and mint == TOKEN_TO_SWAP_SELL:
                return tokenBalanceLamports*10**(-decimals),mint,decimals,tokenBalanceLamports
def get_program_id(address):
    tokenPk = get_pub_key(address)
    accountProgramId = ctx.get_account_info_json_parsed(tokenPk)
    return accountProgramId.value.owner
def get_display(obj,total_js={}):
    if isinstance(obj,dict):
        for key,value in obj.items():
            if isinstance(value,dict):
                total_js=get_display(value,total_js)
            else:
                if key in total_js and value != total_js[key]:
                    input(total_js[key])
                total_js[key]=value
    return total_js
def get_total_address_amounts(account):
    total_js = get_display(account,{})
    total_js = get_display(account.account.data.parsed['info'],total_js)
    return get_display(account.account.data.parsed['info']['tokenAmount'],total_js)
def get_account_info(address):
    accounts = ctx.get_token_accounts_by_owner_json_parsed(get_pub_key(address)  ,TokenAccountOpts(program_id=get_program_id(address)))
    total_accounts=[]
    if accounts:
        accounts=accounts.value
        for account in accounts:
            total_js = get_total_address_amounts(account)
            if total_js not in total_accounts:
                total_accounts.append(total_js)
            tokenBalanceLamports = int(account.account.data.parsed['info']['tokenAmount']['amount'])
            decimals = account.account.data.parsed['info']['tokenAmount']['decimals']
            mint = account.account.data.parsed['info']['mint']
            if tokenBalanceLamports > 0 and mint == address:
                return tokenBalanceLamports*10**(-decimals),total_accounts
    return total_accounts
pair_address = "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"
input(get_program_id(pair_address))
programid = accountProgramId.value.owner
address = get_pub_key(pair_address)
get_account_info(address)

input(get_account_info(pair_address))
#get_all_info("6fvys6PkSCgZcrDCCkYp56BjLMKZ41ySZK6qtgzX49Hg")






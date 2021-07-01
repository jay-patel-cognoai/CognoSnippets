from EasyChatApp.utils import *
from EasyChatApp.models import *
from django.utils import timezone as tz
import json
import requests
import sys
import time
from datetime import date, datetime
# import emoji

log_param={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'en', 'channel': 'WhatsApp', 'bot_id': 'None'}

#   utility functions:
# Calculate difference b/w datetime objects
def get_time_delta(date_str1, date_str2):
    delta_obj = {"minutes":0.0, "hours":0.0}
    try:
        from datetime import date, datetime
        if "." in date_str1:
            date_str1 = str(date_str1).split(".")[0]
        if "." in date_str2:
            date_str2 = str(date_str2).split(".")[0]
        date_str1 = datetime.strptime(date_str1, "%Y-%m-%d %H:%M:%S")
        date_str2 = datetime.strptime(date_str2, "%Y-%m-%d %H:%M:%S")
        delta = date_str2 - date_str1 # 2nd date is greater
        duration_in_s = delta.total_seconds()
        delta_obj = {
            "seconds":duration_in_s,
            "minutes":round(duration_in_s/60,1), #divmod(duration_in_s, 60)[0],
            "hours":divmod(duration_in_s, 3600)[0],
            "days":divmod(duration_in_s, 86400)[0],
            "years":divmod(duration_in_s, 31536000)[0]
        }
        return delta_obj
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_time_delta: %s at %s", str(E), str(exc_tb.tb_lineno), extra=log_param)
        return delta_obj


#   RML TOKEN :
    #   1. GET ROUTE MOBILE API KEY: 
def GET_API_KEY(username,password):
    API_KEY = ""
    try:
        logger.info("=== Inside RouteMobile_GET_API_KEY API ===", extra=log_param)
        # print("=== Inside RouteMobile_GET_API_KEY API ===")

        url = "https://apis.rmlconnect.net/auth/v1/login/"
        payload = {
            "username":username,
            "password":password
        }
        headers = {
            'Content-Type': 'application/json'
        }
        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=25, verify=True)
        logger.info("RouteMobile_GET_API_KEY Response: %s", str(r.text), extra=log_param)
        # print("RouteMobile_GET_API_KEY Response: %s", str(r.text))
        content = json.loads(r.text)

        if str(r.status_code) == "200" or str(r.status_code) == "201":
            API_KEY = content["JWTAUTH"]
    except requests.Timeout as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RouteMobile_GET_API_KEY Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("RouteMobile_GET_API_KEY Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RouteMobile_GET_API_KEY Failed: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("RouteMobile_GET_API_KEY Failed: %s at %s", str(e), str(exc_tb.tb_lineno))
    return API_KEY


    # 	2. CACHING ROUTE MOBILE API KEY:       
def GET_RML_JWT_TOKEN(username, password):
    API_KEY = None
    try:
        logger.info("=== Inside GET_RML_JWT_TOKEN (FOR PUSH MESSAGING)===", extra=log_param)
        token_obj = RouteMobileToken.objects.all()
        if token_obj.count() == 0:
            logger.info("--- token object not found", extra=log_param)
            logger.info("--- getting token from token API", extra=log_param)
            API_KEY = GET_API_KEY(username, password)
            token_obj = RouteMobileToken.objects.create(token=API_KEY)
        elif token_obj[0].token == None or token_obj[0].token == "" or token_obj[0].token == "token":
            logger.info("--- token object is None", extra=log_param)
            logger.info("--- getting token from token API", extra=log_param)
            API_KEY = GET_API_KEY(username, password)
            token_pk = token_obj[0].id
            token_obj = RouteMobileToken.objects.get(id=token_pk)
            token_obj.token = API_KEY
            token_obj.token_generated_on = tz.now()
            token_obj.save()
            logger.info("--- token object updated", extra=log_param)
        else:
            token_pk = token_obj[0].id
            token_generated_on = str(token_obj[0].token_generated_on)
            current_time = str(tz.now())
            time_diff = get_time_delta(str(token_generated_on), str(current_time))["minutes"]
            logger.info("--- Token Minutes:  %s", str(time_diff), extra=log_param)
            API_KEY = token_obj[0].token
            logger.info("--- getting token from cached db", extra=log_param)
            if float(time_diff) > 55.0:
                logger.info("--- token expired", extra=log_param)
                logger.info("--- getting token from token API", extra=log_param)
                API_KEY = GET_API_KEY(username, password)
                token_obj = RouteMobileToken.objects.get(id=token_pk)
                token_obj.token = API_KEY
                token_obj.token_generated_on = tz.now()
                token_obj.save()
                logger.info("--- token object updated", extra=log_param)
        logger.info("=== END GET_RML_JWT_TOKEN ===", extra=log_param)
        return API_KEY    
    except Exception as E:    
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GET_RML_JWT_TOKEN API  Failed: %s at %s", str(E), str(exc_tb.tb_lineno), extra=log_param)
        logger.info("=== END GET_RML_JWT_TOKEN ===", extra=log_param)
    return API_KEY


#   RML PUSH APIs (Template Based): 
    #   1. PUSH TEXT MESSAGE API:
def pushWhatsAppTextMessage(api_key, language, template_name, template_variables, phone_number):
    is_send = False
    message = ""
    try:
        logger.info("=== Inside Push Text Message API ===", extra=log_param)
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        body = []
        for var in template_variables:
            text = {}
            text["text"] = str(var)
            body.append(text)
        
        # print(body)
        payload = {
                "phone": "+"+phone_number,
                "media": {
                    "type": "media_template",
                    "template_name": template_name,
                    "lang_code": language,
                }
            }

        if body != []:
           payload["media"]["body"] = body

        # print(json.dumps(payload, indent=2)
        logger.info("pushWhatsAppTextMessage API Request: %s", str(payload), extra=log_param)
        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        logger.info("pushWhatsAppTextMessage API Response: %s", str(r.text), extra=log_param)
        logger.info("pushWhatsAppTextMessage API status code: %s", str(r.status_code), extra=log_param)

        # print("pushWhatsAppMediaMessage API Response: %s", str(r.text))
        content = json.dumps(r.text)
        if str(r.status_code) == "200" or str(r.status_code) == "202":
            logger.info("pushWhatsAppTextMessage API: Text message pushed succesfully", extra=log_param)
            # print("pushWhatsAppTextMessage API: Text message pushed succesfully")
            is_send = True
            message = "success"
        else:
            if str(r.status_code) == "400":
                message = "Message not sent. Error: variables not provided"
            if str(r.status_code) == "401":
                message = "Message not sent. Error: token  not generated"
            logger.error("pushWhatsAppTextMessage API: Failed to push Text Message.", extra=log_param)
            # print("pushWhatsAppTextMessage API: Failed to push Text Message.")
            is_send =  False
    except requests.Timeout as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppTextMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppTextMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: RML Send Text template API timeout"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppTextMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppTextMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: "+str(e)
    return message, is_send


    #   2.PUSH MEDIA MESSAGE API:
def pushWhatsAppMediaMessage(api_key, media_type, media_url, language, template_name, template_variables, phone_number):
    is_send = False
    message = ""
    try:
        logger.info("=== Inside Push Media Message API ===", extra=log_param)
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        body = []
        for var in template_variables:
            text = {}
            text["text"] = str(var)
            body.append(text)


        media_header = [{
            media_type: {
                'link':media_url
            }
        }]
        payload = {
            "phone": "+"+phone_number,
            "media": {
                "type": "media_template",
                "template_name": template_name,
                "lang_code": language,
                "header": media_header
            }
        }

        if body != []:
           payload["media"]["body"] = body

        payload_str = json.dumps(payload, indent=2)
        logger.info("pushWhatsAppMediaMessage API Request: %s", str(payload_str), extra=log_param)
        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        logger.info("pushWhatsAppMediaMessage API Response: %s", str(r.text), extra=log_param)
        logger.info("pushWhatsAppMediaMessageAPI API status code : %s", str(r.status_code), extra=log_param)
        # print("pushWhatsAppMediaMessageAPI Response: %s", str(r.text))
        content = json.dumps(r.text)
        if str(r.status_code) == "200" or str(r.status_code) == "202":
            logger.info("pushWhatsAppMediaMessage API: Media message pushed succesfully", extra=log_param)
            # print("pushWhatsAppMediaMessage API: Media message pushed succesfully")
            is_send = True
            message = "success"
        else:
            if str(r.status_code) == "400":
                message = "Message not sent. Error: variables not provided"
            if str(r.status_code) == "401":
                message = "Message not sent. Error: token  not generated"
            logger.error("pushWhatsAppMediaMessage API:  Failed to push Media Message.", extra=log_param)
            # print("pushWhatsAppMediaMessage API: Failed to push Media Message.")
            is_send =  False
    except requests.Timeout as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppMediaMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppMediaMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: RML Send Text template API timeout"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppMediaMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppMediaMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: "+str(e)
    return message, is_send


    #   3. PUSH CTA MESSAGE API:
def pushWhatsAppCTAMessage(api_key, language, template_name, phone_number, template_variables=None, dynamic_urls=None, media_type=None, media_url=None):
    import sys
    import json
    import requests
    import time
    is_send = False
    message = ""
    try:
        logger.info("=== Inside Push CTA Message API ===", extra=log_param)

        url = "https://apis.rmlconnect.net/wba/v1/messages"

        headers = {
              'Content-Type': 'application/json',
              'Authorization': api_key
        }

        payload = {
            "phone": "+"+phone_number,
            "media": {
            "type": "call_to_action",
            "template_name": template_name,
            "lang_code": language
            }
        }

        #   Media(image/video/document) in CTA:
        if media_type != None and media_url!= None and media_type in ["image","document","video"]:
            payload["media"]["header"] = [{
                media_type : {
                    "link": media_url
                }
            }]            

        #   Text Variables
        if template_variables != None and len(template_variables) > 0:
            payload["media"]["body"] = []
            for var in template_variables:
                payload["media"]["body"].append({
                    "text":var
                })

        #   Dynamic URLS in button
        if dynamic_urls != None and len(dynamic_urls)>0:
            payload["media"]["button"] = []
            for i,durl in enumerate(dynamic_urls):
                payload["media"]["button"].append({
                    "button_no": str(i),
                    "url": str(durl)
                })


        # print("pushWhatsAppCTAMessage API Request: %s", str(payload))
        logger.info("pushWhatsAppCTAMessage API Request: %s", str(payload), extra=log_param)

        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        logger.info("pushWhatsAppCTAMessage API Response: %s", str(r.text), extra=log_param)
        logger.info("pushWhatsAppCTAMessage API status code: %s", str(r.status_code), extra=log_param)

        # print("pushWhatsAppCTAMessage API Response: %s", str(r.text))
        content = json.dumps(r.text)
        if str(r.status_code) == "200" or str(r.status_code) == "202":
            logger.info("pushWhatsAppCTAMessage API: CTA message pushed succesfully", extra=log_param)
            #print("pushWhatsAppCTAMessage API: CTA message pushed succesfully")
            is_send = True
            message = "success"
        else:
            if str(r.status_code) == "400":
                message = "Message not sent. Error: variables not provided"
            if str(r.status_code) == "401":
                message = "Message not sent. Error: token  not generated"
            logger.error("pushWhatsAppCTAMessage API: Failed to push CTA Message.", extra=log_param)
            # print("pushWhatsAppCTAMessage API: Failed to push CTA Message.")
            is_send =  False
    except requests.Timeout as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppCTAMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppCTAMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: RML Send CTA template API timeout"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppCTAMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppCTAMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: "+str(e)
    return message, is_send


    #   4. PUSH Quick Reply MESSAGE API:
def pushWhatsAppQuickReplyMessage(api_key, language, template_name, phone_number, template_variables=None, media_type=None, media_url=None):
    import sys
    import json
    import requests
    import time
    is_send = False
    message = ""
    try:
        logger.info("=== Inside Push Quick Reply Message API ===", extra=log_param)

        url = "https://apis.rmlconnect.net/wba/v1/messages"

        headers = {
              'Content-Type': 'application/json',
              'Authorization': api_key
        }

        payload = {
            "phone": "+"+phone_number,
            "media": {
            "type": "quick_reply",
            "template_name": template_name,
            "lang_code": language
            }
        }

        #   Media(image/video/document) in QuickReply:
        if media_type != None and media_url!= None and media_type in ["image","document","video"]:
            payload["media"]["header"] = [{
                media_type : {
                    "link": media_url
                }
            }]            

        #   Text Variables
        if template_variables != None and len(template_variables) > 0:
            payload["media"]["body"] = []
            for var in template_variables:
                payload["media"]["body"].append({
                    "text":var
                })

        # print("pushWhatsAppQuickReplyMessage API Request: %s", str(payload))
        logger.info("pushWhatsAppQuickReplyMessage API Request: %s", str(payload), extra=log_param)

        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        logger.info("pushWhatsAppQuickReplyMessage API Response: %s", str(r.text), extra=log_param)
        logger.info("pushWhatsAppQuickReplyMessage API status code: %s", str(r.status_code), extra=log_param)

        # print("pushWhatsAppQuickReplyMessage API Response: %s", str(r.text))
        content = json.dumps(r.text)
        if str(r.status_code) == "200" or str(r.status_code) == "202":
            logger.info("pushWhatsAppQuickReplyMessage API: Quick Reply message pushed succesfully", extra=log_param)
            # print("pushWhatsAppQuickReplyMessage API: Quick Reply message pushed succesfully")
            is_send = True
            message = "success"
        else:
            if str(r.status_code) == "400":
                message = "Message not sent. Error: variables not provided"
            if str(r.status_code) == "401":
                message = "Message not sent. Error: token  not generated"
            logger.error("pushWhatsAppQuickReplyMessage API: Failed to push quick reply Message.", extra=log_param)
            # print("pushWhatsAppQuickReplyMessage API: Failed to push quick reply Message.")
            is_send =  False
    except requests.Timeout as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppQuickReplyMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppQuickReplyMessage API Timeout error: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: RML Send Quick Reply template API timeout"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pushWhatsAppQuickReplyMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("pushWhatsAppQuickReplyMessage API Failed: %s at %s", str(e), str(exc_tb.tb_lineno))
        is_send = False
        message = "Message not sent. Error: "+str(e)
    return message, is_send


# =======================================================================================================================


#   RML PUSH APIs (Session Based): 
    #   1. WHATSAPP SEND TEXT MESSAGE API:
def sendWhatsAppTextMessage(api_key, message, phone_number, preview_url=False):
    import requests
    import urllib
    try:
        logger.info("=== Inside Send WA Text Message API ===", extra=log_param)
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        payload = {
            "phone": "+"+phone_number,
            "text": message
        }
        if preview_url == True:
        	payload["preview_url"] = True
        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        content = json.dumps(r.text)
        logger.info("Send WA Text API Response: %s", str(content), extra=log_param)
        if str(r.status_code) == "200" or str(r.status_code) == "202":
            logger.info("Text message sent succesfully", extra=log_param)
            return True
        else:
            logger.error("Failed to Send Text Message.", extra=log_param)
            return False
    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(RT) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Timeout error: %s", str(RT), str(exc_tb.tb_lineno), extra=log_param)
        return False    
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Failed: %s", str(E), str(exc_tb.tb_lineno), extra=log_param)
    return False


    #   2. WHATSAPP SEND MEDIA MESSAGE API:
def sendWhatsAppMediaMessage(api_key, media_type, media_url, phone_number, caption = None):
    import requests
    import urllib
    try:
        logger.info("=== Inside Send WA Media Message API ===", extra=log_param)
        logger.info("Media Type: %s", media_type, extra=log_param)
        if media_type == "document" and caption == None:
            caption = "FileAttachment"
        elif caption == None:
            caption = ""
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "phone": "+"+phone_number,
            "media": {
                "type": media_type,
                "url": media_url,
                "file": media_url.split("/")[-1],
                "caption": caption
            }
        }
        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        content = json.dumps(r.text)
        logger.info("Send WA "+media_type.upper()+" API Response: %s", str(content), extra=log_param)
        if str(r.status_code) == "200" or str(r.status_code) == "202":
            logger.info(media_type.upper()+" message sent successfully", extra=log_param)
            return True
        else:
            logger.error("Failed to send "+media_type.upper()+" message: %s", extra=log_param)
            return False
    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(RT) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Timeout error: %s", str(RT), str(exc_tb.tb_lineno), extra=log_param)
        return False    
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Failed: %s", str(E), str(exc_tb.tb_lineno), extra=log_param)
    return False


# =======================================================================================================================


#   Check OPT Status:
def check_opt_status(mobile_number):
    logger.info(f"checking opt status for {mobile_number}...", extra=log_param)
    status = False
    try:
        # Consent/OPT Status Checking code here:
        return status
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_opt_status Failed: %s at %s", str(E), str(exc_tb.tb_lineno), extra=log_param)
    return status


#   Send Template Based Push Message (Generic Function):
def send_push_message(template_name, template_type, template_language, template_variables, mobile_number, media_url=None, button_urls=None):
    rm_username = ""
    rm_password = ""
    API_KEY = GET_RML_JWT_TOKEN(rm_username, rm_password)
    push_status = {
        "target_mobile_number":mobile_number,
        "push_message_sent": False,
    }
    is_send = False
    try:
        if mobile_number == "":
           push_status["error_message"] = "Message not sent. Error: customer mobile number is mandatory."
           return push_status

        if template_type == "text":
           error_message,is_send = pushWhatsAppTextMessage(api_key=API_KEY, language=template_language, template_name=template_name, template_variables=template_variables, phone_number=mobile_number)

        elif template_type in ["image", "document", "video"]:
           error_message,is_send = pushWhatsAppMediaMessage(api_key=API_KEY, media_type=template_type, media_url=media_url, language=template_language, template_name=template_name, template_variables=template_variables, phone_number=mobile_number)

        elif template_type == "quick_reply":
            error_message, is_send = pushWhatsAppQuickReplyMessage(api_key=API_KEY, language=template_language, template_name=template_name, phone_number=mobile_number, template_variables=template_variables, media_type=None, media_url=None)

        elif template_type.replace("quick_reply_","") in ["image", "document", "video"]: # e.g "quick_reply_image, quick_reply_video, quick_reply_document"
            error_message, is_send = pushWhatsAppQuickReplyMessage(api_key=API_KEY, language=template_language, template_name=template_name, phone_number=mobile_number, template_variables=template_variables, media_type=template_type.replace("quick_reply_",""), media_url=media_url)

        elif template_type == "cta":
            error_message, is_send = pushWhatsAppCTAMessage(api_key=API_KEY, language=template_language, template_name=template_name, phone_number=mobile_number, template_variables=template_variables, dynamic_urls=button_urls, media_type=None, media_url=None)

        elif template_type.replace("cta_","") in ["image", "document", "video"]: # e.g "cta_reply_image, cta_reply_video, cta_reply_document"
            error_message, is_send = pushWhatsAppCTAMessage(api_key=API_KEY, language=template_language, template_name=template_name, phone_number=mobile_number, template_variables=template_variables, dynamic_urls=button_urls, media_type=template_type.replace("cta_",""), media_url=media_url)

        if is_send == True:
           push_status["push_message_sent"] = True
        else:
           push_status["error_message"] = error_message

    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_push_message Failed: %s at %s", str(E), str(exc_tb.tb_lineno), extra=log_param)
        push_status["error_message"] = "Message not sent. Error: "+str(E)
    logger.error("send_push_message details: %s", str(push_status), extra=log_param)
    return push_status

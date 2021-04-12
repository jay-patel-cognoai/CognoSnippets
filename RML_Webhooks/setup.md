# Steps to enable RML WA Webhook

1. Give easychat webhook url to RML vendor for configuration.
    e.g https://easychat-dev.allincall.in/chat/webhook/whatsapp/?bot_id=46&bot_name=uat

    You will find this url in Bot channel 's WhatsApp configuration.
    if the console domain name is different replace `easychat-dev.allincall.in` with your console's domain.

2. RML will provide the following:
    a. WhatsApp Bot Mobile Number
    b. Username
    c. Password

3. Inside `whatsapp_webhook` function,
    change  `response["mobile_number"] = "whatsappbot_mobile_number"`
    change  `rm_username = "rml_username"`
            `rm_password = "rml_password"`

4. API Key Caching:
    By default RML 
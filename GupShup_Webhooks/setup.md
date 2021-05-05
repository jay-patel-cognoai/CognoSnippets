# Steps to enable Gupshup WA Webhook

1. Give easychat webhook url to gupshup vendor for configuration.
    e.g https://easychat-dev.allincall.in/chat/webhook/whatsapp/?bot_id=46&bot_name=uat

    You will find this url in Bot channel 's WhatsApp configuration.
    if the console domain name is different replace `easychat-dev.allincall.in` with your console's domain.

2. Copy paste `gupshup_WA_Webhook.py` code.

3. gupshup will provide the following:
    a. WhatsApp Bot Mobile Number
    b. AUTHENTICATION NUMBER
    c. AUTHENTICATION KEY

4. Inside `whatsapp_webhook` function,

    change  `response["mobile_number"] = "whatsappbot_mobile_number"` (before try block)

    change  `AUTHENTICATION_NUMBER = "gupshup_AUTHENTICATION_NUMBER_provided"`
            `AUTHENTICATION_KEY = "gupshup_AUTHENTICATION_KEY_provided"`

# Steps to enable GupShup WA LiveChat
1. After GupShup WA Webhook setup completion and assuming LiveChat is already enabled in the bot configuration, copy paste `gupshup_LiveChatBotChannelwebhook.py` into LiveChatBotChannelWebhook model object from Admin panel.

2. Inside `def f(x)` change the credentials as:
    change  `AUTHENTICATION_NUMBER = "gupshup_AUTHENTICATION_NUMBER_provided"`
            `AUTHENTICATION_KEY = "gupshup_AUTHENTICATION_KEY_provided"`

3. Inside `/LiveChatApp/assign_tasks.py` look where the gupshup credentials are used. Replace them with those provided by Gupshup for your Bot.

Note: `/LiveChatApp/assign_tasks.py` may or may not contain guphsup `def sendWhatsAppTextMessage` function. So add this function if not added already.
# Steps to enable RML WA Webhook

1. Give easychat webhook url to RML vendor for configuration.
    e.g https://easychat-dev.allincall.in/chat/webhook/whatsapp/?bot_id=46&bot_name=uat

    You will find this url in Bot channel 's WhatsApp configuration.
    if the console domain name is different replace `easychat-dev.allincall.in` with your console's domain.

2. Copy paste `rml_WA_Webhook.py` code.

3. RML will provide the following:
    a. WhatsApp Bot Mobile Number
    b. Username
    c. Password

4. Inside `whatsapp_webhook` function,

    change  `response["mobile_number"] = "whatsappbot_mobile_number"` (before try block)

    change  `rm_username = "rml_username_provided"`
            `rm_password = "rml_password_provided"`

5. API Key Caching:
    By default RML WA Webhook uses non-cached API key function `GET_API_KEY`.
    RML Token API can be cached for 1 hour. 
    `GET_RML_JWT_TOKEN`is the cached api_key function.
    Before using cached api key, we need to follow the below steps:

        -   Create `RouteMobileToken` model

            in EasyChatApp/models.py
            >   from django.utils import timezone as tz
                class RouteMobileToken(models.Model):
                    token = models.CharField(max_length=1000, default='token', help_text="This is a Bearer token for all RML APIs")
                    token_generated_on = models.DateTimeField(default=tz.now)

            in EasyChatApp/admin.py
            >   class RouteMobileTokenAdmin(admin.ModelAdmin):
                    list_display = ['token_generated_on','token']

        -   python manage.py makemigrations & migrate

        -   gunicorn restart

        -   Create one RouteMobileToken object and set token value as "token"

# Steps to enable RML WA LiveChat
1. After RML WA Webhook setup completion and assuming LiveChat is already enabled in the bot configuration, copy paste `rml_LiveChatBotChannelwebhook.py` into LiveChatBotChannelWebhook model object from Admin panel.

2. Inside `GET_API_KEY` change the credentials as:
        username = "rml_username_provided"
        password = "rml_password_provided"

3. `rml_LiveChatBotChannelwebhook` uses cached version of API Key Function, so make sure steps mentioned earlier to use cached api key are implemented first.

4. Inside `/LiveChatApp/assign_tasks.py` look where the rml credentials are used. Replace them with those provided by RML for your Bot.
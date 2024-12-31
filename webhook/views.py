from django.shortcuts import render
from .models import *

# Create your views here.

# webhook/views.py


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from datetime import datetime

import requests
from django.http import HttpResponse

import json



# Hardcoded sensitive tokens (For testing purposes only, not recommended for production)
WEBHOOK_VERIFY_TOKEN = 'harish'
GRAPH_API_TOKEN = 'EAAqJlXY27X4BOZBpv9UT9JTQL3fuQyXQaVTK73pAO6hDOnuBZCjDaAqxMq42bjFzlF6ebMtdXckiRO6ZCPOmS3zqtOttLCxlzCKo0DPwPZBebijdWIIqGXPTYB3ta9plujwndKtlCl7yu8cad19CrxjYKGgANSofhAzTCIpbxebHW4MPFiP9KWRlYDiYZBZBnykgZDZD'
BUSINESS_PHONE_NUMBER_ID = '482657464921213'

def send_whatsapp_message(phone_number, message, context=None):
    reply_payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message},
    }
    if context:
        reply_payload["context"] = {"message_id": context}

    headers = {
        "Authorization": f"Bearer {GRAPH_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"https://graph.facebook.com/v18.0/{BUSINESS_PHONE_NUMBER_ID}/messages",
            headers=headers,
            json=reply_payload
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending WhatsApp message: {e}")





@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        # Handle webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            #print("Webhook verified successfully!")
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse(status=403)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        # Extract message details
        entry = data.get('entry', [])
        if not entry:
            return HttpResponse(status=400)

        changes = entry[0].get('changes', [])
        if not changes:
            return HttpResponse(status=400)

        value = changes[0].get('value', {})
        messages = value.get('messages', [])
        if not messages:
            return HttpResponse(status=200)  # No message to process

        message = messages[0]
        message_type = message.get('type')

        if message_type == 'text':
            phone_number = message.get('from')  # Sender's WhatsApp ID
            message_body = message.get('text', {}).get('body').strip().lower()

            if not phone_number or not message_body:
                return HttpResponse(status=400)

            # Determine the response based on the message content
            if message_body in ['hi', 'hello', 'hey']:
                response_text = (
                    "Thank you for reaching us.How can i assist you today?**.\n"
                    "1. **Room Booking**\n"
                    "2. **Seva Booking**\n"
                    "3. **Template Information**\n"
                    "4. **Upcoming Events**\n"
                    "5. **Contact Us**\n"
                    "6. **Other Queries**\n"



                )
            elif message_body == '1':
                response_text = (
                    "**Pls select the type of room**\n\n"
                    "1. **Single Room**\n"
                    "2. **Double Room**\n"
                    "3. **Dormitory**\n"

                    
                )
            elif message_body == '2':
                response_text = (
                    "**Pls select the type of seva**\n\n"
                    "1. **Seva One**\n"
                    "2. **Seva Two**\n"
                    "3. **Seva Three**\n"
                    "4. **Seva Four**\n"
                    "5. **Seva Five**\n"


                
                )

            elif message_body == '3':
                response_text = (
                    "**https://websitelink.com **\n"
                    "**click on above link for Template details **\n\n"
                
                )

            elif message_body == '4':
                response_text = (
                    "**https://websitelink.com **\n"
                    "**click on above link for Upcoming Events **\n\n"
                
                )

            elif message_body == '5':
                response_text = (
                    "**https://websitelink.com **\n"
                    "**click on above link for Template details **\n\n"  
                
                )

            elif message_body == '6':
                response_text = (
                    "**https://websitelink.com **\n"
                    "**click on above link to Join vedashala Whatsapp community**\n\n"

                    "**https://websitelink.com **\n"
                    "**click on above link to Join vedashala Whatsapp community**\n\n"
                    
                
                )
            # elif message_body == 'yes':
            #     response_text = (
            #         "Thank you for your response we will get back to you ASAP"
            #     )
            # elif message_body == 'no':
            #     response_text = (
            #         "Thank you for your response for more information please visit our webiste\n"
                    
            #     )
            else:
                response_text = (
                    "I'm sorry, I didn't understand that. Please respond with:\n"
                    "- **Hi** to start the conversation.\n"
                    "- **1** or **2** to choose a class."
                )

            # Send the response to the customer
            send_whatsapp_message(phone_number, response_text, context=message.get('id'))

            # Save the message and response to the database
            try:
                Message.objects.create(
                    phone_number=phone_number,
                    message_body=message_body,
                    response_body=response_text
                )
            except Exception as e:
                print(f"Error saving message: {e}")
                return HttpResponse(status=500)

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=405)  # Method Not Allowed













def chat_view(request):
    # Fetch all messages
    all_messages = Message.objects.all()

    # Print all messages for debugging
    print("All messages:", all_messages)

    # Fetch unique phone numbers
    phone_numbers = Message.objects.values_list('phone_number', flat=True).distinct()

    # Print phone numbers for debugging
    print("Phone numbers:", phone_numbers)

    # Fetch messages by phone number
    messages_by_phone = {}
    for phone in phone_numbers:
        messages = Message.objects.filter(phone_number=phone).order_by('timestamp').values('message_body', 'timestamp')
        messages_by_phone[phone] = list(messages)

    # Print messages by phone number for debugging
    print("Messages by phone:", messages_by_phone)

    # Pass the data to the template
    return render(request, 'chat.html', {
        'phone_numbers': phone_numbers,
        'messages_by_phone': messages_by_phone
    })






@csrf_exempt
def get_phone_numbers(request):
    if request.method == "GET":
        # Get a list of unique phone numbers
        phone_numbers = Message.objects.values_list("phone_number", flat=True).distinct()
        return JsonResponse({"phoneNumbers": list(phone_numbers)})








from django.utils.timezone import localtime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message

@csrf_exempt
def get_messages_by_phone(request, phone_number):
    if request.method == "GET":
        messages = Message.objects.filter(phone_number=phone_number).order_by("-timestamp")
        
        
        messages_data = []
        current_date = None

        for msg in messages:
            # Convert timestamp to local time and format it
            local_timestamp = localtime(msg.timestamp)
            message_date = local_timestamp.date()
            formatted_time = local_timestamp.strftime('%H:%M')  # Format the time in HH:MM format

            # Insert date if it's a new day
            if current_date != message_date:
                current_date = message_date
                messages_data.append({
                    "date": current_date.strftime('%Y-%m-%d'),  # Format date as needed
                    "type": "date"
                })

            # Add the message with its timestamp
            messages_data.append({
                "message_body": msg.message_body,
                "response_body": msg.response_body,
                "timestamp": formatted_time,
                "type": "received"
            })

        return JsonResponse({"messages": messages_data})












def index(request):
    return render(request,'index.html')
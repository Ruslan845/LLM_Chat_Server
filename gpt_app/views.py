import json
import requests
# from openai import OpenAI
import openai
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from auth_app.models import Chatlist, User
from backend.getrequest import getrequest
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from auth_app.serializers import ChatListSerializer


# client = OpenAI(api_key=settings.OPENAI_API_KEY)
client = openai.OpenAI(api_key = settings.OPENAI_API_KEY)
DEEPAI_API_KEY = settings.DEEPAI_API_KEY

def get_answer_openai(question, model):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{
                    "role": "user",
                    "content": question
                }],
            max_tokens=100,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)
    
def get_answer_deepseek(question, model):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + DEEPAI_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model" : model,
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
    }
    print(f"Request to DeepSeek API: {url}")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return answer
    # print(response,json)
    return response.get('messages')[0].get('content')



# Create your views here.   

# def getonelist()

def getanswer(model, question):
    try:
        answer = ''
        if model.startswith('gpt') or model.startswith('text'):
            answer = get_answer_openai(question, model)
        elif model.startswith('deepseek'):
            answer = get_answer_deepseek(question, model)
        print("question: ", question)
        print("answer: ", answer)
        return answer
    except Exception as e:
        return str(e)

@csrf_exempt
@permission_classes([IsAuthenticated])
def add_chat(request):
    body = getrequest(request)
    try:
        chat = Chatlist(
            user_id = body.get('user_id'),
            chat_list = [
                {
                    "role": "user",
                    "text": body.get('question'),
                    "model": body.get('model'),
                    "date": datetime.now(),
                    "deleteddate": None
                }
            ]
        )
        chat.save()

        answer = getanswer(body.get('model'), body.get('question'))
        chat.chat_list.append(
            {
                "role": "bot",
                "text": answer,
                "model": body.get('model'),
                "date": datetime.now(),
                "deleteddate": None 
            }
        )
        chat.save()
        seri_chat = ChatListSerializer.serialize_one(chat)

        chats = Chatlist.objects(user_id = body.get('user_id'))
        titlelist = []
        for chat in chats:
            titlelist.append({"chat_id": chat.id, "chat_title": chat.chat_list[0]["text"]})
        S_titlelist = ChatListSerializer.serialize_titlelist_all(titlelist)
        return JsonResponse({"message": "Chat added successfully~", "chat_list": seri_chat, "title_list": S_titlelist}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@permission_classes([IsAuthenticated])
def ask_gpt(request):

    body = getrequest(request)
    chat = Chatlist.objects(id = body.get('chat_id')).first()
    try:
        question = {
                "role": "user",
                "text": body.get('question'),
                "model": body.get('model'),
                "date": datetime.now(),
                "deleteddate": None
            }
        chat.chat_list.append(question)
        chat.save()

        answer_text = getanswer(body.get('model'), body.get('question'))
        answer = {
                "role": "bot",
                "text": answer_text,
                "model": body.get('model'),
                "date": datetime.now(),
                "deleteddate": None
            }
        chat.chat_list.append(answer)
        chat.save()
        return JsonResponse({"message": "Get answer successfully", "question": ChatListSerializer.serialize_list(question), "answer": ChatListSerializer.serialize_list(answer)}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
@permission_classes([IsAuthenticated])
def  get_title_list(request):
    body = getrequest(request)
    try:
        chats = Chatlist.objects(user_id = body.get('user_id'))
        titlelist = []
        for chat in chats:
            titlelist.append({"chat_id": chat.id, "chat_title": chat.chat_list[0]["text"]})
        S_titlelist = ChatListSerializer.serialize_titlelist_all(titlelist)
        return JsonResponse({"title_list": S_titlelist}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@permission_classes([IsAuthenticated])
def get_chat(request):
    body = getrequest(request)
    try:
        chat = Chatlist.objects(id = body.get('chat_id')).first()
        if chat:
            return JsonResponse({"chat_list": ChatListSerializer.serialize_one(chat)}, status=200)
        else:
            return JsonResponse({"message": "No chat list found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
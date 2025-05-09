import json
import requests
# from openai import OpenAI
import openai
import traceback
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
from user_management.permissions import IsAdminOrReadOnly
from apikey.views import get_one
from bson import ObjectId, errors as bson_errors
# from serpapi import GoogleSearch


# client = OpenAI(api_key=settings.OPENAI_API_KEY)
client = openai.OpenAI(api_key = get_one("OPENAI_API_KEY"))
DEEPAI_API_KEY = get_one("DEEPSEEK_API_KEY")
# SERP_API_KEY = get_one("SERP_API_KEY")

def get_answer_openai(question, model, tem, token):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{
                    "role": "user",
                    "content": question
                }],
            max_tokens=token,
            temperature=tem,    
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)
    
def get_answer_deepseek(question, model, tem, token):
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
        "temperature": tem,
        "max_tokens": token,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return answer
    return response.get('messages')[0].get('content')

# def web_search(question):
#     search = GoogleSearch({
#         "q": question,
#         "api_key": SERP_API_KEY,
#     })
#     results = search.get_dict()
#     answers = results.get("organic_results", [])
#     result_question = "User asked: " + question + "\n I searched the web and found the following:\n"
    
#     for index, answer in enumerate(answers):
#         result_question += f"{index+1}. {answer.get('title')} - {answer.get('link')}\n"
#     result_question += "\nUsing the above information, answer the user's question in a clear and concise way.";
#     print("question: " + question + "\nResult_question: " + answer + "\n\n---\n")
#     return result_question

# def getonelist() 

def getanswer(model, question, tem, token):
    try:
        answer = ''
        if model.startswith('gpt') or model.startswith('text'):
            answer = get_answer_openai(question, model, tem, token)
        elif model.startswith('deepseek'):
            answer = get_answer_deepseek(question, model, tem, token)
        return answer
    except Exception as e:
        return str(e)
    
@csrf_exempt
@permission_classes([IsAuthenticated])
def add_chat(request):
    body = getrequest(request)
    print("body: ", body)
    question = body.get('question')        
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # e.g. 20250425170045
    unique_title = f"{question}__{timestamp}"

    try:
        # d_chat = Chatlist.objects(chat_title = body.get('question'), user_id = body.get('user_id'))
        chat = Chatlist(
            user_id = body.get('user_id'),
            chat_title = unique_title,
            chat_list = []
        )
        print("question: ", question)
        chat.save()
        s_chat = ChatListSerializer.serialize_one(chat)
        chats = Chatlist.objects(user_id = body.get('user_id'))
        print("chats: ", chats)
        titlelist = []
        for chatitem in chats:
            titlelist.append({"chat_id": chatitem.id, "chat_title": chatitem.chat_title })
        print("titlelist: ", titlelist)
        S_titlelist = ChatListSerializer.serialize_titlelist_all(titlelist)
        return JsonResponse({"message": "Chat added successfully~", "chat_id": s_chat["chat_id"], "title_list": S_titlelist}, status=201)
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
                "deleteddate": None,
                "isnew": "False"
            }
        chat.chat_list.append(question)
        chat.save()

        answer_text = getanswer(body.get('model'), body.get('question'), body.get('temperature'), body.get('max_token'))
        answer = {
                "role": "bot",
                "text": answer_text,
                "model": body.get('model'),
                "date": datetime.now(),
                "deleteddate": None,
                "isnew": "True"
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
    print("this is in get_title_list function: ", body)
    print("this is in get_title_list function: ", request)
    try:
        chats = Chatlist.objects(user_id = body.get('user_id'))
        print("chats: ", chats)
        titlelist = []
        for chat in chats:
            print("title: ", chat, chat.chat_title)
            titlelist.append({"chat_id": chat.id, "chat_title": chat.chat_title})
        print("titilelist: ", titlelist)
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
    
@csrf_exempt
# @permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def delete_thread(request, chat_id):
    if request.method == 'DELETE':
        try:
            # Fetch the user by ID
            list = Chatlist.objects.get(id=chat_id)
            list.delete()
            return JsonResponse({'message': 'Thread deleted successfully'}, status=200)
        except list.DoesNotExist:
            return JsonResponse({'error': 'Thread not found'}, status=404)

@csrf_exempt
def delete_chat_message(request, chat_id, message_id):
    if request.method == 'DELETE':
        try:
            # Fetch the user by ID
            chat = Chatlist.objects.get(id=chat_id)
            index = -1
            for message in chat.chat_list:
                if message["deleteddate"] == None:
                    index += 1
                print("index: ", index, "message_id: ", message_id, "message: ", message, "message[....]: ", message["deleteddate"])
                if index == int(message_id):
                    print("in index")
                    message["deleteddate"] = datetime.now()
                    print("message: ", message)
                    print("datetime: ", datetime.now())
                    chat.save()
                    return JsonResponse({'message': 'Message deleted successfully'}, status=200)
            return JsonResponse({'error': 'Message not found'}, status=404)
        except Chatlist.DoesNotExist:
            return JsonResponse({'error': 'Chat list not found'}, status=404)
        
@csrf_exempt
@permission_classes([IsAuthenticated])
def add_chat_history(request):
    try:
        body = getrequest(request)
        print("Received body:", body)
        chat_id = body.get('chat_id')
        chats = body.get('chats')

        if not chat_id or not ObjectId.is_valid(chat_id):
            return JsonResponse({"error": "Invalid or missing chat_id"}, status=400)

        chat = Chatlist.objects(id=ObjectId(chat_id)).first()
        if not chat:
            return JsonResponse({"error": "Chat not found"}, status=404)

        if not chats:
            return JsonResponse({"error": "Missing 'chats' in request body"}, status=400)

        chat.chat_list.append(chats[0])
        print("chat0: ", chats[0])
        chat.save()

        return JsonResponse({"message": "Chat history updated"}, status=200)

    except Exception as e:
        print("Internal Server Error in add_chat_history:", Exception.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@permission_classes([IsAuthenticated])
def change_chat_title(request):
    try:
        body = getrequest(request)
        print("Received body:", body)
        chat_id = body.get('chat_id')
        user_id = body.get('user_id')
        chat_title = body.get('chat_title')

        if not chat_id or not ObjectId.is_valid(chat_id):
            return JsonResponse({"error": "Invalid or missing chat_id"}, status=400)

        du_chat = Chatlist.objects(user_id=ObjectId(user_id), chat_title=chat_title).first()
        print('du_chat:', du_chat)
        if(du_chat):
            return JsonResponse({"message":"duplicate"}, status=200)
        
        chat = Chatlist.objects(id=ObjectId(chat_id)).first()
        if not chat:
            return JsonResponse({"error": "Chat not found"}, status=404)

        if not chat_title:
            return JsonResponse({"error": "Missing 'chat' in request body"}, status=400)


        chat.chat_title = chat_title
        chat.save()


        print("chat.chat_title: ", chat.chat_title)

        return JsonResponse({"message": "Chat history updated"}, status=200)

    except Exception as e:
        print("Internal Server Error in add_chat_history:", traceback.print_exc())
        return JsonResponse({"error": str(e)}, status=500)
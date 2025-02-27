from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from .models import ChatBot
import google.generativeai as genai

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
if api_key:
    print("______________________")# Configure your API key
genai.configure(api_key=api_key)

def home(request):
    models = genai.list_models()
    return render(request, 'base.html', {'models': models})

@login_required
def select_model(request):
    if request.method == "POST":
        selected_model = request.POST.get("model")
        if selected_model:
            return redirect('chat_with_model', model_name=selected_model.replace('/', '-'))
    
    return HttpResponseRedirect(reverse("home"))

@login_required
def ask_question(request, model_name):
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            # model_id = model_name.replace('-', '/')
            try:
                model_id = model_name[7:]
                print(f"models/{model_id}")
                model = genai.GenerativeModel(f"models/{model_id}")
                chat = model.start_chat()
                response = chat.send_message(text)
                user = request.user
                
                ChatBot.objects.create(text_input=text, gemini_output=response.text, user=user)
                response_data = {"text": response.text}
            except Exception as  e:
                response_data = {"text": "This model is currently unavailable due to API limitations. Please try another model or come back later."}
            
            return JsonResponse({"data": response_data})

    return HttpResponseRedirect(reverse("chat_with_model", kwargs={"model_name": model_name}))

@login_required
def chat(request, model_name):
    chats = ChatBot.objects.filter(user=request.user)
    return render(request, "chat_bot.html", {"chats": chats, "model_name": model_name})

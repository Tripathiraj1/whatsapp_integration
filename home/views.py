import os
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def index(request):
    return HttpResponse("Django with Conda is working!")

def get_openai_client():
    api_key = os.getenv("GPT_API")
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY") # Fallback
    if not api_key:
        raise ValueError("GPT_API or OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

@csrf_exempt
def chat_with_gpt(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            prompt = data.get("prompt")
            
            if not prompt:
                return JsonResponse({"error": "Prompt is required"}, status=400)

            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            reply = response.choices[0].message.content
            return JsonResponse({
                "status": "success",
                "response": reply
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)

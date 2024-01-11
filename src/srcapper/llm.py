from decouple import config
from openai import OpenAI

OPEN_API_KEY = config("OPEN_API_KEY")
client = OpenAI(api_key=OPEN_API_KEY)

def get_good_links(input,prompt,MODEL = "gpt-3.5-turbo-16k"):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"You are a helpful programing assistant. {prompt}"},
                {"role": "user", "content": input},
            ],
        temperature=0,)
        return response.choices[0].message.content
    except Exception as e:
        if "quota" in str(e).lower():
            print("Quota Exceeded")
        print(e)
        return None
    
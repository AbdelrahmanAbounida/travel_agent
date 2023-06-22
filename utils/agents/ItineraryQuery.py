import openai
import json 
import os 
from pathlib import Path
from  typing import Dict, Union

BASE_DIR = Path(__file__).resolve().parent
prompt_choices_path = os.path.join(BASE_DIR,"prompt_choices.json")

openai.api_key = os.environ.get("OPENAI_API_KEY")


def load_prompt_choices()-> Dict[str,str]:
    """This method will load all prompt options and their attributes """

    if not os.path.exists(prompt_choices_path):
        print("Please Check that prompt_choices.json file file exists in the same directory")
        return {"error":"Failed to load prompt choices"}
    with open(prompt_choices_path, 'r') as json_config_file:
        config_json = json.load(json_config_file)
        prompt_choices = config_json['prompt_choices']
    
    return prompt_choices 

def load_pinecone_choices() -> Dict[str,str]:
    if not os.path.exists(prompt_choices_path):
        print("Please Check that prompt_choices.json file file exists in the same directory")
        return {"error":"Failed to load prompt choices"}
    with open(prompt_choices_path, 'r') as json_config_file:
        config_json = json.load(json_config_file)
        pinecone_choices = config_json['pinecone_choices']
    
    return pinecone_choices["general"]

def get_pinecone_response(city:str,pinecone_city_info:str,
                          pinecone_hotels_info:str,
                          pinecone_places_info:str,
                          pinecone_restaurants_info:str,
                          pinecone_venues_info:str,
                          pinecone_self_explore_info:str,
                          num_of_days:int
                          ) -> Union[str,Dict[str,str]]:
    
    pinecone_info = {
        "city":city,
        "pinecone_city_info":pinecone_city_info,
        "pinecone_hotels_info":pinecone_hotels_info,
        "pinecone_places_info":pinecone_places_info,
        "pinecone_restaurants_info":pinecone_restaurants_info,
        "pinecone_venues_info":pinecone_venues_info,
        "pinecone_self_explore_info":pinecone_self_explore_info,
        "num_of_days":num_of_days

    }

    pinecone_choices = load_pinecone_choices()

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": pinecone_choices["system_text"].format(pinecone_info=pinecone_info)},
            {"role": "user", "content": pinecone_choices["user_text"].format(pinecone_info=pinecone_info) + f"""
               \n Provide your answer with new information using this sample JSON format .using the same exact keys only.
                Do not include any extra data or any additional explanation note(s).
                Here is the sample JSON format: {pinecone_choices["desired_json_format"]}
                """
            },
        ]
    )
    resp = response["choices"][0]["message"]["content"].replace('\\','')

    try:
        return json.loads(resp)
    except Exception as e:
        print(e)
        return resp



def get_openai_response(city:str,hotel:str,num_of_days:int,user_persona:str,context:str) -> Union[Dict, str]:
    """return openai response as str"""

    openai_choices = load_prompt_choices() 
    itinerary_info = {
                "city":city,
                "hotel":hotel,
                "num_of_days":num_of_days,
                "desired_json_format":openai_choices["desired_json_format"],
                "user_persona":user_persona,
                "context":context
            }
    
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": openai_choices["system_text"].format(itinerary_info=itinerary_info)},
            {"role": "user", "content": openai_choices["user_text"].format(itinerary_info=itinerary_info)},
        ]
    )
    resp = response["choices"][0]["message"]["content"].replace('\\','')
    if 'Notes' in resp:
        resp = resp.split('Notes')[0]
    else:
        last_brace_index = resp.rfind('}')
        if last_brace_index != -1:
            resp = resp[:last_brace_index + 1]
    try:
        out =  json.loads(resp)
        
    except Exception as e:
        print("Not json")
        print(resp)
        print("********************")
        out =  r'{}'.format(resp)

    return out

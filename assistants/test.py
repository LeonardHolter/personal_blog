from openai import OpenAI
import json
import requests

client = OpenAI(api_key="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")




def apertium_machine(tekst):
    url = "https://apertium.org/apy/translate"
    params = {
        "langpair": "nb|nno",
        "q": tekst,
        "markUnknown": "no"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        return result.get("responseData", {}).get("translatedText", "")
    else:
        return "Error: Unable to translate text."

training_message = "Your job is to translate a given bokmål text into Nyorsk. You can not translate words and sentences that are between quotation marks. Execcute the following after you have translated the text: Go thruogh each and every verb. If the verb has to ways to be written, ex:( å bake )and ( å baka )  rewrite the verb to the way that is the same for both bokmål and nynorsk.   "



def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "system", "content": training_message },
        {"role": "user", "content": "Jeg liker å bake "}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "apertium_machine",
                "description": "Get a nynorsk translation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bokmål": {
                            "type": "string",
                            "description": "A text written in Bokmål",
                        },

                    },
                    "required": ["bokmål"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "apertium_machine": apertium_machine,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(

                tekst=function_args.get("bokmål")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
messages = run_conversation()


print(messages.choices[0].message.content)

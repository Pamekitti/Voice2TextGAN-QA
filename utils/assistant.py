import os
import time
import json
from openai import OpenAI


# sample function for demo
def get_current_weather(location, unit="fahrenheit") -> str:
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "82" if unit=="fahrenheit" else "28",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)


class OpenAIAssistant:
    def __init__(self, openai_api_key, assistant_id):
        self.openai_api_key = openai_api_key
        self.assistant_id = assistant_id

        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        self.client = OpenAI()

        # Retrieve an assistant
        self.assistant = self.client.beta.assistants.retrieve(self.assistant_id)

        # Create an empty thread
        self.thread = self.client.beta.threads.create()
    
    def reset_chat(self):
        # Reset the thread
        self.thread = self.client.beta.threads.create()
        return self.thread
        
    def add_message(self, message):
        # Add user messages to the thread
        message = self.client.beta.threads.messages.create(
            thread_id = self.thread.id,
            role="user",
            content=message,
            )
        return message

    def run_assistant(self, verbose=False):
        # Run the assistant
        _run = self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.assistant.id)
        # print(run.model_dump_json(indent=4))

        # Retrieve the assistant response
        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id,run_id=_run.id)
            if verbose:
                print("run status: ", run_status.status)
                # print(run_status.model_dump_json(indent=4))
            
            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
                # print(messages)
                break

            elif run_status.status == 'requires_action':
                tool_outputs = list()
                for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                    # Retrieve the tool call ID, function name, and function arguments
                    tool_call_id = tool_call.id
                    function_name = tool_call.function.name
                    function_arguments = tool_call.function.arguments
                    print(tool_call_id, function_name, function_arguments)

                    # check if the function name is valid
                    if (self._is_valid_function_name(function_name)) and (function_arguments is not None):
                        # call the function
                        kwargs: dict = json.loads(function_arguments)
                        function_response = eval(function_name)(**kwargs)
                        tool_outputs.append({
                            "tool_call_id": tool_call_id,
                            "output": function_response,
                        })
                        print(f"function response: {function_response}")

                # submit the function response to `Run`
                _ = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread.id,
                    run_id=_run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": tool_call_id,
                            "output": function_response,
                        }
                    ]
                )

            else:
                pass

            time.sleep(2)
        
        return run_status.status, messages

    def get_chat_history(self):
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        return messages

    def _is_valid_function_name(self, function_name: str) -> bool:
        """Check if the function name is a valid Python identifier"""
        if not function_name.isidentifier():
            return False
        
        # Optionally: Check if the name is already defined in the current namespace
        if function_name in globals():
            return True

        return False


if __name__ == '__main__':
    # create an instance of the OpenAIAssistant class
    openai_api_key = ""  # TODO: change the API key to your own
    assistant_id = ""  # TODO: change the assistant ID to your own
    openai_assistant = OpenAIAssistant(openai_api_key, assistant_id)
    
    # reset the chat history
    _thread = openai_assistant.reset_chat()
    
    
    # ---------- 1st user query ----------
    
    # add a user message to thread
    _user_input = "Hello, how are you?"
    print("User input: ", _user_input)
    _message = openai_assistant.add_message(_user_input)
    
    # run the assistant
    status, messages = openai_assistant.run_assistant(verbose=True)
    print(f"{messages.data[0].role}: {messages.data[0].content[0].text.value}")
    print()


    # ---------- 2nd user query ----------

    # add a user message to thread
    _user_input = "How is RL being used in Semi-analytical Industrial Cooling System Model for Reinforcement Learning research paper"
    print("User input: ", _user_input)
    _message = openai_assistant.add_message(_user_input)
    
    # run the assistant
    status, messages = openai_assistant.run_assistant(verbose=True)
    print(f"{messages.data[0].role}: {messages.data[0].content[0].text.value}")
    print()
    
    
    # ---------- 3rd user query (custom function calling) ----------

    # add a user message to thread
    _user_input = "New topic, What's the weather like in Bangkok?"
    print("User input: ", _user_input)
    _message = openai_assistant.add_message(_user_input)
    
    # run the assistant
    status, messages = openai_assistant.run_assistant(verbose=True)
    print(f"{messages.data[0].role}: {messages.data[0].content[0].text.value}")
    print()

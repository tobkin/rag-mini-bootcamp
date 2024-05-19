from openai import OpenAI

import os

OPENAI_CLIENT = OpenAI()

class NaiveGenerator:
  def __init__(self):
    self._validate_env_variables()
    # TODO: fill in the system prompt
    self._system_prompt = f"""
      
      """
      
  def _validate_env_variables(self):
    if not os.getenv('OPENAI_API_KEY'):
        raise EnvironmentError("Environment variable 'OPENAI_API_KEY' not set. Please ensure it is defined in your .env file.")

  def _generation_prompt(self, question, context): 
    # TODO: fill in the prompt
    return f"""
      
      """

  def get_completion(self, question, context):
    completion_obj = OPENAI_CLIENT.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {
          "role": "system",
          "content": f"{self._system_prompt}"
        },
        {
          "role": "user",
          "content": f"{self._generation_prompt(question, context)}"
        }
      ],
      temperature=0,
      max_tokens=256,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    return completion_obj.choices[0].message.content
# Reference: 
# https://lmstudio.ai/docs/basics/server
# https://platform.openai.com/docs/api-reference/chat

from openai import OpenAI

base_url = "http://localhost:1234/v1" # Run LM Studio server on this port before running this code

class LLMAgent: 
    client = OpenAI(base_url=base_url, api_key="lm-studio")

    # Given a user prompt message, return the LLM response
    def send_llm_request(self, message):
        completion = self.client.chat.completions.create(
        model="model-identifier",
        messages=[
            {"role": "system", "content": "Always answer in rhymes."}, # TODO: delete this in actual development
            {"role": "user", "content": message}
        ],
        temperature=0.7,
        )

        response = completion.choices[0].message.content
        print(response)
        return response

if __name__ == '__main__':
    agent = LLMAgent()
    while True:
        msg = input("You: ")
        agent.send_llm_request(msg)
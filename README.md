# PrivAgent: A Privacy-First LLM Agent for Contextual Task Automation in Email Environments
UCSD Fall 2024 CSE 227 Course Project

Authors: Jieyi Huang, Xin Sheng
## Getting started
* For the LM Studio, run models `meta-llama-3.1-8b-instruct` and `nomic-embed-text-v1.5`. To stably process long emails, raise the Llama model context length to 8192. 
* To set up Environment, make sure anaconda or miniconda is installed on device, then in the desired environment run in terminal: 
```
conda install --file requirements.txt
```
* To run the application, run in terminal: 
```
python app.py
```
* To run the llm agent for chatting, first run an LM Studio server on port 1234, then run in terminal: 
```
python llm_agent.py
```
* To save the environment, run in terminal: 
```
conda list -e > requirements.txt
```

## Dev Logs
### LLM Agent: run LM Studio server on port 1234
Reference: 
https://lmstudio.ai/docs/basics/server
https://platform.openai.com/docs/api-reference/chat

### LLM Agent: necessary information
General: 
* Current date

Prompt-specific: 

Some information that needs to be filled in should be well-formatted and handled within the LLM agent

Attempts: 
* Use llama-3.2-3b and OpenAI package, not very good result
* Prompt engineer into multiple questions with examples, better
* Prompt engineer into multiple steps, not working
* Use llama-3.1-8b, much better
* Parse the output, higher accuracy
* Lower the temperature, more stable
* Deploy Rag using Llama-Index, move the api calls to Llam-Index query-engine as well, doesn't know chat history
* Change to chat-engine, a lot better

### Google API
Prerequisites we've done to get the authentication project working: 
* Create a new Google project
* Enable APIs: Google Calendar **(Add more in the future)**
* Configure OAuth consent screen
* Add OAuth Client ID
* Copy over credentials json file

Prerequisites for a Google account to use our application: 
* Be added to the tester list

Each time running the app:
* Run llm_agent.py 
* Redirected to website to give authorization
* Either save the token as file, or the user has to authenticate every time **(Possible encryption improvements here)**

Reference: 
https://developers.google.com/calendar/api/quickstart/python
Desktop Pet starter code: https://github.com/tommyli3318/desktop-pet

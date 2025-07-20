# Exploring AI Agents
**AI Agents** extend the functionality of AI Models by incorporating additional instructions and capabilities.
To get started, navigate to the [AI Agents](https://id.io.net/ai/agents) section in your dashboard.
![](https://files.readme.io/b0537ae0f9b88cd43219f6c68834b0ea6202fd621469791ae69238960dd2d27e-IO_Intellegence13.jpg)
### [](https://docs.io.net/docs/exploring-ai-agents#what-you-can-do-on-the-dashboard)
  * Use the **search field** to find a specific agent.
  * Browse **Trending AI Agents** , which are popular in our community.

![](https://files.readme.io/12c59a72d827c83c034a99e8f6cbfcdc726d44bd35e3505c591e259ceb6bf015-IO_Intellegence14.jpg)
### [](https://docs.io.net/docs/exploring-ai-agents#popular-ai-agents)
Agent Name | Description  
---|---  
Summary Agent | An expert in distilling large volumes of text into concise, meaningful summaries. Whether condensing reports, extracting key points from articles, or generating executive briefs, this agent ensures that critical information is delivered efficiently.  
Sentiment Analysis Agent | A neutral and analytical evaluator of emotions embedded in the text, this agent precisely determines sentiment—be it positive, negative, or neutral. Ideal for brand monitoring, customer feedback analysis, and social media insights, it provides an unbiased pulse on public opinion.  
Named Entity Recognizer | A meticulous extractor of key entities such as names, dates, organizations, and locations from unstructured text. Whether used for information retrieval, knowledge graph construction, or document indexing, this agent enhances the understanding of textual data.  
Custom Agent | A highly adaptable and versatile agent designed to handle a wide range of tasks with precision. Whether analyzing data, automating workflows, or assisting with decision-making, this agent is dynamic, resourceful, and ready to tackle whatever challenge comes its way.  
Moderation Agent | An intelligent watchdog that ensures content remains safe, compliant, and aligned with community guidelines. From detecting harmful language to filtering inappropriate content, this agent is dedicated to maintaining a high standard of discourse in any environment.  
Classification Agent | A specialist in sorting, labeling, and organizing data with unparalleled accuracy. Whether categorizing documents, tagging images, or structuring information, this agent brings clarity and order to vast amounts of unstructured content.  
Translation Agent | A linguistic powerhouse fluent in multiple languages, this agent seamlessly translates text while preserving meaning, nuance, and cultural context. Whether for global communication or multilingual content creation, it ensures accuracy and fluency in every translation.  
For a complete list, visit the [AI Agents section](https://id.io.net/ai/agents).
### [](https://docs.io.net/docs/exploring-ai-agents#selecting-agent)
To start configuring the required AI Agent, select and click on the desired AI Agent.
![](https://files.readme.io/234719bed86b8665226f52d99fd5e9bd41d0dd65f3e5803c876b42b73c9d4494-IO_Intellegence15.jpg)
A popup will appear with instructions on how to configure the selected Node. You have two options to install the AI Agent:
  1. Install via pip:
     * Open the Terminal and run the following command:
Terminal
```
pip install --upgrade iointel

```

     * Use this **Python example** to start using the selected AI Agent:
Python
```
from iointel import (
    Agent,
    Workflow
)

import os
import asyncio

api_key = os.environ["OPENAI_API_KEY"]  # Replace with your actual IO.net API key

text = """In the rapidly evolving landscape of artificial intelligence, the ability to condense vast amounts of information into concise and meaningful summaries is crucial. From research papers and business reports to legal documents and news articles, professionals across industries rely on summarization to extract key insights efficiently. Traditional summarization techniques often struggle with maintaining coherence and contextual relevance. However, advanced AI models now leverage natural language understanding to identify core ideas, eliminate redundancy, and generate human-like summaries. As organizations continue to deal with an ever-growing influx of data, the demand for intelligent summarization tools will only increase. Whether enhancing productivity, improving decision-making, or streamlining workflows, AI-powered summarization is set to become an indispensable asset in the digital age."""

agent = Agent(
    name="Summarize Agent",
    instructions="You are an assistant specialized in summarization.",
    model="meta-llama/Llama-3.3-70B-Instruct",
    api_key=api_key,
    base_url="https://api.intelligence.io.solutions/api/v1"
)

workflow = Workflow(objective=text, client_mode=False)

async def run_workflow():
    results = (await workflow.summarize_text(max_words=50,agents=[agent]).run_tasks())["results"]
    return results

results = asyncio.run(run_workflow())
print(results)

```

![](https://files.readme.io/5182d76c919c4dfe776e28bb9c998df71e0a6f4f62b7929be42ba78d5cc995be-Artboard.jpg)   

  2. Install via cURL:  
Use this **cURL example** to start using the selected AI Agent:
cURL
```
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer io-v1-YOUR-DEV-API-KEY" \
  --data '{
    "text": "text to summarize",
    "agent_names": ["summary_agent"],
    "args": { "type": "summarize_text" }
  }' \
  https://api.intelligence.io.solutions/api/v1/workflows/run

```

![](https://files.readme.io/03f1742dc2c8a1ad0a2866b3c0417b030b44ef9607d4b7315fc4ae6337f07202-Group_72.jpg)


**Note:** Don't forget to replace `io-v1-YOUR-DEV-API-KEY` with your actual [API Key](https://ai.io.net/ai/api-keys).
### [](https://docs.io.net/docs/exploring-ai-agents#example-using-curl-request)
![](https://files.readme.io/6709446dddc14a3d8203cae7e56c5f390d0f1b46dfbcbbe58cf47688c1f3981d-agent-example.jpg)
about 1 month ago
* * *
  * [](https://docs.io.net/docs/exploring-ai-agents)
  *     * [What you can do on the dashboard:](https://docs.io.net/docs/exploring-ai-agents#what-you-can-do-on-the-dashboard)
    * [Popular AI Agents](https://docs.io.net/docs/exploring-ai-agents#popular-ai-agents)
    * [Selecting Agent](https://docs.io.net/docs/exploring-ai-agents#selecting-agent)
    * [Example using cURL request](https://docs.io.net/docs/exploring-ai-agents#example-using-curl-request)



# IO Intelligence
IO Intelligence is an AI infrastructure and API platform that democratizes access to advanced **AI models and AI agents** for the IO community and AI developers. It allows users to access and integrate **pre-trained open-source models and custom AI agents** into their applications via API calls.
This guide is for users who want to use the API keys of IO Intelligence to use our open-source **LLM Model Marketplace** or **AI Agents** for your applications. You can also refer to our [API Reference](https://docs.io.net/reference/get-started-with-io-intelligence-api) to understand how to use our API.
## [](https://docs.io.net/docs/io-intelligence#table-of-contents)
  * [Getting Started](https://docs.io.net/docs/io-intelligence#getting-started)
  * [Creating an API Key](https://docs.io.net/docs/io-intelligence#creating-an-api-key)
  * [Exploring AI Models](https://docs.io.net/docs/exploring-ai-models)
  * [Testing AI Models](https://docs.io.net/docs/exploring-ai-models#testing-ai-model)
  * [Exploring AI Agents](https://docs.io.net/docs/exploring-ai-agents)
  * [Configuring a Node for an AI Agent](https://docs.io.net/docs/exploring-ai-agents#configuring-a-node-for-an-ai-agent)
  * [Using the API](https://docs.io.net/docs/io-intelligence#using-the-api)
  * [FAQs](https://docs.io.net/docs/io-intelligence#faqs)


## [](https://docs.io.net/docs/io-intelligence#getting-started)
To use the IO Intelligence API, you’ll need an **API key**. Follow these steps to get started:
  1. **Sign up** for an account on IO Intelligence.
  2. **Create an API key** (see [Creating an API Key](https://ai.io.net/ai/api-keys)).
  3. Explore the available open-source **AI Models** and **AI Agents**.
  4. Use the API Reference to integrate the API into your application.


### [](https://docs.io.net/docs/io-intelligence#creating-an-api-key)
  1. Navigate to the **API Keys** section.
![](https://files.readme.io/054eb77108c20ae5c107fed3801d0cb6f258463c94bbad63bf6bc69e05a01d01-IO_Intellegence_1.jpg)
  2. Click **Create New Secret Key.**
![](https://files.readme.io/0610c81565871f2e9faa543af9aa2fc1c989016a7b221e5b057c0113e55e5e2a-IO_Intellegence2.jpg)
  3. Fill in the required details:
     * **Name** : Enter a descriptive name for your key.
     * **Project** : Select "IO Intelligence".
     * **Permissions** : Choose from All, Read, Write.
     * **Expiration** Date: Select 30, 60, 90, or 180 days.
  4. Click Create Secret Key.
![](https://files.readme.io/9abcdf8de584c839e19093de2cd25ced681224acfdcc8863b00c861576faa490-IO_Intellegence3.jpg)
  5. A popup will appear with your secret key. **Copy the secret key and store it securely (e.g., in a password manager or secure file).**
![](https://files.readme.io/11d1150a832ca47b83c7501b8db7a17e35454c631d01213234fd116c497e722b-IO_Intellegence4.jpg)


### [](https://docs.io.net/docs/io-intelligence#managing-api-keys)
**Search API Keys:** Use the **search field** to find a previously created key.
**View API Key Details:**
  * **Name** : The identifier of the key.
  * **Project** : The associated project.
  * **Permissions** : Access levels assigned to the key.
  * **Expiration Date:** The validity period of the key.
  * **Editing a Key** : Update the name or permissions of an existing key.
  * **Revoking a Key** : If a key is no longer needed, you can revoke it. Note: Once revoked, the key cannot be restored.

![](https://files.readme.io/8295ec8c9d5b1f695c1e79f3ec625876a183d1b86bc11d0672ae39e67902471a-IO_Intellegence5.jpg)
### [](https://docs.io.net/docs/io-intelligence#revoking-api-keys)
  1. Click the **Revoke** button in the API Key table.
  2. A confirmation popup will appear.
  3. Confirm the action to revoke the key.

![](https://files.readme.io/6dfa6fd9538707c5e248cf192efef068bb055d682fa1ce5fe3fa1407b108589e-IO_Intellegence6.jpg)
## [](https://docs.io.net/docs/io-intelligence#using-the-api)
To use the IO Intelligence API:
  1. Authenticate your requests using your **API key**.
  2. Send requests to the appropriate endpoints (see [API Reference](https://docs.io.net/reference/get-started-with-io-intelligence-api)).
  3. Handle responses and integrate them into your application.


**Example: cURL Request**
cURL
```
curl https://api.intelligence.io.solutions/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $IOINTELLIGENCE_API_KEY" \
  -d '{
     "model": "meta-llama/Llama-3.3-70B-Instruct",
     "messages": [{"role": "user", "content": "Say this is a test!"}],
     "temperature": 0.7
   }'

```

For detailed information on API endpoints, parameters, and examples, visit the [IO Intelligence API Reference](https://docs.io.net/reference/get-started-with-io-intelligence-api).
## [](https://docs.io.net/docs/io-intelligence#faqs)
##### [](https://docs.io.net/docs/io-intelligence#q-what-is-io-intelligence-api)
IO Intelligence API allows developers to integrate advanced AI models and agents into their applications for various use cases like text generation, embeddings, and more.
##### [](https://docs.io.net/docs/io-intelligence#q-how-do-i-secure-my-api-key)
Do not share your API key publicly.  
Use environment variables to store API keys securely.  
Rotate your API keys periodically.
##### [](https://docs.io.net/docs/io-intelligence#q-what-are-the-request-limits-for-the-api)
The IO Intelligence API offers different **free daily limits per account** , depending on the AI model. See the table in our [API Reference](https://docs.io.net/reference/get-started-with-io-intelligence-api#important-note-on-usage-limits) for model-specific limits.
2 months ago
* * *
  * [](https://docs.io.net/docs/io-intelligence)
  *     * [Table of Contents](https://docs.io.net/docs/io-intelligence#table-of-contents)
    * [Getting Started](https://docs.io.net/docs/io-intelligence#getting-started)
      * [Creating an API Key:](https://docs.io.net/docs/io-intelligence#creating-an-api-key)
      * [Managing API Keys](https://docs.io.net/docs/io-intelligence#managing-api-keys)
      * [Revoking API Keys](https://docs.io.net/docs/io-intelligence#revoking-api-keys)
    * [Using the API](https://docs.io.net/docs/io-intelligence#using-the-api)
    * [FAQs](https://docs.io.net/docs/io-intelligence#faqs)



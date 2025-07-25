# Retrieval Engine
The **Retrieval Engine** is a powerful tool within the io.net ecosystem that enhances your AI applications with capabilities like document ingestion, intelligent file management, agentic reasoning, and conversational question answering.
Retrieval Engine allows your AI to **read, view** , and **listen** to various types of content — learning from them in real-time. Once your files are ingested, Retrieval Engine combines the insights and context from your documents to generate intelligent, grounded responses to your queries.
### [](https://docs.io.net/docs/retrieval-engine#what-is-retrieval-engine)
[Retrieval Engine](https://ai.io.net/ai/re) stands for **Retrieval-Augmented Generation** — a method of combining a language model with a retrieval system. Instead of relying solely on the language model's pre-trained knowledge, Retrieval Engine retrieves relevant context from your uploaded documents in real-time to answer your questions more accurately and specifically.
It’s especially useful in enterprise, research, and developer environments where accuracy, transparency, and traceability of answers are critical.
### [](https://docs.io.net/docs/retrieval-engine#getting-started)
To begin using the Retrieval Engine System:
  1. **Go to your io.net Dashboard.**
  2. Navigate to the **[Retrieval Engine](https://ai.io.net/ai/re)** into **IO Intelligence** section.
  3. Upload your content and begin interacting with the system.

![](https://files.readme.io/0a6be78cd8f6dced4bce873a917652afe5862debee68a05361248406c486239d-Rag1.jpg)
### [](https://docs.io.net/docs/retrieval-engine#what-you-can-do-in-the-retrieval-engine)
#### [](https://docs.io.net/docs/retrieval-engine#1-chat-with-retrieval-engine)
  * At the bottom of the page, there is a chat field
  * Simply type your question or command.
  * Retrieval Engine will search through your uploaded documents and respond using context from those files.


#### 
**Upload Files**
[](https://docs.io.net/docs/retrieval-engine#2-upload-files)
  * Click the **Upload Files** button or drag and drop files into the left-hand panel.
  * Supported formats: **.pdf, .docx, .png, .jpg, .mp4, .html** , and more.
  * Maximum file size per upload: **100MB**.
![](https://files.readme.io/4ff2e7e4ac1c289adf4aa036bedf34a72a9fdff76cf70efc22861275cc159489-rag4.jpg)


> ## 📘
> ### [](https://docs.io.net/docs/retrieval-engine#notes--best-practices)
>   * Make sure your files are clearly named and well-structured for better results.
>   * For best performance, use updated file formats and avoid scanned documents or low-quality media.
> 

#### [](https://docs.io.net/docs/retrieval-engine#3-view-file-information--summaries)
  * Hover over a file in the left panel.
  * Click the **three-dot menu** (⋮) next to the file name.
  * Select **"File Info"** to view the document’s summary and metadata generated by Retrieval Engine.
![](https://files.readme.io/a512695cc2f10a4aad469a00432eda79f43a17ff6786ee692b1aba654c92fc09-rag6.jpg)


#### [](https://docs.io.net/docs/retrieval-engine#4-delete-files)
  * To remove a file from your local Retrieval Engine storage: 
    * Hover over the file name.
    * Click the **three-dot menu (⋮)** and choose **"Delete File"**.

![](https://files.readme.io/84ac6e792314b744649f205a8ed270d2ee5cde7bbc7f07c8899991e634c88c38-rag5.jpg)
#### [](https://docs.io.net/docs/retrieval-engine#5-search-settings)
To adjust how your search works, click the **Settings icon** next to the **Upload Files** button.
![](https://files.readme.io/13a833c25a0feb52fe2c2da7ba27502c9ed26194043b29229ba90c55acceedc2-Search_Settings.png)
Main Settings
  * **Vector Search** – Uses machine learning to find semantically similar content, even if exact keywords aren’t used.
  * **Hybrid Search** – Combines both traditional keyword search and semantic (vector-based) search for more accurate results.
  * **Graph Search** – Enhances retrieval using relationships and connections between documents or data points.

![](https://files.readme.io/31b740bde0d968191c04a9e3d3778f185aae33a73ffa25bc7fa832fc71ec22b1-Search_Settings2.png)
**Vector Search Settings**
  * **Search Results Limit** – Number of results shown per query (default is 10).
  * **Index Measure** – Method for comparing similarity: 
    * **Cosine** – Measures angle between vectors (commonly used).
    * **Euclidean** – Measures straight-line distance.
    * **Dot Product** – Multiplies and sums vector elements.
  * **Probes** – Controls the number of partitions searched; more probes = better recall, but slower performance.
  * **EF Search** – Trade-off setting between speed and accuracy during search. Higher = better results but slower.

![](https://files.readme.io/d699807582879a8eaa95bd34cd4ba69c19fa0f9c5ac5471fcd31fcb6e24cbc6a-Vector_Search.png)
**Hybrid Search Settings**
  * **Full Text Weight** – Sets how much importance to give exact keyword matches.
  * **Semantic Weight** – Sets how much importance to give AI-based understanding of the text.
  * **Full Text Limit** – Limits how many keyword-based results to include in hybrid search.
  * **RRF K** – A ranking method that merges results from different search strategies. Higher K = more balanced merging.

![](https://files.readme.io/21395726e0058fc930aa1fca18057f770ad934c536172f33ab6b5eac720ab55b-Hybrid_Search_Settings.png)
**RAG Generation Settings (RAG = Retrieval-Augmented Generation)**
  * **Model** – Selects which AI model to use for generating responses.
  * **Temperature** – Controls randomness of the AI’s responses: 
    * Lower (e.g. 0.1) = more focused and deterministic answers.
  * **Top P** – Controls diversity. 1 = full range of outputs considered.
  * **Max Tokens to Sample** – Limits how long the AI’s response can be (1024 tokens = about 700–800 words).

![](https://files.readme.io/b8da86fffdd5f9bbf8a1dc24c3345cb2037d1988fd51cc1c94827fce96c25734-RAG_Generation_Settings.png)
### [](https://docs.io.net/docs/retrieval-engine#communicating-with-the-retrieval-engine)
Once your documents are uploaded:
  * Enter your question in the chat field.
  * Retrieval Engine will analyze your request and search through your files to provide the most accurate answer.

![](https://files.readme.io/cd7b74e8d35d33a863a16f8f183557430b6c6b54d1f88aa6805c3c672efa7ce8-rag3.jpg)
#### [](https://docs.io.net/docs/retrieval-engine#the-response-will-include)
  * A clear and concise answer.
  * A breakdown of Retrieval Engine reasoning path — how it arrived at that answer.
  * A list of tools or agents that were used in processing your request.
  * A reference to source files used — whether from your uploaded content or external sources.

![](https://files.readme.io/43f99c45e492af682f4e1125a7c40ad928db6786fac79ea19b6715715e22965f-rag7.jpg)
### [](https://docs.io.net/docs/retrieval-engine#example-use-cases)
  * Research paper analysis
  * Enterprise document summarization
  * Legal document Q&A
  * Media file transcription and interpretation
  * Knowledge management for teams


about 1 month ago
* * *
  * [](https://docs.io.net/docs/retrieval-engine)
  *     * [What is Retrieval Engine?](https://docs.io.net/docs/retrieval-engine#what-is-retrieval-engine)
    * [Getting Started](https://docs.io.net/docs/retrieval-engine#getting-started)
    * [What You Can Do in the Retrieval Engine](https://docs.io.net/docs/retrieval-engine#what-you-can-do-in-the-retrieval-engine)
      * [1. Chat with Retrieval Engine](https://docs.io.net/docs/retrieval-engine#1-chat-with-retrieval-engine)
      * [2. **Upload Files**](https://docs.io.net/docs/retrieval-engine#2-upload-files)
      * [3. View File Information & Summaries](https://docs.io.net/docs/retrieval-engine#3-view-file-information--summaries)
      * [4. Delete Files](https://docs.io.net/docs/retrieval-engine#4-delete-files)
      * [5. Search Settings](https://docs.io.net/docs/retrieval-engine#5-search-settings)
    * [Communicating with the Retrieval Engine](https://docs.io.net/docs/retrieval-engine#communicating-with-the-retrieval-engine)
      * [The Response Will Include:](https://docs.io.net/docs/retrieval-engine#the-response-will-include)
    * [Example Use Cases](https://docs.io.net/docs/retrieval-engine#example-use-cases)



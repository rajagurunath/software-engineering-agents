# Agentic Workflow Editor
Build, connect, and execute powerful AI workflows using a visual, no-code interface. From simple task chains to full-blown multi-agent orchestration — without writing a single line of code.
## [](https://docs.io.net/docs/agentic-workflow#what-is-agentic-workflow)
**Agentic Workflow Editor** is a visual builder that lets you create and manage AI workflows composed of models, agents, tools, and task logic — like a modular intelligence engine.
Instead of scripting interactions between various models or APIs, you can drag components onto a canvas, configure them, connect them visually, and run the flow to see the outcome — all from your browser.
### [](https://docs.io.net/docs/agentic-workflow#who-is-this-for)
  * **AI Engineers & Researchers** – Quickly prototype multi-agent systems
  * **Data Scientists & Analysts** – Automate complex logic chains without coding
  * **Product / Ops Teams** – Connect AI models to business logic visually
  * **Consultants & Agencies** – Package workflows as reusable templates


## [](https://docs.io.net/docs/agentic-workflow#getting-started)
To begin using the Agentic Workflow Editor :
  1. **Go to your io.net Dashboard.**
  2. Navigate to the **[Agentic Workflow Editor](https://id.io.net/ai/agentic-workflow-editor)** under **IO Intelligence** section.
![](https://files.readme.io/8bd89ada3ee0343160527832b53ea3a26e84268fa63c2b463a4e6ea1ba98d4d5-AFW-1.jpg)
  3. Create a new workflow and start interacting with AI models.


### [](https://docs.io.net/docs/agentic-workflow#interface-overview)
Section | Description  
---|---  
**Left Sidebar** | Workflows list: folders, create new flow, rename/delete  
**Center Editor** | Visual flow builder: drag & drop components  
**Right Sidebar** | Settings for selected components  
**Bottom Panel** | Flow Outcome result: logs and execution steps  
## [](https://docs.io.net/docs/agentic-workflow#import-your-flow-before-starting)
  * Click **Import From YAML** button when you just created new flow in the center of the flow editor
![](https://files.readme.io/12bcdad467779bd3a3a3f4cac1b75161a47188df7d18f934008110e6746561a8-Artboard.jpg)
  * Upload `.yaml` file (max 1MB) 
  * Click **Generate Flow**
![](https://files.readme.io/0d5c4eb8771956ce49db919e89ef2d08bba4fe3b2388d79bd8f74beccfc4260e-Artboard3.jpeg)


## [](https://docs.io.net/docs/agentic-workflow#how-the-flow-working)
To design an effective agentic workflow, we recommend the following order:
### [](https://docs.io.net/docs/agentic-workflow#1-create-an-agent)
Start by adding an Agent component to represent your core logic and behavior. In the right sidebar, configure: `Agent Name`, `Instructions` (what it should do), `Swarm Name `(for group coordination if applicable)
![](https://files.readme.io/30edbb4345858afb1ecf950a90376b52d1e18ac3f315b346b55ae35888acfbb0-AFW-7.jpg)
> ## 🚧
> First, insert an Agent component. Then connect it to a Model, followed by Tasks or Tools.
### [](https://docs.io.net/docs/agentic-workflow#2-pick-an-ai-model)
Attach an AI Model to the Agent by clicking into the component and choosing from the available models in the right sidebar. This defines the core reasoning engine your agent will use.
  1. Click **Add Component** → Select **AI Model**
  2. Select the Component block → use right sidebar to:
     * Search and select an AI model
     * Click **Save**
![](https://files.readme.io/403d89dd39ff32b32c650752cf39315fb12b192ab97e925df020b539b13fe4d5-AFW-3.jpg)
  3. The block updates with the model name


### [](https://docs.io.net/docs/agentic-workflow#3-define-tasks)
Add Task components for specific steps your Agent will perform. Configure each task with: `Task ID`, `Name`, `Text`, `Client Mode (on/off)`
![](https://files.readme.io/5e275657c27e6e04000163741885596d014b515e5c49b1c2213b810513377461-AFW-8.jpg)
### [](https://docs.io.net/docs/agentic-workflow#4-connect-tools)
Use Tool components to integrate external capabilities — such as RAG search, cryptocurrency data, or web search. Tools allow **Agents** or **Tasks** to interact with these systems.
To use a Tool:
  * Add the **Tool** component to your flow.
  * Select one from the built-in list — no manual configuration is required.


Tool Name | Description  
---|---  
`r2r.list documents` | Lists documents with pagination.  
`r2r.rag search` | Performs a Retrieval-Augmented Generation (RAG) search.  
`listing coins` | Retrieves a paginated list of active cryptocurrencies.  
`get coin info` | Returns coin metadata like logo, description, links, and documentation.  
`get coin quotes` | Provides real-time price quotes for cryptocurrencies.  
`get coin quotes historical` | Returns historical price quotes.  
`search the web` | Performs a web search. Requires `text` input.  
`search the web async` | Performs a web search asynchronously. Requires `text` input.  
> ## 📘
> Note: When connecting components, remember — arrow always points from Agent or Task → Tool. Tools never initiate.
![](https://files.readme.io/19aa01d29c0c4fee1049b44dd46dab134da9aec9281a7af4da0fac3a0a0f2ee1-AFW-9.jpg)
### [](https://docs.io.net/docs/agentic-workflow#5-add-stages-optional)
Add Stage components to organize your workflow into sequential or parallel stages, each with defined objectives and context. Configure each Stage with: `Type`, `Objective`, `Result Type`, `Context`
![](https://files.readme.io/8e99b2e453e4346c015613084865cf33d9f936cb58fe07bd157e20c1ce9aa75a-AFW-10.jpg)
### [](https://docs.io.net/docs/agentic-workflow#6-connect-everything)
In the Agentic Workflow Editor, components are connected to define how data and logic flow between them.
  * **Agents** and **Tasks** are active components — they **initiate** actions.
  * **Tools** and **Models** are passive — they are **called** by Agents or Tasks.


#### [](https://docs.io.net/docs/agentic-workflow#valid-connection-examples)
  * Agent → Tool
  * Agent → Model
  * Task → Tool


#### [](https://docs.io.net/docs/agentic-workflow#invalid)
  * Tool → Agent
  * Tool → Task


> ## 📘
> Tools don’t initiate logic — they return results when triggered by another component.
**To create a connection:** Drag from the top-right circle of one block to another. This sets execution order and data flow
![](https://files.readme.io/081f4fee39c6cf3694d865314e6a9ffe774687164ce4f58eb955a7a78d7836af-Group_20.jpg)
**To remove a connection** : Hover over the connecting line, then click the cross icon to remove it. 
![](https://files.readme.io/c21c8645c4654b9cef7e248900cbaa382d8064527e66f66b1ce130ba0ab97f31-Group_21.jpg)
### [](https://docs.io.net/docs/agentic-workflow#7-run-and-review)
Hit Run to execute your flow and see step-by-step output in the Flow Outcome panel.
  * **Successful** real-time execution steps in **Flow Outcome**
![](https://files.readme.io/17d2edd51ab0997dc39affbc1ec606b97e5a2eea8bd7224abfdd469dce045203-AFW-4.jpg)
  * **Errors** (e.g., logic issues or invalid config) will be displayed clearly
![](https://files.readme.io/d4ace2ddeea2c660998a2f3c11752b2fe467217ad5e912a3c85b4c175547417e-AFW-5.jpeg)


### [](https://docs.io.net/docs/agentic-workflow#8-reposition-or-delete)
  * Drag components freely to organize your flow
  * **To delete a component:** Select the block in the editor, then click the **trash icon** in the right sidebar
![](https://files.readme.io/7a36f8ce885e5c453bfa79a7680228094d9950ca3cb9cc04a140fb8da4f5e80c-Artboard.jpg)


## [](https://docs.io.net/docs/agentic-workflow#saving-exporting)
  * Your work is **autosaved** , no need to click Save (see timestamp near Run). 
  * Click **⋮** three dots (top-right) to :
    * **Download as .yaml** your Flow
    * **Delete flow** from your account
![](https://files.readme.io/3547ad69bee77cf429fe5599adb669f2c8b5754587b4ab33c574118ed5c75d53-AWF-10.jpg)


## [](https://docs.io.net/docs/agentic-workflow#left-sidebar-workflows)
The left sidebar helps you organize and manage your workflows efficiently. Here's how it works:
  * **Search Bar**  
Quickly find any existing workflow by typing its name. 
  * **Add New Flow**  
Use the “+ Flow” button to start a new workflow inside the selected folder.
  * **Flow List**  
Displays all your existing workflows, grouped by folders.  
Each flow entry shows the number of components inside it, e.g. (2).
  * **Flow Actions** (Hover Options)  
When you hover over a flow in the list, additional options appear: 
    * **Edit** – Open the flow in the editor.
    * **Rename** – Update the flow name.
    * **Delete** – Permanently remove the flow (confirmation required).

![](https://files.readme.io/55601102ee1b143f9339f94f5988562c919625813549306a34628a9297d0befd-afw18.jpeg)
You can also collapse the left sidebar to maximize the workspace. Click the collapse arrow icon to hide or show the sidebar.
## [](https://docs.io.net/docs/agentic-workflow#canvas-tools)
  * Zoom In / Out using **+ / -** buttons
  * Use **Lock icon** to freeze layout
  * Use **Fit to View** to focus on working area
  * Collapse **Left / Bottom Panels** for full-screen editing

![](https://files.readme.io/d532e9ae63a970e884b53ae5408c79f55fb7d4f7f4173ccfad1be21a980c1739-AWF-14.jpeg)
## [](https://docs.io.net/docs/agentic-workflow#what-happens-under-the-hood)
Each flow is executed as an agentic graph:
  * Components are orchestrated via context-passing protocol
  * Execution supports branching, parallelism, and tool chaining
  * Flow outcome shows step-by-step logs, results, and failures


> ## 📘
> Note: execution is managed by IO’s internal orchestration engine, ensuring retry logic, state management, and observability.
## [](https://docs.io.net/docs/agentic-workflow#tips)
  * Start with an Agent → Connect an AI Model → Add Tasks and Tools
  * Keep blocks modular and reusable
  * Use Flow Outcome to debug before scaling
  * YAML export lets you version-control or share flows


## [](https://docs.io.net/docs/agentic-workflow#shortcuts--extras)
Action | How  
---|---  
Upload Flow | Click **Import From YAML** , select `.yaml`, click Generate  
Delete Flow | Click `⋮`, choose **Delete Flow** (confirmation popup)  
Export Flow | Click `⋮`, choose **Download YAML**  
Collapse Panels | Click arrows on **Left** or **Bottom** bars  
Fit View | Use **Zoom to Fit** icon  
15 days ago
* * *
  * [](https://docs.io.net/docs/agentic-workflow)
  *     * [What is Agentic Workflow?](https://docs.io.net/docs/agentic-workflow#what-is-agentic-workflow)
      * [Who is this for?](https://docs.io.net/docs/agentic-workflow#who-is-this-for)
    * [Getting Started](https://docs.io.net/docs/agentic-workflow#getting-started)
      * [Interface Overview](https://docs.io.net/docs/agentic-workflow#interface-overview)
    * [Import your flow before starting:](https://docs.io.net/docs/agentic-workflow#import-your-flow-before-starting)
    * [How the flow working](https://docs.io.net/docs/agentic-workflow#how-the-flow-working)
      * [1. Create an Agent](https://docs.io.net/docs/agentic-workflow#1-create-an-agent)
      * [2. Pick an AI Model](https://docs.io.net/docs/agentic-workflow#2-pick-an-ai-model)
      * [3. Define Tasks](https://docs.io.net/docs/agentic-workflow#3-define-tasks)
      * [4. Connect Tools](https://docs.io.net/docs/agentic-workflow#4-connect-tools)
      * [5. Add Stages (Optional)](https://docs.io.net/docs/agentic-workflow#5-add-stages-optional)
      * [6. Connect Everything](https://docs.io.net/docs/agentic-workflow#6-connect-everything)
      * [7. Run and Review](https://docs.io.net/docs/agentic-workflow#7-run-and-review)
      * [8. Reposition or Delete](https://docs.io.net/docs/agentic-workflow#8-reposition-or-delete)
    * [Saving, Exporting](https://docs.io.net/docs/agentic-workflow#saving-exporting)
    * [Left Sidebar: Workflows](https://docs.io.net/docs/agentic-workflow#left-sidebar-workflows)
    * [Canvas Tools](https://docs.io.net/docs/agentic-workflow#canvas-tools)
    * [What Happens Under the Hood?](https://docs.io.net/docs/agentic-workflow#what-happens-under-the-hood)
    * [Tips](https://docs.io.net/docs/agentic-workflow#tips)
    * [Shortcuts & Extras](https://docs.io.net/docs/agentic-workflow#shortcuts--extras)



# Deploy CaaS
Flexible & High-Performance Containers Built for Rapid Deployment and Scalable AI Workloads
IO.NET offers a simple and powerful interface for deploying containers using high-performance infrastructure. Whether you're running inference, training models, or hosting APIs, the Containers system gives you flexibility and speed.
This guide is intended for users who want to deploy using IO Cloud API keys on our CaaS clusters. For detailed API usage, refer to our [API Reference](https://docs.io.net/reference/get-started-with-caas-api)
## [](https://docs.io.net/docs/deploy-containers#deploy-container)
Click the "Deploy Container" button to launch a wizard that guides you through the deployment process.
![](https://files.readme.io/3516c8afcbb503d277926a87fd0571cdbb71614ebecd0f96d7ca551c007699db-Containers1.jpg)
## [](https://docs.io.net/docs/deploy-containers#container-deployment-wizard)
### [](https://docs.io.net/docs/deploy-containers#step-1-basic-deployment-settings)
Configure your container:
  * **Container Image** _(required)_  
Example: `myorg/myimage:latest`
  * **Image Type**
    * Public Image
    * Private Image
  * **Start Command**  
Enter the start command in JSON array format, example: 
JSON
```
["python3","-m","vllm.entrypoints.openai.api_server","--model"]

```

  * **Traffic Port** _(required)_  
Default: `8000`
  * **Environment Variables**  
Click **Add Variable** to define key-value pairs.  
Options: 
    * Normal Variable
    * Private Variable  
You can add or remove variables as needed.


Once all required fields are completed, click **Next Step**.
![](https://files.readme.io/32a23e67af9f05a46df9f0f99498ac37b4f3dd415c94c99333f51cb3b6b179b4-Containers2.jpg)
### [](https://docs.io.net/docs/deploy-containers#step-2-select-your-cluster-processor--location)
Choose the hardware and region for your deployment:
  * **Available GPUs**  
Search by GPU model and view: 
    * GPU Model
    * GPUs per Container
  * **Location Selection**  
After selecting a GPU, you'll see a list of locations showing: 
    * Region (e.g. Canada, Germany)
    * Available containers per location


Once both **GPU** and **location** are selected, proceed to the **next step**.
![](https://files.readme.io/fada87435d94daccfcaaa05513b5f3dc7e9a834e4a70ebb005bf2847734aed5f-Containers3.jpg)
### [](https://docs.io.net/docs/deploy-containers#step-3-summary)
On the Summary page, the choices you made in the process are displayed. You must select the number of Containers and the duration of time that you will use them. 
  1. In the **No. of Containers** field, select the number of Containers in the dropdown. 2 Containers will increase the cost. 
  2. In the **Enter Duration** field, select the length of time: Hourly, Daily, or Weekly. To the right, you can increase the quantity. 
  3. Review all the details of your cluster, including the **Total Cost**.
  4. Click **Deploy Cluster**.

![](https://files.readme.io/f3057dcfd2153e35cc6333fa037c8e21fd14cba6f8b856c4890ed889652ffceb-Containers4.jpg)
### [](https://docs.io.net/docs/deploy-containers#view-cluster)
After payment is processed you can view your cluster loading. 
![](https://files.readme.io/b30fc8f-Cluster_load.png)
Click **Return to Clusters** after your cluster is successfully deployed. The screenshot below is a detail page of your cluster.
![](https://files.readme.io/81a933f12f6aceaf4230ec194f9c0eeb9b268d910ba86d03801bfb4c4fceefc7-Bitmap.jpg)
5 days ago
* * *
  * [](https://docs.io.net/docs/deploy-containers)
  *     * [Deploy Container](https://docs.io.net/docs/deploy-containers#deploy-container)
    * [Container Deployment Wizard](https://docs.io.net/docs/deploy-containers#container-deployment-wizard)
      * [Step 1: Basic Deployment Settings](https://docs.io.net/docs/deploy-containers#step-1-basic-deployment-settings)
      * [Step 2: Select Your Cluster Processor + Location](https://docs.io.net/docs/deploy-containers#step-2-select-your-cluster-processor--location)
      * [Step 3: Summary](https://docs.io.net/docs/deploy-containers#step-3-summary)
      * [View Cluster](https://docs.io.net/docs/deploy-containers#view-cluster)



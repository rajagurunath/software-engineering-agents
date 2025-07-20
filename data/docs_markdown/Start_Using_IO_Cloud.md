# Start Using IO Cloud
Discover the simple steps for creating, configuring, deploying, and managing clusters, giving you complete control over your computing power.
## [](https://docs.io.net/docs/start-using-io-cloud#introduction)
IO Cloud enables the deployment and management of on-demand, decentralized GPU clusters, giving users access to powerful GPU resources without significant hardware investments or the complexity of managing infrastructure. IO Cloud democratizes GPU access by leveraging a decentralized model, providing machine learning engineers and developers with the same seamless experience as traditional cloud providers.
The platform utilizes a distributed network of nodes, IO workers, to offer flexible, scalable compute resources. IO Cloud clusters are self-healing, fully meshed GPU systems that ensure high availability and fault tolerance. With IO Cloud, you can tap into a decentralized network of GPUs and CPUs capable of running Python-based machine learning workloads. It is ideal for AI projects requiring distributed compute. The platform is natively built on the Ray framework, the same distributed computing technology used by OpenAI to train models like GPT-3 and GPT-4 across hundreds of thousands of servers.
  

## [](https://docs.io.net/docs/start-using-io-cloud#io-clouds-integration-flow)
The diagram below provides a high-level overview of how users integrate with IO Cloud - from choosing a compute resource to launching AI workloads. It illustrates the end-to-end flow across key components, including cluster selection, container deployment, and runtime execution.
![](https://files.readme.io/f317543b116c7a9e1ca2f52fb70034ee1796079973adb11871d6a244dde709b9-IO_Cloud_v3.jpg)
## [](https://docs.io.net/docs/start-using-io-cloud#create-account)
To create an account, go to [cloud.io.net](https://cloud.io.net/cloud/home). Currently, you can sign up using Google, Apple ID, X, or Worldcoin. Choose your preferred option, click **Sign Up** , and you're all set to join us.
#### 
[cloud.io.net](https://cloud.io.net/cloud/home)
[](https://docs.io.net/docs/start-using-io-cloud#go-to-cloudionet)
![](https://files.readme.io/278b46c-Step1.jpg)
#### [](https://docs.io.net/docs/start-using-io-cloud#payments)
IO Cloud simplifies the process of paying for GPU clusters by offering two convenient payment methods:
  * **Solana:** This cryptocurrency option enables fast, secure transactions. You can configure a Solana wallet either during account creation or through your Account Settings. Once configured, you can fund your wallet or proceed with payment for your GPU cluster.
  * **Credit Cards:** We accept all major credit cards, providing a straightforward payment solution.


To learn more about payment options, visit our [IO Cloud Payments](https://docs.io.net/docs/io-cloud-payments) page.
#### [](https://docs.io.net/docs/start-using-io-cloud#app-guide)
The home page offers the following options:
Action
Definition
Deploy a Cluster
Create a new cluster for your workloads.
Browse the GPU Marketplace
Explore and select GPUs for your clusters.
Add Funds to Your Balance
Top up your account for cluster usage.
View and Monitor Your Clusters
Track the status and performance of your existing clusters.
  

## [](https://docs.io.net/docs/start-using-io-cloud#clusters)
io.net offers three distinct cluster types to power your AI projects:
![](https://files.readme.io/6bc0b6e9298d06a9c4ca84121681dd7dbec173b401dea926e5a600471b020dc0-IOClouds.jpg)
### [](https://docs.io.net/docs/start-using-io-cloud#ray-cluster)
Designed to run distributed applications efficiently across multiple nodes.
  * **Powered by the Ray framework:** A widely-used open-source framework for building and managing distributed applications.
  * **Universal API:** Delivers a consistent interface for creating and managing distributed applications across various hardware configurations.
  * **Scalable Infrastructure:** Comprises multiple interconnected nodes collaborating to execute tasks and manage resources efficiently.


To view detailed instructions on Ray clusters, see [Deploy Ray Cluster](https://docs.io.net/docs/deploy-ray-cluster).
### [](https://docs.io.net/docs/start-using-io-cloud#mega-ray-cluster)
Enables you to select and rent from a broader range of available GPUs or CPUs, offering even greater resource allocation flexibility than a standard Ray-based cluster.
  * **Powered by the Ray framework:** Similar to a standard Ray cluster but with enhanced flexibility.
  * **On-Demand Resource Allocation:** You can rent available GPUs or CPUs based on tailored filters for your project's needs.
  * **Dynamic Scaling:** Provides greater resource management control than a fixed-size Ray cluster.


To view detailed instructions on Ray clusters, see [Deploy Mega-Ray Cluster](https://docs.io.net/docs/deploy-mega-ray-cluster).
### [](https://docs.io.net/docs/start-using-io-cloud#bare-metal-on-demand)
Gives you full access to physical hardware without any virtualization layer — ideal for low-level control and maximum performance.
  * **Direct-to-Hardware Access:** Run workloads directly on machines for optimal speed and isolation.
  * **No Virtualization Overhead:** Perfect for users with specialized or custom environments.
  * **Custom Configuration:** Choose your processor and location, then deploy instantly.


To view detailed instructions, see [Deploy Bare Metal Instance](https://docs.io.net/docs/deploy-bare-metal-cluster).
### [](https://docs.io.net/docs/start-using-io-cloud#container-as-a-service-caas)
Allows you to configure and deploy containers on powerful GPU-backed infrastructure through a simple, guided interface.
  * **Step-by-Step Wizard:** Set image, command, ports, environment variables, and more.
  * **Cluster & Location Choice:** Select from available GPUs and regions that meet your needs.
  * **Scalable & Fast:** Built for AI and compute-heavy workloads with rapid setup.


To view detailed instructions, see [Deploy Container](https://docs.io.net/docs/deploy-containers).
## [](https://docs.io.net/docs/start-using-io-cloud#clusters-tabs)
The Cluster tabs provide a central hub for managing your deployed clusters. Each tab displays a list of clusters, categorized by type, with details such as:
  * **Name:** The unique identifier for the cluster.
  * **Accelerator (GPU):** The type of GPU used in the cluster.
  * **Status:** The current state of the cluster (e.g., running, stopped, pending).
  * **Remaining Compute Hours:** The remaining time on your cluster's billing cycle.

![](https://files.readme.io/78530e4-view_cluster_tab.png)
From here, you can perform actions like:
  * **Rename:** Change the name of a cluster.
  * **Extend:** Increase the duration of your cluster's billing cycle.
  * **Terminate:** Stop and delete a cluster.


Each cluster tab also provides quick access to essential management tools:
  * **Visual Studio:** An integrated code editing and debugging development environment.
  * **Jupyter Notebook:** An interactive environment for data analysis and visualization.
  * **Ray Dash:** A dashboard for monitoring and managing distributed applications.


For a detailed explanation of monitoring and managing your clusters, see [Monitor and Manage Clusters](https://docs.io.net/docs/monitor-manage-clusters).
![](https://files.readme.io/f3981a0-view_cluster2.png)
5 days ago
* * *
  * [](https://docs.io.net/docs/start-using-io-cloud)
  *     * [Introduction](https://docs.io.net/docs/start-using-io-cloud#introduction)
    * [IO Clouds Integration Flow](https://docs.io.net/docs/start-using-io-cloud#io-clouds-integration-flow)
    * [Create Account](https://docs.io.net/docs/start-using-io-cloud#create-account)
    * [Clusters](https://docs.io.net/docs/start-using-io-cloud#clusters)
      * [Ray Cluster](https://docs.io.net/docs/start-using-io-cloud#ray-cluster)
      * [Mega-Ray Cluster](https://docs.io.net/docs/start-using-io-cloud#mega-ray-cluster)
      * [Bare Metal on Demand](https://docs.io.net/docs/start-using-io-cloud#bare-metal-on-demand)
      * [Container-as-a-Service (CaaS)](https://docs.io.net/docs/start-using-io-cloud#container-as-a-service-caas)
    * [Clusters Tabs](https://docs.io.net/docs/start-using-io-cloud#clusters-tabs)



# Deploy Ray Cluster
This document explains how to deploy a Ray cluster by leveraging compute power in io.net's DePIN network.
## [](https://docs.io.net/docs/deploy-ray-cluster#payments)
IO Cloud customers can load their io.net account prior to deploying clusters, or they can pay at the end of the deploy process. The main two ways to pay for clusters is using Solana and credit cards. To use Solana, you must set up a wallet. This can be done when you register your account or later in **Account Settings**. 
To learn more about the types of payments we offer and step-by-step guides, see [IO Cloud Payments](https://docs.io.net/docs/io-cloud-payments).
## [](https://docs.io.net/docs/deploy-ray-cluster#configure-cluster)
### [](https://docs.io.net/docs/deploy-ray-cluster#1-create-cluster)
Select Ray from the Cluster menu.
![](https://files.readme.io/7be3fe5c51a8696d5933b951897f4b8bee94387cce8aa1d73c2bd54df2b793e9-Ray1.jpg)
### [](https://docs.io.net/docs/deploy-ray-cluster#2-select-cluster-type)
Select the cluster type that meets the scope of your project.
  * **General** - This option works well for prototyping or general E2E workloads. 
  * **Inference** - Choose if you require production-ready clusters for low-latency inference and heavy workloads. 
  * **Train** - Choose if you require production-ready clusters for machine learning models, training, and fine-tuning. 

![](https://files.readme.io/c35726eb588c50a0ed8ba435617b98b29b97096e364fc861a5da644eb22d2a9b-Bitmap2.jpeg)
### [](https://docs.io.net/docs/deploy-ray-cluster#3-rename-cluster)
Click the pencil icon to the right of the name to rename your cluster. In the screenshot below, the icon is highlighted in the blue box. Provide a unique name for your cluster. 
![](https://files.readme.io/eb660e1-rename.png)
Click **Next Step**. 
### [](https://docs.io.net/docs/deploy-ray-cluster#4-security-compliance)
Select the level and type of security for your cluster.
  * **E2E Encrypted** - A method of secure communication that prevents bad actors from accessing data while it's transferred. It restricts data access to the sender and recipient. All data traffic between GPUs is encrypted.
  * **SOC2/HIPAA** - (Coming Soon) A framework for managing and securing data related to technology and cloud computing services. All data traffic between GPUs is encrypted. 

![](https://files.readme.io/8a79ab3-sec_com.png)
Click **Next Step**. 
### [](https://docs.io.net/docs/deploy-ray-cluster#5-location)
To select a location for our GPUs, enter a country name in the Search field or browse the country list (screenshot below is truncated). You can select multiple locations. Residents of countries with strict data residency can use this option to meet those requirements.
> ## 📘
> One reason to select a specific location is to reduce latency. If you're located in USA and select USA for location, then your clients can get results more quickly if, for example, your GPUs are inferencing.
![](https://files.readme.io/23f3bce-ray_location.png)
Click **Next Step**.
### [](https://docs.io.net/docs/deploy-ray-cluster#6-connectivity-tiers)
Select the connectivity speed for your project. 
  * **Ultra High Speed** - Download 1600 MB/s / 1200 MB/s Upload
  * **High Speed** - Download 800 MB/s / 600 MB/s Upload
  * **Medium** - Download 400 MB/s / 300 MB/s Upload
  * **Low Speed** - Download 100 MB/s / 10 MB/s Upload

![](https://files.readme.io/2991dc1-connect_ray.png)
Click **Next Step**.
### [](https://docs.io.net/docs/deploy-ray-cluster#7-select-gpus)
Select the type of computing your project requires, **GPU** or **CPU**.
  * If you select GPU, also select NVIDIA and browse for the model that satisfies your requirements. 
  * If you select CPU, you can choose between Apple of AMD CPUs. 

![](https://files.readme.io/2507166-ray_clus_select.png)
Click **Next Step**.
### [](https://docs.io.net/docs/deploy-ray-cluster#8-cluster-base-image)
Ray is the only selection for now. We will release additional cluster base images soon such as:
  * IOG
  * Ludwig
  * Pytorch FSDP
  * Unreal Engine 5
  * Unity Streaming  
  


![](https://files.readme.io/67a82eda17320fe5cd529db6bc82da5071188c4aa556096236702b858512991d-Bitmap.jpg)
Click **Next Step**.
### [](https://docs.io.net/docs/deploy-ray-cluster#9-master-configuration)
All clusters include a preconfigured master node. These nodes are selected by io.net from reliable and security compliant data centers.
![](https://files.readme.io/78bc942-ray_ms_config.png)
Click **Next Step**.
### [](https://docs.io.net/docs/deploy-ray-cluster#10-summary)
On the Summary page, the choices you made in the process are displayed. You must select the number of GPUs and the duration of time that you will use them. 
  1. In the **Enter GPUs Quantity** field, select the number of GPUs in the dropdown. 2 GPUs will increase the cost. 
  2. In the **Enter Duration** field, select the length of time: Hourly, Daily, or Weekly. To the right, you can increase the quantity. 
  3. Review all the details of your cluster, including the **Total Cost**.
  4. Click **Deploy Cluster**. 

![](https://files.readme.io/3142dc3-fees1.png)
### [](https://docs.io.net/docs/deploy-ray-cluster#view-cluster)
After payment is processed you can view your cluster loading. 
![](https://files.readme.io/b30fc8f-Cluster_load.png)
Click **Return to Clusters** after your cluster is successfully deployed. The screenshot below is a detail page of your cluster. 
![](https://files.readme.io/72c4867-view_cluster2.png)
5 days ago
* * *
  * [](https://docs.io.net/docs/deploy-ray-cluster)
  *     * [Payments](https://docs.io.net/docs/deploy-ray-cluster#payments)
    * [Configure Cluster](https://docs.io.net/docs/deploy-ray-cluster#configure-cluster)
      * [1. Create Cluster](https://docs.io.net/docs/deploy-ray-cluster#1-create-cluster)
      * [2. Select Cluster Type](https://docs.io.net/docs/deploy-ray-cluster#2-select-cluster-type)
      * [3. Rename Cluster](https://docs.io.net/docs/deploy-ray-cluster#3-rename-cluster)
      * [4. Security Compliance](https://docs.io.net/docs/deploy-ray-cluster#4-security-compliance)
      * [5. Location](https://docs.io.net/docs/deploy-ray-cluster#5-location)
      * [6. Connectivity Tiers](https://docs.io.net/docs/deploy-ray-cluster#6-connectivity-tiers)
      * [7. Select GPUs](https://docs.io.net/docs/deploy-ray-cluster#7-select-gpus)
      * [8. Cluster Base Image](https://docs.io.net/docs/deploy-ray-cluster#8-cluster-base-image)
      * [9. Master Configuration](https://docs.io.net/docs/deploy-ray-cluster#9-master-configuration)
      * [10. Summary](https://docs.io.net/docs/deploy-ray-cluster#10-summary)
      * [View Cluster](https://docs.io.net/docs/deploy-ray-cluster#view-cluster)



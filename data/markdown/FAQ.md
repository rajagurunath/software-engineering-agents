# FAQ
Straightforward answers to general queries.
##### [](https://docs.io.net/docs/faq#q-what-is-ionets-mission-and-what-are-you-working-towards)
io.net is a decentralized GPU network designed to give unlimited computing power to ML applications. We make computing more scalable, accessible, and efficient. Our mission is to unlock fair access to computing power by assembling 1 million + GPUs from independent data centers, crypto miners, and crypto projects such as Filecoin or Render.
##### [](https://docs.io.net/docs/faq#q-how-big-is-the-gpu-shortage-how-is-ionet-solving-it)
The major cloud providers currently have around 10-15 exaFLOPS of GPU compute capacity available. However, given the surging volume of AI/ML model training and inferencing workloads, the potential demand for GPU compute in the cloud could be as high as 20-25 exaFLOPS.
This suggests the current shortage in cloud GPU capacity is likely in the range of 5-10 exaFLOPS. In the near future, cloud GPU capacity must expand 2- 3 times current levels in order to meet user demand.
There is a long lead time to increase GPU supply which suggests that this problem won't be resolved any time soon.
io.net is solving this by accessing underutilized GPU sources outside of the cloud such as:
  * Independent data centers: There are thousands of independent data centers in the US alone, and their average utilization rate is only 12% - 18%.
  * Crypto miners: Miners have suffered significant losses with Ethereum’s switch to Proof-of-Stake. They can repurpose GPUs in our DePin network. 
  * Consumer GPUs: Consumer GPUs account for 90% of the total supply yet the majority of these resources are latent in consumer households and small cloud farms. 


When combined, it is estimated these sources can provide an additional 200 exaFLOPs of GPU capacity.
##### [](https://docs.io.net/docs/faq#q-how-is-ionet-different-from-aws)
io.net offers a fundamentally different approach to cloud computing. We leverage a distributed and decentralized model that provides increased control and flexibility for users. io.net's services don't involve complicated permission models and it's cost efficient. The combination of all these factors sets io.net in its own league of Decentralized providers.
##### [](https://docs.io.net/docs/faq#q-how--why-is-ionet-cheaper-and-faster-than-other-providers-like-aws)
io.net is significantly more affordable and faster than current cloud solutions. By leveraging underutilized sources, such as independent data centers, crypto miners, and consumer GPUs, we offer compute for up to 90% less than traditional cloud providers.
We are significantly faster than the competition because creating distributed clusters through traditional cloud providers is a time-consuming process. Companies like AWS often ask for detailed KYC information, require long-term contracts, and often have waitlists for the most desired hardware. It can often take two weeks to obtain GPU compute from cloud providers.
io.net doesn't impose these restrictions which allows users to access GPU supply and deploy clusters in less than 90 seconds. Ultimately, the combination of speed and cost allows io.net to be 10x to 20x more efficient than traditional cloud providers.
##### [](https://docs.io.net/docs/faq#q-what-is-a-depin-and-how-does-ionet-fit)
DePIN, or Decentralized Physical Infrastructure Networks, leverages blockchains, IoT, and the greater Web3 ecosystem to create, operate and maintain real-world physical infrastructure. These networks use token incentives to coordinate, reward, and safeguard members of the network. io.net is the first and only GPU DePIN. We are optimized for machine learning but are also ideal for all GPU use cases. 
##### [](https://docs.io.net/docs/faq#q-what-type-of-gpus-does-ionet-offer)
We offer a wide range of:
  * GPUs, including NVIDIA RTX series, and AMD Ryzen series.
  * CPUs, including Intel, AMD, and the Apple M3/M4 Chip with its unparalleled neural engine.


Please refer to (pricing page) to see the full list of supported GPUs. Contact our support team if your hardware is not listed.
Our minimum requirements are:
  * +12 GB of RAM
  * +500 GB Free Disk Space
  * Internet Speed : Download +500 MBs and +250 Mbps Upload with < 30ms ping


Test your internet from here: <https://www.speedtest.net>
##### [](https://docs.io.net/docs/faq#q-why-is-ionet-needed-for-machine-learning)
io.net is natively built on top of ray.io, a machine-learning framework for distributed computing. This is the same framework used by open.ai to train GPT3 over 300k CPUs and 20k GPU. You can use io.net to distribute your AI and Python applications for reinforcement learning to deep learning, to tuning, and model serving - across an extensive grid of GPUs.
We are set to support all the frameworks that ML engineers use for workload distribution, including Anyscale, Pytorch FSDP, TensorFlow, and Predibase.
##### [](https://docs.io.net/docs/faq#q-who-are-your-target-customers)
Anyone looking to create or operate an ML model or AI app is a potential customer. Due to the explosion of “no-code tools” like Predibase and model creation platforms like Hugging Face, this will eventually be a massive market.
##### [](https://docs.io.net/docs/faq#q-how-do-we-manage-availability-and-allocation-to-users-across-your-global-network-of-gpus)
io.net connects a global network of clients to a global network of suppliers. We deploy our container on each worker machine, facilitating the io.net Virtual Network's integration and monitoring of all device availability across the network. Our algorithm intelligently groups resources, matching the selections made by the engineer and glues them into a cluster, all within 90 seconds. Our networking solution has been thoroughly tested and found reliable.
##### [](https://docs.io.net/docs/faq#q-what-is-the-connectivity-requirement-for-suppliers)
  * We are offering clients different tiers of connectivity, from low to ultra high. While our absolute minimum connectivity requirement is 250 Mbps, we strongly encourage suppliers to support at least 1 Gbps download and upload speeds to remain attractive to demand-side customers.
  * We expect data traffic to average 5GB / hour.


##### [](https://docs.io.net/docs/faq#q-can-i-customize-cluster-creation)
Clients can create their cluster with unmatched flexibility through a set of selections and options: cluster type by use case, sustainability (e.g., “Green GPUs” powered by 100% clean energy), geographic location, security compliance level (SOC2, HIPAA, end-to-end encryption), connectivity tier, and cluster purpose (currently Ray App, but more options available soon). Our out-of-the-box configuration requires no additional setup by our clients to deploy the cluster.
##### [](https://docs.io.net/docs/faq#q-explain-the-pricing-model-do-pricing-tiers-differ-based-on-gpu-model--performance)
Prices are automatically determined based on supply and demand; GPU specs, such as internet speed, GPU make and model, security / compliance certifications, etc., will also affect pricing. For example, enterprise-grade GPUs with SOC2 compliance and >2 Gbps cost more than consumer-grade GPUs without SOC2 compliance and slower connectivity.
##### [](https://docs.io.net/docs/faq#q-whats-the-maximum-amount-of-gpus-allowed-in-a-single-cluster)
The only limitation for your cluster size is the total available supply of GPUs.
##### [](https://docs.io.net/docs/faq#q-how-long-does-it-take-to-create-a-cluster-of-gpus)
It takes less than 90 seconds to create a cluster on io.net.
##### [](https://docs.io.net/docs/faq#q-is-it-possible-to-adjust-the-number-of-gpus-in-my-cluster-as-my-requirements-change)
Yes it is possible to adjust the number of GPUs either with Auto Scaling or by manually adding nodes to your cluster.
##### [](https://docs.io.net/docs/faq#q-what-is-the-minimum-and-maximum-duration-for-gpu-cluster-rentals)
There is a one hour minimum for clusters. You can rent GPUs for as long as you need them, there is no time limit. 
##### [](https://docs.io.net/docs/faq#q-does-the-docker-container-launch-with---privileged-flag)
No, the Docker container does not launch with the --privileged flag.
##### [](https://docs.io.net/docs/faq#q-why-do-we-mount-the-docker-socket-while-starting-the-containers)
The platform manages the device states and usage through the orchestration of docker containers. You must mount the docker socket to manage docker containers on the worker node. This is mandatory for the platform and there are currently no plans or alternatives to remove this.
##### [](https://docs.io.net/docs/faq#q-isnt-mounting-docker-socket-and---privileged-flag-the-same)
While the --privileged flag gives broad system access to a container, mounting the Docker socket gives the container control over Docker on the host.
##### [](https://docs.io.net/docs/faq#q-why-do-you-use-docker-containers)
Our platform enables clustering GPU compute and provides the end user of the platform with a production ready environment for distributed training. The custom docker images contain all the required drivers and environments. All the required libraries are installed, enabling efficient utilization of GPU and CPU resources that are required for distributed training. 
For suppliers, reproducing our environment is challenging and can result in irregularities based on the worker platform (linux, windows). Docker helps to stabilize this issue. Distributed training can only function if the environment is replicated on all nodes.
##### [](https://docs.io.net/docs/faq#q-do-you-have-proof-of-compute--verification-what-kind-of-proof-do-you-use-)
**Current Industry Protocol**
It's primarily accomplished with validators that randomly replicate compute jobs on the network and verify that it matches the results provided by participants. Secondly, with a rewards punishment system that ensures that participants are not providing false results since the compute is done off chain. Thirdly, through proof of learning which is an anti-cheat mechanism based on logs provided by user that detail their compute process and some other steps.
This proof of compute isn't mature and hasn't proven itself as its efficacy remains theoretical. In proof-of-work systems, due to the sequential nature of computations, validating work at a specific point requires completing all previous work up to that point. There are many other obstacles and challenges associated with this model.
**io.net Protocol**
io.net leverages the existing model, taking advantage of its benefits and enhancing its strengths with our improvements. Our compute service operates on an hourly basis, allowing users to book clusters for specific periods of time. Since our service is time based rather than compute based, we simply need to prove that the GPU's compute power is completely available when it's rented.
This is achieved with io.net's innovative concept of Proof: **Proof of Time-Lock**. This provides proof that the GPUs were not accessed by any other services or threads that would diminish compute power during the time it was rented. We can prove that from the start of the rental period (T1) until the end (T2), the GPU is 100% committed to the AI/ML jobs running on the device. This proof consists of multiple steps that benchmarks:
  * Consumption
  * Monitoring containers 
  * Eliminating foreign processes 
  * A punishment and rewards system to ensure that all workers are compliant 


All this is accomplished with io.net's revolutionary AI, which learns at a granular level with each cluster booking to ensure fairness and maintain a trusted environment throughout the entire process.
##### [](https://docs.io.net/docs/faq#q-how-do-you-mitigate-latency-issues)
  * io.net's flexible system features our algorithm that intelligently groups resources and matches their Connectivity Speed, Geolocations, and Hardware Specs to eliminate bottlenecks and reduce latency.
  * Our distribution technology on Ray and Mesh networks ensures that data travels along multiple paths which increases redundancy, fault tolerance, while improved load distribution minimizes latency.
  * When VPNs are used to increase security it often results in increased latency. In order to offer robust security with minimal latency, we employ a kernel-level VPN that uses one of the most secure mesh VPN protocols, ensuring high security without compromising network performance.
  * The majority of our GPU supply is hosted by Tier 3 - 4 data centers and advanced mining facilities. Quality infrastructure results in low latency. Our reports indicate that over 40% of our supply has internet speeds surpassing those of Lambda Labs Cloud.


##### [](https://docs.io.net/docs/faq#q-how-do-you-parallelize--how-are-you-connecting-all-the-gpus-together)
**Distribution and decentralization** : We leverage Ray with specialized libraries for data streaming, training, fine-tuning, hyperparameter tuning. When our technology is combined with Mesh VPN, it results in a streamlined process for developing and deploying large-scale AI models across a vast network of GPUs. 
##### [](https://docs.io.net/docs/faq#q-how-do-you-ensure-data-privacy-and-security)
Our **IO** agent eliminates risks by detecting and blocking unauthorized containers from running on a hired GPU. When a node is hired, data between worker nodes is encrypted within the Docker file system. Network traffic is on a mesh VPN, providing maximum security. **We also prioritize suppliers with SOC2 compliance** and continue to stress the importance of SOC2 compliance with our suppliers.
19 days ago
* * *
  * [](https://docs.io.net/docs/faq)
  *     * [Q: What is io.net's mission, and what are you working towards?](https://docs.io.net/docs/faq#q-what-is-ionets-mission-and-what-are-you-working-towards)
    * [Q: How big is the GPU shortage? How is io.net solving it?](https://docs.io.net/docs/faq#q-how-big-is-the-gpu-shortage-how-is-ionet-solving-it)
    * [Q: How is io.net different from AWS?](https://docs.io.net/docs/faq#q-how-is-ionet-different-from-aws)
    * [Q: How & why is io.net cheaper and faster than other providers like AWS?](https://docs.io.net/docs/faq#q-how--why-is-ionet-cheaper-and-faster-than-other-providers-like-aws)
    * [Q: What is a DePIN and how does io.net fit?](https://docs.io.net/docs/faq#q-what-is-a-depin-and-how-does-ionet-fit)
    * [Q: What type of GPUs does io.net offer?](https://docs.io.net/docs/faq#q-what-type-of-gpus-does-ionet-offer)
    * [Q: Why is io.net needed for machine learning?](https://docs.io.net/docs/faq#q-why-is-ionet-needed-for-machine-learning)
    * [Q: Who are your target customers?](https://docs.io.net/docs/faq#q-who-are-your-target-customers)
    * [Q: How do we manage availability and allocation to users across your global network of GPUs?](https://docs.io.net/docs/faq#q-how-do-we-manage-availability-and-allocation-to-users-across-your-global-network-of-gpus)
    * [Q: What is the connectivity requirement for suppliers?](https://docs.io.net/docs/faq#q-what-is-the-connectivity-requirement-for-suppliers)
    * [Q: Can I customize cluster creation?](https://docs.io.net/docs/faq#q-can-i-customize-cluster-creation)
    * [Q: Explain the pricing model? Do pricing tiers differ based on GPU model / performance?](https://docs.io.net/docs/faq#q-explain-the-pricing-model-do-pricing-tiers-differ-based-on-gpu-model--performance)
    * [Q: What's the maximum amount of GPUs allowed in a single cluster?](https://docs.io.net/docs/faq#q-whats-the-maximum-amount-of-gpus-allowed-in-a-single-cluster)
    * [Q: How long does it take to create a cluster of GPUs?](https://docs.io.net/docs/faq#q-how-long-does-it-take-to-create-a-cluster-of-gpus)
    * [Q: Is it possible to adjust the number of GPUs in my cluster as my requirements change?](https://docs.io.net/docs/faq#q-is-it-possible-to-adjust-the-number-of-gpus-in-my-cluster-as-my-requirements-change)
    * [Q: What is the minimum and maximum duration for GPU cluster rentals?](https://docs.io.net/docs/faq#q-what-is-the-minimum-and-maximum-duration-for-gpu-cluster-rentals)
    * [Q: Does the docker container launch with --privileged flag?](https://docs.io.net/docs/faq#q-does-the-docker-container-launch-with---privileged-flag)
    * [Q: Why do we mount the Docker socket while starting the containers?](https://docs.io.net/docs/faq#q-why-do-we-mount-the-docker-socket-while-starting-the-containers)
    * [Q: Isn't mounting docker socket and --privileged flag the same?](https://docs.io.net/docs/faq#q-isnt-mounting-docker-socket-and---privileged-flag-the-same)
    * [Q: Why do you use docker containers?](https://docs.io.net/docs/faq#q-why-do-you-use-docker-containers)
    * [Q: Do you have proof of compute / verification, what kind of proof do you use ?](https://docs.io.net/docs/faq#q-do-you-have-proof-of-compute--verification-what-kind-of-proof-do-you-use-)
    * [Q: How do you mitigate latency issues?](https://docs.io.net/docs/faq#q-how-do-you-mitigate-latency-issues)
    * [Q: How do you parallelize? / How are you connecting all the GPUs together?](https://docs.io.net/docs/faq#q-how-do-you-parallelize--how-are-you-connecting-all-the-gpus-together)
    * [Q: How do you ensure data privacy and security?](https://docs.io.net/docs/faq#q-how-do-you-ensure-data-privacy-and-security)



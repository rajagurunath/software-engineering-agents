# Device Onboarding
This document provides instructions about how to create an account, device onboarding basics, block rewards, staking, and statuses to assist in you in the onboarding process.
### [](https://docs.io.net/docs/device-onboarding#table-of-contents)
  * [Create Account](https://docs.io.net/docs/device-onboarding#create-account)
  * [Requirements](https://docs.io.net/docs/device-onboarding#requirements)
  * [Set Up a New Worker](https://docs.io.net/docs/device-onboarding#set-up-a-new-worker)
  * [App Guide](https://docs.io.net/docs/device-onboarding#app-guide)
    * [Workers Homepage](https://docs.io.net/docs/device-onboarding#workers-homepage)
    * [Device Status](https://docs.io.net/docs/device-onboarding#device-status)
    * [Readiness](https://docs.io.net/docs/device-onboarding#readiness)
    * [Transition Between States](https://docs.io.net/docs/device-onboarding#transition-between-states)
  * [Troubleshoot](https://docs.io.net/docs/device-onboarding#troubleshoot)


### [](https://docs.io.net/docs/device-onboarding#create-account)
To create an account, go to [worker.io.net](https://worker.io.net/). Currently, you can sign up using Google, Apple ID, X, or Worldcoin. Choose your preferred option, click **Sign Up** , and you're all set to join us.
#### 
[worker.io.net](https://worker.io.net)
[](https://docs.io.net/docs/device-onboarding#go-to-workerionet)
![](https://files.readme.io/278b46c-Step1.jpg)
### [](https://docs.io.net/docs/device-onboarding#requirements)
Devices that meet the [minimum system requirements](https://docs.io.net/docs/device-onboarding#minimum-system-requirements) are eligible for job assignments. All devices must pass our [Proof of Work](https://docs.io.net/docs/proof-of-work) verification through the Worker to be hired by clusters.
To view a list of the current supported devices, see [Supported Devices](https://docs.io.net/docs/supported-devices). 
> ## 📘
> After your onboard your device for the first time, there is a 12 hour waiting period until it's eligible to be hired as a worker. Your device is only subject to the waiting period after its initial onboarding.
#### [](https://docs.io.net/docs/device-onboarding#minimum-system-requirements)
  * 12 GB RAM
  * 256 GB SSD
  * Windows: NVIDIA GeForce RTX 30xx and above series / MacOS: Apple M3, M4.
  * Internet Speed (please use [speedtest.net](https://www.speedtest.net/) or a similar service to check your speed)  
To qualify for the airdrop, the minimum requirement is 100Mb/s download and 75Mb/s upload. However, for a higher chance of being hired, the recommended minimum requirements are: 
    * Download: Above 500 Mb/s
    * Upload: Above 250 Mb/s
    * Ping: Below 30ms


> ## 📘
> For better performance, we recommend a download/upload speed of 200–500 Mbps and 16GB of RAM to avoid crashes.
#### [](https://docs.io.net/docs/device-onboarding#staking)
Your must stake to your device to make it eligible for block rewards and to be hired for jobs. For more information about staking, see our [Staking](https://docs.io.net/docs/io-staking) documentation. 
### [](https://docs.io.net/docs/device-onboarding#set-up-a-new-worker)
We have detailed guides available to help you set up your worker on various operating systems such as:
  * [MacOS](https://docs.io.net/docs/install-on-macos)
  * [Windows](https://docs.io.net/docs/install-on-windows)
  * [Ubuntu](https://docs.io.net/docs/install-on-ubuntu)
  * [HiveOS](https://docs.io.net/docs/install-on-hiveos)


These guides are tailored to provide step-by-step instructions, ensuring a smooth setup process for your new worker. Whether you're using MacOS, Windows or Ubuntu, you'll find comprehensive guidance to join get your worker up and running efficiently.
## [](https://docs.io.net/docs/device-onboarding#app-guide)
### [](https://docs.io.net/docs/device-onboarding#workers-homepage)
This screen provides users with real-time access to general information about all their calculations. Users can easily see who is connected to the network, currently active, or experiencing errors. Additionally, they can perform actions like renaming and deleting devices.
For users managing a large number of devices, features like search and sorting by criteria such as Status, Brand, Technology, Connectivity Tier, and Security Compliance are invaluable.
This page allows you to monitor workers and track data such as:
  * **Status**
  * **Device ID-** The unique identifier for your device. Click the ID to view the Device Detail page.
  * **Readiness** - This value provides insights into your device's readiness for Block Reward eligibility.
  * **Up For**
  * **Chip/GPUs**

![](https://files.readme.io/9d4cc63-devlist.png)
### [](https://docs.io.net/docs/device-onboarding#device-status)
**Device Status** is displayed at the top of the table. 
![](https://files.readme.io/59808221f52c12d37dddea6a7d91cd503dd36d01b2e15fa893633fc373f92464-status.png)
Status 
Description 
🟢 up/running 
Running status is indicative that everything installed correctly and everything is in normal operations. No issues. 
🟢 Idle 
Idle status is indicative that everything installed correctly and everything is in normal operations but it has not been hired by someone yet. It is awaiting work. No issues.
🟡 Paused 
Paused status is indicative that the client has manually suspended or disabled the node. They can resume it themselves. 
🔴 Down 
Down status is indicative that a worker is down. and needs to re-run the commands. 
🔴 Failed 
Failed status is indicative of a connection/outage problem or the device is offline.  
The device is not communicating and is unavailable or experiencing another form of outage such as:
  * Error during startup: There may have been errors during the startup of your worker that prevented it from launching successfully.
  * Resource issues: It's possible that there aren't enough resources available for your worker to start, such as allocated memory, CPU time, or other resources.
  * Network failure: Network issues can prevent the establishment of connection with the platform or other services, leading to startup failures.


🟠 Blocked 
Blocked status is indicative that we detected GPU utilization that was not authorized by our internal checks. It's important that GPU availability is dedicated 100% to the task being volunteered for the health of the DePin.
Blocked status occurs in a few different flavors, but mainly these:
  * Excessive GPU Utilization: Playing games, Graphic intensive utilization, etc. (You'll need to pause it before you start usage)
  * Mining Detection: FYI - Our team has implemented an update to detect mining devices and instances with high GPU usage, resulting in an automatic ban.


🟣 Unsupported device 
Unsupported status is indicative that your worker or its current configuration is not supported into the IO.NET platform at this moment. This could be due to incompatibility with the required software version, operating system, or hardware components. The list of supported devices can be checked [here](https://docs.io.net/docs/supported-devices)
🟣 Inactive 
Inactive status is indicative that your worker has been inactive for more than 5 days. This may have been caused by pausing a worker and forgetting about it, an outage, or a technical / communication issue. 
### [](https://docs.io.net/docs/device-onboarding#readiness)
The **Readiness** column differs from **Status**. This value provides insights into your device's readiness for Block Reward eligibility. The screenshot below shows the Readiness column in the **Device Status** table. 
![](https://files.readme.io/b0d050b6694204211bcdf31071da304b04c1f41a3b307d70dd410bcf0d48d788-Readiness.png)
If the status is **Cluster Ready,** then your device is eligible to be hired and/or for a Block Reward. The four possible Readiness statuses are: 
Status 
Description 
Cluster Ready
Device meets PoW requirements and passed several Cluster Formation verifications. 
Hired 
Device is currently hired by a cluster. 
Pending 
The device has joined the network and is currently undergoing both the PoW and Cluster Readiness test. This process can take up to 12 hours of cumulative uptime after onboarding, but may complete sooner if your device passes our tests early. If your device remains in a Pending state after more than 12 hours of uptime, please contact us. 
Not Block Reward Ready
Device doesn't meet the criteria for block reward eligibility, mainly Cluster Formation verifications. 
**Not Block Reward Ready** offers one of three tooltips in the UI to provide troubleshooting tips. 
  * **Please check your device's computational capacity** - Your device's computational capacity is below the required threshold.
  * **Please check your device setup and computational capacity** - Your device setup might not be configured correctly and its computational capacity is below the required threshold. Please refer to the worker setup guide.
  * **Please check your device setup** - Your device setup might not be configured correctly. Please refer to the worker setup guide.


#### [](https://docs.io.net/docs/device-onboarding#transition-between-states)
The transition from **Pending** to **Cluster Ready** state can take up to 12 hours. During this time, we form clusters with newly joined devices (Pending) and verify them as **Cluster Ready** once they successfully pass the cluster formation process. 
If the device fails to join the cluster multiple times, it's labeled as **Not Block Reward Ready**. To verify if a device has successfully passed cluster formation is to check its job page, which indicates the record of past cluster formations. 
### [](https://docs.io.net/docs/device-onboarding#troubleshoot)
  1. Verify that the device is operated using io.net official binaries and official docker images.
  2. Verify that the device has the right network setup (beyond basic internet speed test capability) where the device can properly interact with the remote head node or peer workers.


19 days ago
* * *
What’s Next
  * [Device Utilization Threshold](https://docs.io.net/docs/device-utilization-threshold)
  * [Optimize PCIe Lane Configuration](https://docs.io.net/docs/optimize-pcie-lane-configuration)
  * [Supported Devices](https://docs.io.net/docs/supported-devices)
  * [Proof of Work](https://docs.io.net/docs/proof-of-work)


  * [](https://docs.io.net/docs/device-onboarding)
  *     *       * [Table of Contents](https://docs.io.net/docs/device-onboarding#table-of-contents)
      * [Create Account](https://docs.io.net/docs/device-onboarding#create-account)
      * [Requirements](https://docs.io.net/docs/device-onboarding#requirements)
      * [Set Up a New Worker](https://docs.io.net/docs/device-onboarding#set-up-a-new-worker)
    * [App Guide](https://docs.io.net/docs/device-onboarding#app-guide)
      * [Workers Homepage](https://docs.io.net/docs/device-onboarding#workers-homepage)
      * [Device Status](https://docs.io.net/docs/device-onboarding#device-status)
      * [Readiness](https://docs.io.net/docs/device-onboarding#readiness)
      * [Troubleshoot](https://docs.io.net/docs/device-onboarding#troubleshoot)



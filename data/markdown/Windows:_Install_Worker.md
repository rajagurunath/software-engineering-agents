# Windows: Install Worker
A step-by-step guide for setting up the environment for io.net on Windows-based machines.
### [](https://docs.io.net/docs/install-on-windows#go-to)
[cloud.io.net](https://cloud.io.net)
If you have not yet created an account, Creating an account on io.net is currently available only through X (Twitter), Apple ID or Google. Simply click on the "Sign Up" button and select either X, Apple ID, Worldcoin or Google to proceed with account creation
![](https://files.readme.io/ad230e1344d7b2815045e36b565055d9b76b3bc9be3971c8dfe55a1aeec51a18-Step1.jpg)
### [](https://docs.io.net/docs/install-on-windows#1-from-io-elements-go-to-io-worker)
IO Elements serves as your new control panel for navigating the service efficiently. Click on **IO Worker** to delve deeper into its functionalities and features.
![](https://files.readme.io/352f11e1cce13ad3a66154afddaff6e05886432951baefe131f88956107404b9-Step2.jpg)
### [](https://docs.io.net/docs/install-on-windows#2-click-connect-new-worker-to-open-the-wizard)
If Workers have not been added, click Connect New Worker. If the screen is full of information, find the same button in the upper right corner.
![](https://files.readme.io/d45c3842aeb35ce8e794d4587595775820edc84b5f64377d2b506b6dc3d35ec2-Step3.jpg)
### [](https://docs.io.net/docs/install-on-windows#3-name-your-device)
Click the "**Pencil** " icon to open the popup for editing the device name. 
Please add a unique name for your device. We suggest a format such as: **My-Test-Device**.
![](https://files.readme.io/fa15e9bcea705360a6f26c50fb9e7d9c5b6f4a4b59014312407edfe16df677b1-Step4.jpg)
### [](https://docs.io.net/docs/install-on-windows#4-select-windows-operating-system)
Choose the Operating System of your device from MacOS, **Windows** or Ubuntu.
![](https://files.readme.io/dfc41c05dde812a2168b7ca61a35139b9900598b94a8e95ade990910ac420a71-Step5.jpg)
### [](https://docs.io.net/docs/install-on-windows#5-select-device-type)
You should choose the device type based on your task. A video card is better suited for AI tasks, while a processor is more suitable for graphic rendering.
GPU - This is the part of your computer or laptop that handles graphics - the video card. It's usually from Nvidea or Radeon. You can find a full list of video cards that io.net is compatible with [here](https://docs.io.net/docs/supported-devices).
CPU - This forms the core of every smart device in our world, including your computer or laptop. Now, alongside Intel and AMD processors, Apple's processors have also joined the lineup. You can find a comprehensive list of processors compatible with io.net [here](https://docs.io.net/docs/supported-devices).
![](https://files.readme.io/5f74617cc09868a7db5d77f3eff61fa1ebf646d81a3470feebc6b8be0d96aff3-Step6.jpg)
You can also verify whether your GPU or CPU is included in the list of devices supported by our service on the wizard page.
> ## 🚧
> If you choose GPU Worker and your device doesn't have GPU the setup will fail
### [](https://docs.io.net/docs/install-on-windows#6-prerequisites-for-windows)
Follow the steps below to complete the prerequisites:
![](https://files.readme.io/a3ae8239f7c4796ac196d0dce63d1c92a3c0a1105911602b4d492a3d17825902-Step7.jpg)
  1. Download and Install Desktop Docker. You can find comprehensive instructions on how to install Docker for Windows in this [concise guide](https://docs.io.net/docs/install-docker-on-windows).
  2. Then Download and Setup CUDA. Please refer to the instructions on how to do this by [following the link](https://docs.io.net/docs/cuda-toolkit-optional).
  3. Afterward (if needed or if not done yet), you'll need to install or update the correct NVIDIA driver for your video card. You can find instructions on how to do this [here](https://docs.io.net/docs/install-nvidia-drivers-on-windows) .


> ## 🚧
> When using SXM or NV Link, ensure that Fabric Manager is [installed correctly](https://community.cisco.com/t5/data-center-and-cloud-knowledge-base/installing-cisco-fabric-manager-on-windows/tac-p/3114583/highlight/true) and enabled. This will prevent initialization issues and ensure that all GPUs are functioning properly, thereby avoiding PoW verification failures.
### [](https://docs.io.net/docs/install-on-windows#7-download-and-launch-io-binary)
**IO Binary** is a compiled executable file used to perform computational tasks and manage system operations. It is crucial for the operation of the platform as it handles essential functions directly related to the performance and reliability of computational resources.
> ## 🚧
> Do not modify or run code directly in io.net’s docker containers. This may disqualify your device from earning block rewards or being hired. If you have suggestions or ideas for custom code in our Docker containers, contact customer support to suggest them.
In this step, what you are required to do is:
  1. **Download the Executable File:** Copy the URL below, open your browser, and paste it. The browser downloads the executable file to your computer.**It's recommended to download the IO Binary again, as we often update versions for improvements.**
```
https://github.com/ionet-official/io_launch_binaries/raw/main/io_net_launch_binary_windows.exe

```
![](https://files.readme.io/8ec2f399bdd07703560dd2e9af8d1f79e33336427f32b14d376cb9f068b3f1b5-Step8.jpg)
  2. **Open IO Binary file into Terminal**
**Terminal** is a tool on your computer that allows you enter commands to tell the computer what to do. Instead of clicking on elements with a mouse, you write instructions, and the computer follows them. It's like talking directly to your computer using text.
     * Click the **Start Menu** icon, then find and select the **Terminal** app from the popup menu.
![](https://files.readme.io/90b9d15b93b4e634149cdf0c17d1590945ae783e3cd52b299769aeaa1683adb2-Step9.jpg)
     * In the **Terminal** , navigate to the **Downloads** folder by typing the command to go to the folder with the IO Binary.
```
cd Downloads

```

     * Next, copy the command from your new worker page to launch the IO Binary. 
![](https://files.readme.io/607900a8c3e3be42bcc8c6eadc56f2e5906c7f79ee262a8e4df0093d54b3ff4c-Step10.jpg)
Then paste it into the terminal and press Enter to run it. 
![](https://files.readme.io/112d137028f2efef3352c7c24b2c59a750940be79844e64844ea1bde01bc05be-step11.jpg)


### [](https://docs.io.net/docs/install-on-windows#8-authorize-your-new-device)
The IO Binary may prompt you to authorize your new device. 
> ## 📘
> Remember, you have about 3 minutes to complete the authorization of the device. If you miss it, you will need to rerun the code again.
You can do this in two ways:
  1. **Copy the Link from the Terminal** : 
![](https://files.readme.io/c8e7343e60c283b2a83d039ef5776c69fa87af7e11e863c1a0d0d0325d0f4eca-Step12.jpg)
Paste it into your browser and confirm the action. After confirmation, the system will prompt you to log in.
![](https://files.readme.io/84d7a619ac5837ec14900fc4de5ed80491a51e4446ae037a7dd229c4a0ef4272-Step13.jpg)
  2. **Copy the Code from the Terminal** : 
![](https://files.readme.io/bb881b52d9ca492049252563d3475ae89f33c98fef96c7be76ed398f4839c1cd-Step14.jpg)
Enter this code on the page <https://auth0.io.solutions/activate> to authorize the device. After it, the system will prompt you to log in.
![](https://files.readme.io/2b4f433ca39a47e3bd4d4c406bc14d409e18a3411f7a71628a70fa490cd6092c-Step15.jpg)


> ## 📘
> Onboard Multiple Devices by Bypassing Interactive Authentication
> After you authenticate once, you can bypass the interactive auth process when you join additional devices.  
>  To do this, run the binary with an additional argument, the **--token** flag, followed by the token value.
> In the Command Prompt, copy your token and pass the --token flag, followed by the token and run the binary. 
> ![](https://files.readme.io/f27905002262427fa20ed58a2d231cc05fa38a7ac32f9070f978ab65074f6f7c-Step16.png)```
io_net_launch_binary_windows.exe --token your-token-value

```

> Tokens are valid for 12 months.
### [](https://docs.io.net/docs/install-on-windows#9-remove-previously-installed-docker-containers)
IO Binary will ask you questions related to previously installed Docker Containers. To continue the installation of IO Worker, you must agree to remove all old containers and proceed by typing: **Yes**
![](https://files.readme.io/459922475413ce8dd94f0ea72a89b82750570e9733344ad852b080b051ba88e2-Step17.jpg)
### [](https://docs.io.net/docs/install-on-windows#11-wait-for-worker-connection-to-complete)
The IO Binary will installs all additional containers and images for your Docker. The process may take some time to complete as it installs additional packages for Docker. Please allow the installation process to finish.
![](https://files.readme.io/1e0a17be57515e028528b84c5e4544fc49e6b418eef7c008f43aa7965d42aa52-Step18.jpg)
Afterward, return to the browser to complete the installation.
You may need to wait for up to 10 minutes while the device checks and connects to the IO Ecosystem. If it doesn't connect, reach out to our Support ticket by logging into your [IO.Net account](https://worker.io.net).
![](https://files.readme.io/7059edf-Step13.gif)
> ## 🚧
> Please disable power-saving mode when running your devices on IO Net. Power-saving mode can impair device performance, potentially leading to failure in PoW or being classified as not providing adequate computing power.
### [](https://docs.io.net/docs/install-on-windows#congratulations-on-successfully-setting-up-your-first-worker)
Now that your Worker has been successfully created and is running, you can track its status on the Workers page.
![](https://files.readme.io/34c24b5076da68796d7e8d65b4a658f50e02358e4910e7685293210f954a5010-step-20.png)   

> ## 📘
> If you're having trouble installing the Worker, please refer to our [Windows Worker troubleshooting guide](https://docs.io.net/docs/troubleshoot-windows-worker) or the [general Worker troubleshooting guide](https://docs.io.net/docs/troubleshoot-worker). If the issue persists or you need further assistance, feel free to [check our knowledge base](https://support.io.net/en/support/home) for answers, and if you still need help, don’t hesitate to open a support ticket!
> ## 🚧
> Be aware that you will be installing a 20GB size container. This contains all the packages needed to serve AI/ML apps. Everything happens inside the container, nothing within the container can access your filesystem.
8 months ago
* * *
What’s Next
  * [Windows: Install Docker](https://docs.io.net/docs/install-docker-on-windows)
  * [CUDA Toolkit (Optional)](https://docs.io.net/docs/cuda-toolkit-optional)
  * [Install Nvidia Drivers](https://docs.io.net/docs/install-nvidia-drivers-on-windows)
  * [Troubleshoot Docker (Linux & Windows)](https://docs.io.net/docs/troubleshoot-docker)
  * [Monitor & Manage Workers](https://docs.io.net/docs/monitor-manage-workers)
  * [Windows: Troubleshoot Worker](https://docs.io.net/docs/troubleshoot-windows-worker)


  * [](https://docs.io.net/docs/install-on-windows)
  *     * [Go to](https://docs.io.net/docs/install-on-windows#go-to)
    * [1. From IO Elements Go to IO Worker](https://docs.io.net/docs/install-on-windows#1-from-io-elements-go-to-io-worker)
    * [2. Click "Connect New Worker" to Open the Wizard](https://docs.io.net/docs/install-on-windows#2-click-connect-new-worker-to-open-the-wizard)
    * [3. Name Your Device](https://docs.io.net/docs/install-on-windows#3-name-your-device)
    * [4. Select Windows Operating System](https://docs.io.net/docs/install-on-windows#4-select-windows-operating-system)
    * [5. Select Device Type](https://docs.io.net/docs/install-on-windows#5-select-device-type)
    * [6. Prerequisites for Windows](https://docs.io.net/docs/install-on-windows#6-prerequisites-for-windows)
    * [7. Download and Launch IO Binary](https://docs.io.net/docs/install-on-windows#7-download-and-launch-io-binary)
    * [8. Authorize Your New Device](https://docs.io.net/docs/install-on-windows#8-authorize-your-new-device)
    * [9. Remove Previously Installed Docker Containers](https://docs.io.net/docs/install-on-windows#9-remove-previously-installed-docker-containers)
    * [11. Wait for Worker Connection to Complete](https://docs.io.net/docs/install-on-windows#11-wait-for-worker-connection-to-complete)
    * [Congratulations on Successfully Setting up Your First Worker.](https://docs.io.net/docs/install-on-windows#congratulations-on-successfully-setting-up-your-first-worker)



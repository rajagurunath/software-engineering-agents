# Windows: Install Docker
A step-by-step guide for installing Docker on Windows-based machines
### [](https://docs.io.net/docs/install-docker-on-windows#what-is-docker)
Let's take a quick look at what **Docker** is? Imagine Docker as a magic box where you put your software and everything it needs to run. This box can be easily carried to any computer, and when you open it, your software works just the way you packed it, without needing anything extra from that computer. Here are a few steps to install Docker:
> ## ❗️
> Network Capability Issue on Docker Desktop for Windows
> We are currently investigating a network performance issue with Docker Desktop on Windows. This might be due to Docker's overhead, and we are exploring potential fixes.
> **Recommendation** :  
>  If you experience this issue, we recommend switching to Linux as a temporary workaround.
> Thank you for your understanding and patience.
### [](https://docs.io.net/docs/install-docker-on-windows#first-verify-that-virtualization-is-enabled-on-your-computer)
To verify if virtualization is enabled, open **Task Manager** by pressing Ctrl+Alt+Del. Select "**Performance** " and then click on the "**CPU** " tab to view the information in the bottom right corner, as shown in the image below:
![](https://files.readme.io/def0a77ce8b421fc05925437a64177eee107962c5b36a64bbd4872068c98e334-Step1.jpg)
> ## 🚧
> If it's not enabled, follow these steps:
  1. To enable virtualization technology in your BIOS or UEFI settings, you need to access your computer's BIOS or UEFI configuration menu during the boot process. The specific steps can vary depending on your computer's manufacturer and model, but here are the general steps to enable virtualization.
  2. Install WSL 2 by opening the PowerShell as an Administrator. To do this, search for "PowerShell" in the Start menu, right-click on "Windows PowerShell," and select "Run as administrator."
  3. Run the following command to enable the WSL feature in **Windows 10/11** in Terminal: 
Terminal Command
```
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

```

  4. Then **Enable** the Virtual Machine Platform Feature while still in the same PowerShell window by running the following command: 
Terminal Command
```
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

```

  5. Then set WSL 2 as the Default Version (you might be required to restart your machine sometimes): 
Terminal Command
```
wsl --set-default-version 2

```



### [](https://docs.io.net/docs/install-docker-on-windows#1-download-docker)
Go to the [Docker website](https://www.docker.com/products/docker-desktop/) and click on "**Download for Windows**." Downloading the Docker file may take some time. Please be patient.
![](https://files.readme.io/95a4cbd4f0ddf46a9d3ba867b4ca911ed1c7cd2851927842a9fed04a117aabd2-Step2.jpg)   

### [](https://docs.io.net/docs/install-docker-on-windows#2-run-the-installation-process)
The installation starts when you open the file. Follow the prompts. When the installation process is completed, you need to **restart your computer.** Just click the "**Close and Restart** " button on the last step of the Docker wizard:
![](https://files.readme.io/e5eebdef187efd9de0b73eb2b2acc408d5c530c1bf8c197e3c484c0d8a1328fb-Step3.jpg)
After rebooting, open Docker and use the recommended settings from the installation wizard:
![](https://files.readme.io/32e6c86ea6a2eaf00a84d4320612a2567b1e9e50fcf5dfc575d5e9bb137cff52-Step4.jpg)
### [](https://docs.io.net/docs/install-docker-on-windows#3-configure-wsl2-to-integrate-with-docker-settings)
Open the Docker settings. In the Resources section, choose WSL 2 Integration and check the box for WSL 2 to integrate.
![](https://files.readme.io/9acbba90f47ce6f03d814f729865c5267d2d970267770e3a0ca750d623ad0943-Step5.jpg)
### [](https://docs.io.net/docs/install-docker-on-windows#4-openterminal-through-start-menu)
Click the Start Menu icon in the Popup Menu, type Terminal in the search field, then click Terminal
![](https://files.readme.io/a16c898ed54cc7b42064f07705a1fe247e042b6889129d914721c51157b1f891-Step6.jpg)
### [](https://docs.io.net/docs/install-docker-on-windows#5-verify-the-installation-in-terminal)
![](https://files.readme.io/c61ab3eb3a5d3772de6250efa527f9037f5d64a14e5808442de346b6a797baa1-Step7.jpg)
Copy and paste the following line into Terminal. 
Terminal Command
```
docker --version

```

The result will be the current version of Docker.
```
Docker version 24.0.6, build ed223bc

```

### [](https://docs.io.net/docs/install-docker-on-windows#congratulations-on-successfully-setting-up-docker)
Now that Docker has been successfully installed and is running, you can proceed with [setting up the Worker](https://docs.io.net/docs/install-on-windows).
  

> ## 📘
> If you encounter issues with Docker, please refer to our [Troubleshooting Docker guide](https://docs.io.net/docs/troubleshoot-docker). If the problem persists or if you need further assistance, feel free to [check our knowledge base](https://support.io.net/en/support/home) for answers, and if you still need help, don’t hesitate to open a support ticket!
8 months ago
* * *
What’s Next
  * [Windows: Install Worker](https://docs.io.net/docs/install-on-windows)
  * [Troubleshoot Docker for Windows](https://docs.io.net/docs/troubleshoot-docker-for-windows)
  * [Supported Devices](https://docs.io.net/docs/supported-devices)


  * [](https://docs.io.net/docs/install-docker-on-windows)
  *     * [What is Docker?](https://docs.io.net/docs/install-docker-on-windows#what-is-docker)
    * [First, verify that Virtualization is Enabled on your Computer.](https://docs.io.net/docs/install-docker-on-windows#first-verify-that-virtualization-is-enabled-on-your-computer)
    * [1. Download Docker](https://docs.io.net/docs/install-docker-on-windows#1-download-docker)
    * [2. Run the Installation Process](https://docs.io.net/docs/install-docker-on-windows#2-run-the-installation-process)
    * [3. Configure WSL2 to Integrate with Docker Settings](https://docs.io.net/docs/install-docker-on-windows#3-configure-wsl2-to-integrate-with-docker-settings)
    * [4. Open Terminal Through Start Menu](https://docs.io.net/docs/install-docker-on-windows#4-openterminal-through-start-menu)
    * [5. Verify the Installation in Terminal](https://docs.io.net/docs/install-docker-on-windows#5-verify-the-installation-in-terminal)
    * [Congratulations on Successfully Setting up Docker](https://docs.io.net/docs/install-docker-on-windows#congratulations-on-successfully-setting-up-docker)



# MacOS: Install Docker
A step-by-step guide for installing Docker on MacOS-based machines.
### [](https://docs.io.net/docs/install-docker-on-macos#what-is-docker)
Let's take a quick look at what Docker is? Imagine Docker as a magic box where you put your software and everything it needs to run. This box can be easily carried to any computer, and when you open it, your software works just the way you packed it, without needing anything extra from that computer. Here are a few steps to install Docker:
### [](https://docs.io.net/docs/install-docker-on-macos#1-download-docker)
Go to the [Docker website](https://www.docker.com/products/docker-desktop/) and click on "**Download for Mac - Apple Chip.** "
Downloading the Docker file may take some time. Please be patient.
![](https://files.readme.io/0ffabf70a17c1d2ecd014da5fb1aa694df810f39530f6ede923eb2032f11c294-Step1.jpg)
### [](https://docs.io.net/docs/install-docker-on-macos#2-open-the-dockerdmg-file-and-drag-it-into-the-applications-folder)
![](https://files.readme.io/6cde349-Step2.jpg)
### [](https://docs.io.net/docs/install-docker-on-macos#3-start-the-docker-installation-from-the-applications-folder)
We recommend using the recommended settings during the installation wizard.
![](https://files.readme.io/4eda55c186520c2223b78563edbbb047033d956cd780f898bb143b0d34b34e4c-Step3.jpg)
### [](https://docs.io.net/docs/install-docker-on-macos#4-open-terminal-through-launchpad)
Click the Launchpad icon in the Dock, type Terminal in the search field, then click Terminal
![](https://files.readme.io/7acc67f5656643749054e5dd9f6a39772cf8f7348f903cbbb925d83cc0f28c3b-Step4.jpg)
### [](https://docs.io.net/docs/install-docker-on-macos#5-verify-the-installation-in-terminal)
![](https://files.readme.io/e901826dcc950343214ce2a5f06d6e6bc757b49adcfc715a8f143ddf8eb29ebc-Step5mac.jpeg)
Copy and paste the following line into Terminal. 
Terminal Command
```
docker --version

```

The result will be the current version of Docker.
```
Docker version 24.0.6, build ed223bc

```

### [](https://docs.io.net/docs/install-docker-on-macos#expanding-virtual-disk-limit)
  1. Click **Settings**.
  2. Go to **Resources** on the left nav.
![](https://files.readme.io/09b563bbd55cf92dc1979014994315fd6c16510df311303f8e2eb10436ed98d0-IO_docker_resources_left_nav.png)
  3. Check the amount of space shown under **Virtual disk limit**.  
**Note:** Docker does not natively assign all of your disk space. 
![](https://files.readme.io/ff1f4b08df586b67e267c8cd17be9b7f6638f4485495b4885a8b08f808a788a4-IO_virtual_disk_limit_macos.png)
  4. Drag the slider to your desired virtual disk limit amount.
  5. Click **Apply & restart**.


### [](https://docs.io.net/docs/install-docker-on-macos#congratulations-on-successfully-setting-up-docker)
Now that Docker has been successfully installed and is running, you can proceed with [setting up the Worker](https://docs.io.net/docs/install-on-macos).
  

> ## 📘
> Feel free to [check our knowledge base](https://support.io.net/en/support/home) for answers, and if you still need help, don’t hesitate to open a support ticket!
7 months ago
* * *
What’s Next
  * [MacOS: Install Worker](https://docs.io.net/docs/install-on-macos)
  * [Proof of Compute](https://docs.io.net/docs/prof-of-compute)


  * [](https://docs.io.net/docs/install-docker-on-macos)
  *     * [What is Docker?](https://docs.io.net/docs/install-docker-on-macos#what-is-docker)
    * [1. Download Docker](https://docs.io.net/docs/install-docker-on-macos#1-download-docker)
    * [2. Open the docker.dmg File and Drag It Into the Applications Folder](https://docs.io.net/docs/install-docker-on-macos#2-open-the-dockerdmg-file-and-drag-it-into-the-applications-folder)
    * [3. Start the Docker Installation From the Applications Folder](https://docs.io.net/docs/install-docker-on-macos#3-start-the-docker-installation-from-the-applications-folder)
    * [4. Open Terminal Through Launchpad](https://docs.io.net/docs/install-docker-on-macos#4-open-terminal-through-launchpad)
    * [5. Verify the Installation in Terminal](https://docs.io.net/docs/install-docker-on-macos#5-verify-the-installation-in-terminal)
    * [Expanding Virtual Disk Limit](https://docs.io.net/docs/install-docker-on-macos#expanding-virtual-disk-limit)
    * [Congratulations on Successfully Setting up Docker](https://docs.io.net/docs/install-docker-on-macos#congratulations-on-successfully-setting-up-docker)



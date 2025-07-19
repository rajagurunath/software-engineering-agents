# Windows: Troubleshoot Docker
### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#windows-uptime)
Follow the instructions below if you experience inconsistent uptime on Windows.
> ## 📘
> To ensure that the DHCP lease time on the router is set to a duration exceeding 24 hours, access the group policy editor within the Windows operating system. Proceed by enabling the specified settings in the following sequence:
  1. Open the group policy editor and go to **Computer Configuration**.
  2. In Computer Configuration, find the **Administrative Templates** section.
  3. Under **Administrative Templates** , go to **System**.
  4. In the **System** menu, choose **Power Management**.
  5. Access the **Sleep Settings** subsection within **Power Management**.
  6. Activate both **Allow network connectivity during connected-standby (on battery)** and **Allow network connectivity during connected-standby (plugged in)** options.


Adjust the settings above to meet your requirements.
### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#fixing-the-docker-desktop---unexpected-wsl-error-in-windows)
This error occurs when you haven't updated to the latest version of WSL or haven't enabled the Hyper-V feature. Follow these steps:
![](https://files.readme.io/63989d6-UseCases-DockerWSL.jpg)
  1. **Check and Update WSL Version** : First, ensure that you’re running the latest version of WSL. You can check your current WSL version by opening a command prompt and typing:
```
wsl --version

```

If you find that you’re not on WSL 2, you can set the default version to 2 by executing:
```
wsl --set-default-version 2

```

  2. **Enable Hyper-V Feature** : Hyper-V is a virtualization technology tool that needs to be enabled in Windows. To check if Hyper-V is enabled, you can use the Windows Features dialog via Search:
![](https://files.readme.io/95eca0ec814f73628c619d3f020cd61e9c52e6ad5ac9b004caf5a8d4d2e4d3b0-UseCases-DockerWSL-2.jpg)
In the **Windows Features** dialog, scroll down and check **Windows Hypervisor Platform** , then click OK.:
![](https://files.readme.io/0346c11c13e1b8ddd972467c09f4a81bb31bb9a5ab1383baef3c92aa726203cf-UseCases-DockerWSL-3.jpg)
After installing **Windows Hypervisor Platform** , the problem should disappear.


### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#stop-the-docker-with-all-containers-and-images)
Run the command below in Terminal to stop the platform and remove all containers for Windows.
Terminal Command
```
# Stop all running containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -aq)

```

### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#restart-the-platform)
  * Reboot your computer or server.
  * After the device reboots, restart the platform by entering this command into the Terminal: ```
./io_net_launch_binary_windows.exe 

```



### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#additional-guides)
#### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#ports)
Expose the ports below to ensure platform stability for Windows:
  * TCP: 443, 25061, 5432, 80
  * UDP: 80, 443, 41641, 3478


Ensure that these ports are open and accessible to enable smooth operation of the platform.
#### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#how-can-i-verify-that-program-has-started-successfully)
  * When running the following command on Terminal, **you should always have 2 Docker containers running** : 
Terminal Command
```
 docker ps

```

  * If there are no containers or only one container running after running the docker run**-d ... command** from the website: 
    * Stop the platform using the command provided in the guide above.
    * Restart the platform using the command from the website again.


### [](https://docs.io.net/docs/troubleshoot-docker-for-windows#waiting-for-io-containers-to-start)
Ensure the "**Use containerd for storing and pulling images** " option is **disabled** in Docker's General Settings.
![](https://files.readme.io/790b54eb86adbf616cd0b0bfb8e30bad3899827e4b56a043bc3711322b96ebcc-DockerIssue1.5.jpg)
Containerd may interfere with Docker’s default image management, **so it’s recommended to turn it off**.
## [](https://docs.io.net/docs/troubleshoot-docker-for-windows#worker-disconnecting-despite-containers-running)
If your Worker disconnects even when the containers are up, try the following checks:
  1. Ensure resources aren't limited. Make sure Docker's "**Resource Saver** " feature is **disabled** in the **Resources tab** of **Docker Settings**.
![](https://files.readme.io/ec67447f68fd986bf9eb405aa9aa03bb07ee65eaf0f95bd5e88f00cb450af13f-DockerIssue5.5.jpg)
  2. Check Docker Resource Allocation. Ensure Docker is allocated the minimum required **CPU** , **RAM** , and **disk space**. System requirements are as follows:
     * **Memory** : At least 512MB of free RAM (2GB is recommended)
     * **Disk** : Adequate storage to run the Docker containers you intend to use
     * **CPU/GPU** : You can check the currently supported [CPUs/GPUs](https://docs.io.net/docs/supported-devices).
  3. Verify Power Supply to GPU(s). Ensure the GPU(s) are receiving adequate power for stable operation.


## [](https://docs.io.net/docs/troubleshoot-docker-for-windows#connectivity-tier-not-displaying-correctly)
To troubleshoot connectivity tier issues, users can test network speeds via a sample Docker container. Here's how:
  1. Pull the Python 3.9 Slim container: ```
docker pull python:3.9-slim

```

  2. Run the container: ```
docker run -it --name speedtest-container python:3.9-slim /bin/bash

```

  3. Install the speedtest tool: ```
pip install speedtest-cli

```

  4. Test the network speed: ```
speedtest-cli

```


![](https://files.readme.io/4f78a04e7dcac9a77ef208709f38bb2e8821bb81dce7cd1921b08fada7e100e6-DockerIssue6.1.jpg)
We recommend running similar speed tests periodically within your containers to monitor connectivity performance. You can also guide users on how to perform these tests at regular intervals or during specific instances for troubleshooting.
6 months ago
* * *
What’s Next
  * [Windows: Install Docker](https://docs.io.net/docs/install-docker-on-windows)


  * [](https://docs.io.net/docs/troubleshoot-docker-for-windows)
  *     *       * [Windows Uptime](https://docs.io.net/docs/troubleshoot-docker-for-windows#windows-uptime)
      * [Fixing the "Docker Desktop - Unexpected WSL error" in Windows](https://docs.io.net/docs/troubleshoot-docker-for-windows#fixing-the-docker-desktop---unexpected-wsl-error-in-windows)
      * [Stop the Docker with all Containers and Images](https://docs.io.net/docs/troubleshoot-docker-for-windows#stop-the-docker-with-all-containers-and-images)
      * [Restart the Platform](https://docs.io.net/docs/troubleshoot-docker-for-windows#restart-the-platform)
      * [Additional Guides](https://docs.io.net/docs/troubleshoot-docker-for-windows#additional-guides)
      * [Waiting for IO Containers to Start](https://docs.io.net/docs/troubleshoot-docker-for-windows#waiting-for-io-containers-to-start)
    * [Worker Disconnecting Despite Containers Running](https://docs.io.net/docs/troubleshoot-docker-for-windows#worker-disconnecting-despite-containers-running)
    * [Connectivity Tier Not Displaying Correctly](https://docs.io.net/docs/troubleshoot-docker-for-windows#connectivity-tier-not-displaying-correctly)



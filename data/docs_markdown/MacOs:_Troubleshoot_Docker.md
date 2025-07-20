# MacOs: Troubleshoot Docker
### [](https://docs.io.net/docs/troubleshoot-docker-for-macs#incompatible-cpu-detected-error)
To resolve this issue, ensure you download and install the appropriate Docker version. For macOS, Docker provides two options: "**Apple Chip** " and "**Intel Chip**." 
![](https://files.readme.io/d87445a-Step6.jpg)
First, you need to remove the previous version for the **Intel chip**. Click on the **Bug** icon to open Docker Settings, then click **Uninstall**.
![](https://files.readme.io/a268dc3fbe5ec21efbd083196849729543a8da4b5d05e4e7cfce469183cf06cb-Step8.jpg)
After that, visit the Docker website and download and install the version designed for the "**Apple Chip**." Downloading the Docker file may take some time, so please be patient..
![](https://files.readme.io/ed0ff6d93b2af567a5770329213d7d19abbf55718e2853b78be0cb61353f4712-Step1.jpg)
### [](https://docs.io.net/docs/troubleshoot-docker-for-macs#waiting-for-io-containers-to-start)
Ensure the "**Use containerd for storing and pulling images** " option is **disabled** in Docker's General Settings.
![](https://files.readme.io/5b05896a180bbf6c4b0c344f8c6a2ab29a7102cf5a3aa29bcabb956d99ae1789-DockerIssue1.jpg)
Containerd may interfere with Docker’s default image management, **so it’s recommended to turn it off**.
## [](https://docs.io.net/docs/troubleshoot-docker-for-macs#worker-disconnecting-despite-containers-running)
If your Worker disconnects even when the containers are up, try the following checks:
  1. Ensure resources aren't limited. Make sure Docker's "**Resource Saver** " feature is **disabled** in the **Resources tab** of **Docker Settings**.
![](https://files.readme.io/fca1d421123b295103d84f08b0214060405a6f1038f3a7f025185caeb7c8abab-DockerIssue5.jpg)
  2. Check Docker Resource Allocation. Ensure Docker is allocated the minimum required **CPU** , **RAM** , and **disk space**. System requirements are as follows:
     * **Memory** : At least 512MB of free RAM (2GB is recommended)
     * **Disk** : Adequate storage to run the Docker containers you intend to use
     * **GPU** : You can check the currently supported [GPUs](https://docs.io.net/docs/supported-devices).


## [](https://docs.io.net/docs/troubleshoot-docker-for-macs#connectivity-tier-not-displaying-correctly)
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


![](https://files.readme.io/37c7c1b2c41928a6d66458a8db5dadbf926f4e769866e45f089cdbfbcce87ec0-DockerIssue6.2.jpg)
We recommend running similar speed tests periodically within your containers to monitor connectivity performance. You can also guide users on how to perform these tests at regular intervals or during specific instances for troubleshooting.
6 months ago
* * *
What’s Next
  * [MacOS: Install Docker](https://docs.io.net/docs/install-docker-on-macos)


  * [](https://docs.io.net/docs/troubleshoot-docker-for-macs)
  *     *       * [Incompatible CPU detected Error](https://docs.io.net/docs/troubleshoot-docker-for-macs#incompatible-cpu-detected-error)
      * [Waiting for IO Containers to Start](https://docs.io.net/docs/troubleshoot-docker-for-macs#waiting-for-io-containers-to-start)
    * [Worker Disconnecting Despite Containers Running](https://docs.io.net/docs/troubleshoot-docker-for-macs#worker-disconnecting-despite-containers-running)
    * [Connectivity Tier Not Displaying Correctly](https://docs.io.net/docs/troubleshoot-docker-for-macs#connectivity-tier-not-displaying-correctly)



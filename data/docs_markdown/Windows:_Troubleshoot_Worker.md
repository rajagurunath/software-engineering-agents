# Windows: Troubleshoot Worker
Here we've compiled essential use cases for working with Workers.
### [](https://docs.io.net/docs/troubleshoot-windows-worker#how-to-resolve-unsupported-gpu-issues)
If a user's supported GPU is listed as unsupported on the website, they should verify their NVIDIA driver configuration. Often, when a Docker container running **nvidia-smi** fails, the backend receives this information and marks the GPU as unsupported.
To check the configuration, running the following command should provide the correct output:
```
docker run --gpus all nvidia/cuda:11.0.3-base-ubuntu18.04 nvidia-smi

```

### [](https://docs.io.net/docs/troubleshoot-windows-worker#regulate-ram-usage)
![](https://files.readme.io/18ae7a1-RamIssue.jpg)
Create a file called **.wslconfig** to restrict the resources used by **WSL2** (Windows Subsystem for Linux). Follow the steps below to create it:
  * **Open File Explorer** and navigate to your user's home directory (usually **C:\Users <Username>**). 
  * **Create a new text file** in your home directory and name it **.wslconfig**.
  * **Edit the .wslconfig File:** Right-click on the newly created **.wslconfig** file and open it with a text editor such as Notepad.
  * **Add the following configuration parameters** to limit memory (set values according to your preference):
```
[wsl2]  
memory=4GB # Limits the VM memory in WSL between 2 and 4 GB  
processors=2 # Limits the number of processors to 2  
swap=8GB # Sets the swap size to 8 GB

```

  * **Save the file and restart your computer**. If the worker does not connect automatically, you may [need to install it again](https://docs.io.net/docs/troubleshoot-worker#how-can-i-pause-or-reset-a-worker-if-it-has-disconnection-issues).


### [](https://docs.io.net/docs/troubleshoot-windows-worker#computer-time-synchronization-issue)
Make sure your computer's time is synchronized with the server. If it's not, the IO binary won't work properly. Click the **Start Menu** and open the **Settings** app.
![](https://files.readme.io/8ea9a4c3c0f092316eec2a18c72e10d22af5863b8583b032a6c22600d08c2384-win1.jpg)
Next, in the **Settings** app, go to **Time & Language** and select **Date & Time**. Then, under **Additional settings,** click the **Sync now** button to synchronize your computer's time with the server. 
![](https://files.readme.io/3c9dc71d5678cdf1e0cdfa4d7499f6b80c4c37af21365540c7ca1116643a87ac-win2.jpg)
### [](https://docs.io.net/docs/troubleshoot-windows-worker#common-issue-container-cpu-dropping-to-0)
A common issue that many users encounter is the CPU of the container dropping to 0.
This problem is often due to missing necessary software components. For instance, on Windows, you need to ensure [CUDA](https://docs.io.net/docs/cuda-toolkit-optional) and [WSL2](https://docs.io.net/docs/install-docker-on-windows#3-configure-wsl2-to-integrate-with-docker-settings) are installed. 
If you still encounter this issue after installing all the necessary software components, try deleting the containers and images, then **re-run** the worker command and wait. You may need to repeat this process 3 or 4 times until they function normally. If the issue persists after these steps, it may indicate a system-level error.
![](https://files.readme.io/76dd63ed4563198c02ef6d3a7c1fb01de5776790ab965a9437a56ab13604bf0a-UseCases-NoContainersCPU0_Copy.jpg)   

> ## 📘
> For general questions about the Worker, no matter the operating system, check [here](https://docs.io.net/docs/troubleshoot-worker)
  

> ## 📘
> Feel free to [check our knowledge base](https://support.io.net/en/support/home) for answers, and if you still need help, don’t hesitate to open a support ticket!
8 months ago
* * *
What’s Next
  * [Windows: Install Worker](https://docs.io.net/docs/install-on-windows)
  * [Troubleshoot Worker](https://docs.io.net/docs/troubleshoot-worker)


  * [](https://docs.io.net/docs/troubleshoot-windows-worker)
  *     * [How to Resolve Unsupported GPU Issues?](https://docs.io.net/docs/troubleshoot-windows-worker#how-to-resolve-unsupported-gpu-issues)
    * [Regulate RAM Usage](https://docs.io.net/docs/troubleshoot-windows-worker#regulate-ram-usage)
    * [Computer Time Synchronization Issue](https://docs.io.net/docs/troubleshoot-windows-worker#computer-time-synchronization-issue)
    * [Common Issue: Container CPU Dropping to 0](https://docs.io.net/docs/troubleshoot-windows-worker#common-issue-container-cpu-dropping-to-0)



# CUDA Toolkit
A step by step process for Downloading the CUDA Toolkit.
### [](https://docs.io.net/docs/cuda-toolkit-optional#what-is-cuda)
The CUDA Toolkit is like a toolbox for programmers who want to make their software run faster using NVIDIA graphics cards. It has everything they need, like tools and instructions, to write code that takes advantage of the graphics card's power for tasks like math calculations, simulations, and artificial intelligence. Here are a few steps to install the CUDA Toolkit:
### 
[NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) Download Page
[](https://docs.io.net/docs/cuda-toolkit-optional#1-go-to-nvidia-cuda-toolkit-download-page)
Choose either the Windows or Linux operating system to access additional settings.
![](https://files.readme.io/5a12d3e-Step1.jpg)
### [](https://docs.io.net/docs/cuda-toolkit-optional#2-provide-additional-information)
For Windows, you need to choose your architecture, which is usually x86_64 for 64-bit systems.
![](https://files.readme.io/c0d3322-Step2.jpg)
### [](https://docs.io.net/docs/cuda-toolkit-optional#3-download-the-recommended-cuda-executable-file)
Downloading the Local Installer file may take some time. Please be patient. After downloading the file, run the installer.
![](https://files.readme.io/259f0b0-Step3.jpg)
### [](https://docs.io.net/docs/cuda-toolkit-optional#4-open-the-exe-file-and-proceed-with-the-installation-process)
It includes steps such as agreeing to the terms and selecting installation options.
![](https://files.readme.io/07fbac5-Step4.jpg)
### [](https://docs.io.net/docs/cuda-toolkit-optional#5-fixing-cuda-toolkit-installation-errors)
Installation errors while installing CUDA Toolkit are common issues encountered by many users. 
![](https://files.readme.io/ca50287-Step5-1.jpg)
Follow these steps to resolve the error:
  1. When reinstalling the CUDA Toolkit, opt for **Custom (Advanced)** installation.
![](https://files.readme.io/00b5f31-Step5-2.jpg)
  2. After selecting the custom installation option, expand the **CUDA** section and uncheck the option for **Nsight Compute** to exclude it from the installation. This step ensures that only the necessary components are installed, reducing the likelihood of errors.
![](https://files.readme.io/5aaf2c8-Step5-3.jpg)
  3. Proceed with the installation process.


### [](https://docs.io.net/docs/cuda-toolkit-optional#6-verify-the-installation-process)
![](https://files.readme.io/c86c1e9-Step9-2-2.jpeg)
After the installation, open Windows Terminal and enter the following command:
Terminal Command
```
nvcc --version

```

You should receive a similar response:
```
nvcc: NVIDIA (R) Cuda compiler driver  
Copyright (c) 2005-2022 NVIDIA Corporation  
Built on Wed_Sep_21_10:41:10_Pacific_Daylight_Time_2022  
Cuda compilation tools, release 11.8, V11.8.89  
Build cuda_11.8.r11.8/compiler.31833905_0

```

### [](https://docs.io.net/docs/cuda-toolkit-optional#thats-it-you-have-the-cuda-toolkit-installed-and-ready)
Now that CUDA Toolkit has been successfully installed and is running, you can proceed with [setting up the Worker](https://docs.io.net/docs/install-on-windows)
  

> ## 📘
> Feel free to [check our knowledge base](https://support.io.net/en/support/home) for answers, and if you still need help, don’t hesitate to open a support ticket!
about 1 year ago
* * *
What’s Next
  * [Windows: Install Worker](https://docs.io.net/docs/install-on-windows)
  * [Install Nvidia Drivers](https://docs.io.net/docs/install-nvidia-drivers-on-windows)


  * [](https://docs.io.net/docs/cuda-toolkit-optional)
  *     * [What is CUDA?](https://docs.io.net/docs/cuda-toolkit-optional#what-is-cuda)
    * [1. Go to NVIDIA CUDA Toolkit Download Page](https://docs.io.net/docs/cuda-toolkit-optional#1-go-to-nvidia-cuda-toolkit-download-page)
    * [2. Provide Additional Information](https://docs.io.net/docs/cuda-toolkit-optional#2-provide-additional-information)
    * [3. Download the Recommended Cuda Executable File](https://docs.io.net/docs/cuda-toolkit-optional#3-download-the-recommended-cuda-executable-file)
    * [4. Open the .exe File and Proceed With the Installation Process](https://docs.io.net/docs/cuda-toolkit-optional#4-open-the-exe-file-and-proceed-with-the-installation-process)
    * [5. Fixing CUDA Toolkit Installation Errors](https://docs.io.net/docs/cuda-toolkit-optional#5-fixing-cuda-toolkit-installation-errors)
    * [6. Verify the Installation Process](https://docs.io.net/docs/cuda-toolkit-optional#6-verify-the-installation-process)
    * [That’s It. You Have the Cuda Toolkit Installed and Ready](https://docs.io.net/docs/cuda-toolkit-optional#thats-it-you-have-the-cuda-toolkit-installed-and-ready)



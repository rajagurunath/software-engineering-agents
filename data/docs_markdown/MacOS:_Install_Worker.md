# MacOS: Install Worker
A step-by-step guide for setting up the environment for io.net on Mac OS-based machines
### [](https://docs.io.net/docs/install-on-macos#before-starting-check-your-mac-processor)
We currently only support **Apple chip** processors (M3, M4). All currently supported processor and video card models can be [found here](https://docs.io.net/docs/supported-devices).
To check your Mac processor:
  1. On your Mac, click the Apple icon in the top-left corner of the menu bar.
  2. Select the **About This Mac** option.
  3. If you see **Apple M3**(or higher) in the **Chip** line, it means you’re using a Mac with an Apple Silicon CPU. 

![](https://files.readme.io/1c29ed6d34b2f9bbc8ab80f43279d2872964c560f867a81530e82ee76c6519f3-Step0.jpg)
### 
[cloud.io.net](https://cloud.io.net)
[](https://docs.io.net/docs/install-on-macos#go-to-cloudionet)
If you have not yet created an account, Creating an account on io.net is currently available only through X (Twitter), Apple ID or Google. Simply click on the "Sign Up" button and select either X, Apple ID, Worldcoin or Google to proceed with account creation.
![](https://files.readme.io/de29df40f9a632af89c7cafd95f4acb332657550aca5bc1b3630225034a6453b-Step1.jpg)
### [](https://docs.io.net/docs/install-on-macos#1-from-io-elements-navigate-to-worker-section)
IO Elements serves as your new control panel for navigating the service efficiently. Click on **IO Worker** to delve deeper into its functionalities and features. 
![](https://files.readme.io/4ab2791afa1784c65f0b291076f9e8c0f91ca5e8f4fffe7fb922c26c352d19e2-Step2.jpg)
### [](https://docs.io.net/docs/install-on-macos#2-use-connect-new-worker-button-to-open-the-wizard)
If Workers have not yet been added, you can use the central button. If the screen is full of information, find the same button in the upper right corner
![](https://files.readme.io/5274db0357e3ae99cfc95b57f3f1aa9c2af8cc906d358b53eaf857dac33a7ce1-Step3.jpg)
### [](https://docs.io.net/docs/install-on-macos#3-name-your-device)
Click the "**Pencil** " icon to open the popup for editing the device name. 
Please add a unique name for your device.  
An ideal format would be something like this: **My-Test-Device**
![](https://files.readme.io/560a01163ca32f581e247537775cc0996388c39442b09a3ff49f97c836b263db-Step4.jpg)
### [](https://docs.io.net/docs/install-on-macos#4-select-macos-operating-system-os)
Choose the Operating System “OS” of your device from **MacOS** , Windows or Ubuntu.
![](https://files.readme.io/a757734d9ac6926db17891cada2e623939bb28c16ed646f75837aeeb4ba7cc08-Step5.jpg)
### [](https://docs.io.net/docs/install-on-macos#5-prerequisites-for-mac)
Download and install Docker Desktop for MacOS by [following the link](https://docs.io.net/docs/install-docker-on-macos).
> ## 📘
> It has been confirmed that some users limit the amount of system resources that IO Worker can access when performing compute verifications. Many users do not set the proper amount of device level resources available for the Docker engine. Many have used default settings or restricted the Worker’s RAM access to 8GB or lower. This would significantly impact the device capability in passing PoW. This is mostly common among Mac devices.
> ## 👍
> To install Docker on MacOS computers, refer to the "[Installing Docker on MacOS](https://docs.io.net/docs/install-docker-on-macos)" instructions.
### [](https://docs.io.net/docs/install-on-macos#6-download-and-launch-io-binary)
**IO Binary** is a compiled executable file used to perform computational tasks and manage system operations. It is crucial for the smooth operation of the platform as it handles essential functions directly related to the performance and reliability of the computational resources.
> ## 🚧
> Do not modify or run code directly in io.net’s docker containers. This may disqualify your device from earning block rewards or being hired. If you have suggestions or ideas for custom code in our Docker containers, contact customer support to suggest them.
Follow the steps below to download and launch the IO binary:
  1. Open the Terminal through **Launchpad**
**Terminal** is a tool on your computer that lets you type in commands to tell the computer what to do. Instead of clicking on things with a mouse, you write instructions, and the computer follows them. It's like talking directly to your computer using text.
Click the **Launchpad** icon in the Dock, start typing "**Terminal** " in the search field, then click the **Terminal** icon:
![](https://files.readme.io/3291b8cd2dda2294bc83c86b27ace24b4f14975f3736e73f954885e03ea562c4-Step7.jpg)
  2. Download the IO Binary for MacOS using the following link in the Terminal:
```
curl -L https://github.com/ionet-official/io_launch_binaries/raw/main/io_net_launch_binary_mac -o io_net_launch_binary_mac

```

  3. Grant permissions to the new IO Binary with this command:
```
chmod +x io_net_launch_binary_mac

```
![](https://files.readme.io/62adb19e9554964bb2165220b1765c75fd4fd00f4d9969f2183bb93a38d0e40a-Step8.jpg)
  4. Copy generated the IO Binary address provided in the wizard and past it into Terminal to run further:
```
./io_net_launch_binary_mac

```

> ## 📘
> To disable sleep mode for a device, pass the --disable_sleep_mode=true argument at the end of the command line.
> ```
./io_net_launch_binary_mac --disable_sleep_mode=true

```

> You can find more additional arguments to use with the IO Binary command [here](https://github.com/ionet-official/io_launch_binaries?tab=readme-ov-file#usage).
![](https://files.readme.io/683fbce68de7b3917192602974b1798b2ec72ef9bce09131884c709ea3923ffe-Step9.jpg)


### [](https://docs.io.net/docs/install-on-macos#7-authorize-your-new-device)
The IO Binary may prompt you to authorize your new device. 
> ## 📘
> Remember, you have 3+ minutes to complete the authorization of the device. If you miss it, rerun the code again.
You can do this in two ways:
  1. **Copy the Link from the Terminal** : 
![](https://files.readme.io/1fe091affcc9ecea5a6c7ae920614ad99d92f7e0e8880e63b71d279e30f5e88e-Step10.jpg)
Paste it into your browser and confirm the action. After confirmation, the system will prompt you to log in.
![](https://files.readme.io/75a85cc630a26880d26fccca2842d9348507fca6dfb709e57f9d5f650c43d4ff-Step11.jpg)
  2. **Copy the Code from the Terminal** : 
![](https://files.readme.io/4c7cc651857433572f524da527258c5a4642945c8dc0e016df457fada8f26477-Step12.jpg)
Enter this code on the page <https://auth0.io.solutions/activate> to authorize the device. You will be prompted to log in.
![](https://files.readme.io/ec4ce726825eb4890de728b4c776d51a86f5a0439db945f3415ef5dda7a76c16-Step13.jpg)


> ## 📘
> Onboard Multiple Devices by Bypassing Interactive Authentication
> To onboard a new device, use the following command with the **--token** flag:
> ![](https://files.readme.io/6d8bb6bdbf6dd9d4579553b2acb5b66abc0b4de472f894ec26628363fe363738-Step14.png)```
./io_net_launch_binary_mac --token your-token-value

```

> This will allow you to bypass the interactive authentication process.
### [](https://docs.io.net/docs/install-on-macos#8-remove-previously-installed-docker-containers)
IO Binary will ask you questions related to previously installed Docker Containers. To continue the installation of IO Worker, you must agree to remove all old containers. To proceed enter **Yes**.
![](https://files.readme.io/c84db64596d5b5e755d2a1071dd28e317cdf17d3369203ef48934a38e7dbc95e-Step15.jpg)
### [](https://docs.io.net/docs/install-on-macos#9-wait-for-worker-connection-to-complete)
IO Binary will install all additional containers and images for your Docker. The process may take some time to complete as it installs additional packages for Docker. Please allow the installation process to finish.
![](https://files.readme.io/06971281dcd23dd8542851d0730f39e35c59f05d3d5ba7024fbee9b718c3a270-Step16.jpg)
Afterward, return to the browser to complete the installation.
You may need to wait for up to 10 minutes while the device checks and connects to the IO Ecosystem. If it doesn't connect, contact customer support by logging into your [IO.Net account](https://worker.io.net).
![](https://files.readme.io/7059edf-Step13.gif)
> ## 🚧
> Please disable power-saving mode when running your devices on IO Net. Power-saving mode can impair device performance, potentially leading to failure in PoW or being classified as not providing adequate computing power.
### [](https://docs.io.net/docs/install-on-macos#congratulations-on-successfully-setting-up-your-first-worker)
Now that your Worker has been successfully created and is running, you can track its status on the Workers page.
![](https://files.readme.io/39d09fdd09c068a8aa8ab32d14562b94b1da1fbb7221dc4a01ad8ae3c8058104-step18.png)   

> ## 📘
> If you're having trouble installing the Worker, please refer to our [MacOS Worker troubleshooting guide](https://docs.io.net/docs/troubleshoot-macos-worker) or the [general Worker troubleshooting guide](https://docs.io.net/docs/troubleshoot-worker). If the issue persists or you need further assistance, feel free to [check our knowledge base](https://support.io.net/en/support/home) for answers, and if you still need help, don’t hesitate to open a support ticket!
> ## 🚧
> Be aware that you will be installing a 20GB size container. This contains all the packages needed to serve AI/ML apps. Everything happens inside the container, nothing within the container can access your filesystem.
2 months ago
* * *
What’s Next
  * [MacOS Troubleshoot Worker](https://docs.io.net/docs/troubleshoot-macos-worker)
  * [MacOS: Install Docker](https://docs.io.net/docs/install-docker-on-macos)


  * [](https://docs.io.net/docs/install-on-macos)
  *     * [Before Starting, Check Your Mac Processor](https://docs.io.net/docs/install-on-macos#before-starting-check-your-mac-processor)
    * [Go to cloud.io.net](https://docs.io.net/docs/install-on-macos#go-to-cloudionet)
    * [1. From IO Elements Navigate to Worker Section](https://docs.io.net/docs/install-on-macos#1-from-io-elements-navigate-to-worker-section)
    * [2. Use "Connect New Worker" Button to Open the Wizard](https://docs.io.net/docs/install-on-macos#2-use-connect-new-worker-button-to-open-the-wizard)
    * [3. Name Your Device](https://docs.io.net/docs/install-on-macos#3-name-your-device)
    * [4. Select MacOS Operating System “OS”](https://docs.io.net/docs/install-on-macos#4-select-macos-operating-system-os)
    * [5. Prerequisites for Mac](https://docs.io.net/docs/install-on-macos#5-prerequisites-for-mac)
    * [6. Download and Launch IO Binary](https://docs.io.net/docs/install-on-macos#6-download-and-launch-io-binary)
    * [7. Authorize Your New Device](https://docs.io.net/docs/install-on-macos#7-authorize-your-new-device)
    * [8. Remove previously installed Docker containers](https://docs.io.net/docs/install-on-macos#8-remove-previously-installed-docker-containers)
    * [9. Wait for Worker Connection to Complete](https://docs.io.net/docs/install-on-macos#9-wait-for-worker-connection-to-complete)
    * [Congratulations on Successfully Setting up Your First Worker.](https://docs.io.net/docs/install-on-macos#congratulations-on-successfully-setting-up-your-first-worker)



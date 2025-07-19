# Device Block Reward Multiplier
A detailed comparison of 2025 block reward multipliers by device type, with upcoming staking-related adjustments.
The io.net block reward system uses performance-based multipliers to fairly distribute rewards across a wide variety of hardware types. These multipliers are designed to reflect the relative utility, compute performance, and cost-efficiency of each device, ensuring the most effective hardware for AI workloads is appropriately incentivized.
## [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#network-expansion-and-updated-reward-structure)
On **June 4, 2025 at 3 PM UTC** , io.net is significantly expanding its network with the addition of over **800 NVIDIA H200 GPUs**. This is the largest single onboarding of enterprise-grade hardware in our history and is part of our commitment to scaling infrastructure for enterprise AI workloads like training and inference.
To ensure fair distribution of rewards as the network grows, the block reward system has been updated to reflect the following changes:
  * Updated device multipliers
  * New reward pool categories
  * Temporary staking grace period


## [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#reward-pool-categories)
Pool Type | Description  
---|---  
🔴 **No longer supported** | Low-tier or outdated devices. Multiplier set to 0. **No longer earn rewards.**  
🟡 **Community Pool** | Consumer and mid-range devices. **Earn 5% of block rewards.**  
🟢 **Enterprise Pool** | High-performance processors. **Earn 95% of block rewards.**  
## [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#device-earning-multiplier-comparison)
#### [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#-no-longer-supported)
Processor | Current Multiplier | New Multiplier | Notes  
---|---|---|---  
M2 Max | 1 | 0 | Already dropped  
M2 Pro | 0.75 | 0 | Already dropped  
M2 Ultra | 1.25 | 0 | Already dropped  
A10 | 0.75 | 0 | Dropped due to lack of demand and supply  
A10G | 0.75 | 0 | Dropped due to lack of demand and supply  
A16 | 1 | 0 | Dropped due to lack of demand and supply  
A40 | 2 | 0 | Dropped due to lack of demand and supply  
GeForce GTX 1080 Ti | 0.25 | 0 | Dropped due to lack of demand  
GeForce GTX 2080 Ti | 0.25 | 0 | Dropped due to lack of demand  
GeForce GTX 3050 | 0.25 | 0 | Dropped due to lack of demand  
GeForce GTX 3050 Ti | 0.25 | 0 | Dropped due to lack of demand  
#### [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#%F0%9F%9F%A1-community-pool)
Processor | Current Multiplier | New Multiplier | Notes  
---|---|---|---  
M3 | 0.5 | 1 | TFLOP-based adjustment with bonus for unified memory  
M3 Pro | 0.75 | 1.25 | TFLOP-based adjustment with bonus for unified memory  
M3 Max | 1 | 1.5 | TFLOP-based adjustment with bonus for unified memory  
M4 | 0.5 | 1 | TFLOP-based adjustment with bonus for unified memory  
M4 Pro | 0.75 | 1.25 | TFLOP-based adjustment with bonus for unified memory  
M4 Max | 1 | 1.5 | TFLOP-based adjustment with bonus for unified memory  
GeForce RTX 3060 | 0.25 | 0.75 | TFLOP-based adjustment  
GeForce RTX 3060 Ti | 0.25 | 0.75 | TFLOP-based adjustment  
GeForce RTX 3070 | 0.25 | 1 | TFLOP-based adjustment  
GeForce RTX 3070 Ti | 0.25 | 1 | TFLOP-based adjustment  
GeForce RTX 3080 | 0.25 | 1.5 | TFLOP-based adjustment  
GeForce RTX 3080 Ti | 0.25 | 1.75 | TFLOP-based adjustment  
GeForce RTX 3090 | 0.5 | 1.75 | TFLOP-based adjustment  
GeForce RTX 3090 Ti | 0.5 | 2 | TFLOP-based adjustment  
GeForce RTX 4060 | 0.25 | 1 | TFLOP-based adjustment  
GeForce RTX 4060 Ti | 0.25 | 1 | TFLOP-based adjustment  
GeForce RTX 4070 | 0.25 | 1.5 | TFLOP-based adjustment  
GeForce RTX 4070 Ti | 0.25 | 2.5 | TFLOP-based adjustment  
GeForce RTX 4080 | 0.5 | 2.75 | TFLOP-based adjustment  
L4 | 0.75 | 0.25 | TFLOP-based adjustment  
RTX 4000 | 0.4 | 0.75 | TFLOP-based adjustment  
RTX 4000 SFF Ada Generation | 0.5 | 1 | TFLOP-based adjustment  
RTX 5000 | 0.25 | 1.5 | TFLOP-based adjustment  
RTX 5000 Ada Generation | 1.5 | 3 | TFLOP-based adjustment  
RTX 6000 Ada Generation | 2.5 | 4.5 | TFLOP-based adjustment  
RTX A4000 | 0.4 | 1.5 | TFLOP-based adjustment  
RTX A5000 | 0.75 | 1.5 | TFLOP-based adjustment  
RTX A6000 | 1.5 | 2 | TFLOP-based adjustment  
Tesla T4 | 0.4 | 0.5 | TFLOP-based adjustment  
Tesla V100-PCIE-16GB | 0.5 | 0.75 | TFLOP-based adjustment  
Tesla V100-PCIE-32GB | 0.75 | 0.75 | TFLOP-based adjustment  
Tesla V100-SXM2-16GB | 0.5 | 0.75 | TFLOP-based adjustment  
Tesla V100-SXM2-32GB | 0.75 | 0.75 | TFLOP-based adjustment  
Tesla V100S-PCIE-32GB | 0.75 | 0.75 | TFLOP-based adjustment  
#### [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#%F0%9F%9F%A2-enterprise-pool)
Processor | Current Multiplier | New Multiplier | Notes  
---|---|---|---  
L40S | 2.25 | 3 | High-demand based adjustment  
A100 80GB PCIe | 5 | 5 | No change  
A100-PCIE-40GB | 2 | 2 | No change  
A100-SXM4-80GB | 5 | 5 | No change  
GeForce RTX 4090 | 0.75 | 1.25 | High-demand based adjustment  
GeForce RTX 4090 D | 0.75 | 1.25 | High-demand based adjustment  
H100 80GB HBM3 | 10 | 10 | No change  
H100 PCIe | 10 | 10 | No change  
H100 80G PCIe | 10 | 10 | No change  
B200 | 30 | 30 | No change  
H200 | 15 | 12 | High-demand based adjustment  
## [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#overview-of-staking-requirements)
> ## 🚧
> Important: Changes to Staking Requirements Coming July 1, 2025
> Until **July 1, 2025** , staking requirements will continue to be calculated using the current earning multiplier.
To qualify for block rewards, each device must meet a minimum staking threshold calculated as follows:
  * **Base Stake** per processor: 200 $IO
  * **Earning Multiplier** : Varies by device performance
  * **Number of processors** : Total processors in the device


###### [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#minimum-stake--base-stake-%C3%97-max1-earning-multiplier-%C3%97-number-of-processors)
Starting **July 1, 2025** , staking requirements may increase for some devices, as a new calculation logic will take effect. For example:
  * A device with **8** H100 **GPUs** , each having an earning **multiplier of 10** :  
Minimum Stake calculation: **200 × 10 × 8 = 16,000 $IO**
  * A device with **4** RTX 4070 **GPUs** , each having an earning **multiplier of 0.25** :  
Minimum Stake calculation: 200 × max(1, 0.5) × 4 = **200 × 1 × 4 = 800 $IO**


> ## 📘
> Even if the earning multiplier is less than 1, the multiplier used in the calculation defaults to 1 to ensure a minimum stake of 200 $IO per processor.
### [](https://docs.io.net/docs/proposed-device-block-reward-multiplier#upcoming-adjustments)
With the integration of new H200 GPUs and the introduction of a Community Hardware Pool, the following changes are anticipated:
  * **Updated Multipliers:** Devices will have their earning multipliers recalibrated based on performance metrics.
  * **Adjusted Staking Requirements:** As multipliers change, the corresponding staking requirements will also adjust.
  * **Grace Period** : A one-month grace period will be provided before new staking requirements are enforced.


> ## 🚧
> Important Note
> **Higher multiplier** ≠ **always higher rewards.**  
>  Actual rewards depend on several factors - including the number of eligible devices in a block, pool allocation (e.g., Community vs. Enterprise), and your device’s multiplier.
For more detailed information on staking requirements and calculations, please refer to the [IO Staking Documentation](https://docs.io.net/docs/io-staking).
about 2 months ago
* * *
  * [](https://docs.io.net/docs/proposed-device-block-reward-multiplier)
  *     * [Network Expansion and Updated Reward Structure](https://docs.io.net/docs/proposed-device-block-reward-multiplier#network-expansion-and-updated-reward-structure)
    * [Reward Pool Categories](https://docs.io.net/docs/proposed-device-block-reward-multiplier#reward-pool-categories)
    * [Device Earning Multiplier Comparison](https://docs.io.net/docs/proposed-device-block-reward-multiplier#device-earning-multiplier-comparison)
    * [Overview of Staking Requirements](https://docs.io.net/docs/proposed-device-block-reward-multiplier#overview-of-staking-requirements)
      * [Upcoming Adjustments](https://docs.io.net/docs/proposed-device-block-reward-multiplier#upcoming-adjustments)



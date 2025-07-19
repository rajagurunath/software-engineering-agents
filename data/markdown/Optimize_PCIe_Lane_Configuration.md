# Optimize PCIe Lane Configuration
When onboarding new devices into the IO.NET network, it’s essential to review the hardware installed and ensure that it is fully capable of performing as expected. We recommend verifying that your hardware supports the required PCIe (Peripheral Component Interconnect Express) lanes. PCIe lanes are the fundamental building blocks of a PCIe connection, enabling communication between a device and the CPU.
## [](https://docs.io.net/docs/optimize-pcie-lane-configuration#locate-pcie-lanes-for-your-cpu)
To ensure optimal performance and stability, it’s recommended that your device's CPU be capable of providing the number of PCIe lanes required for the hardware installed. The number of PCIe lanes required varies depending on the number of PCIe hardware components installed on your motherboard.
### [](https://docs.io.net/docs/optimize-pcie-lane-configuration#locate-the-number-of-pcie-lanes-for-your-cpu)
  * For Intel CPUs, search Intel Ark for your CPU model and look for “Max # of PCI Express Lanes” (here’s an example for the Intel Core i9 14900k, which provides 20x PCIe lanes).
  * For AMD CPUs, search AMD’s Processor Specifications site for your model to find PCI Express versions.


### Device Type
### PCIe Lane Requirements
#### GPUs
- Consumer-grade GPUs, such as NVIDIA 30-series and 40-series models, require 8 PCIe lanes per GPU and should be configured to use an x8 PCIe slot  
- Enterprise-grade GPUs, such as NVIDIA H100 and A100 models, require 16 PCIe lanes per GPU and should be configured to use an x16 PCIe slot 
#### SATA SSDs & NVMe SSDs
- SATA SSDs require 2x PCIe lanes per device  
- NVMe SSDs require a minimum of 4x-8x PCIe lanes per device; the exact number depends on the NVMe SSD generation (e.g., Gen4, Gen5) and the motherboard's maximum supported generation 
#### Other Devices
- Network Adapters (1Gbps, 10Gbps) require between 4x-8x PCIe lanes - Sound cards require between 4x-8x PCIe lanes  
- Storage expansion cards and HBAs (Host Bus Adapters) require between 8x-16x PCIe lanes (e.g., those that enable you to add multiple NVMe SSDs to a single PCIe card or arrange storage devices in JBOD configuration) 
  

> ## 📘
> Note: We strongly recommend removing all PCI devices that are not a GPU, Storage Device, or Network Adapter from your system. These devices won’t be used, and they will reduce the number of PCIe lanes available for other critical components.
### [](https://docs.io.net/docs/optimize-pcie-lane-configuration#configure-pcie-lane-width)
To ensure that each of your GPUs performs optimally, we strongly recommend configuring the PCIe Lane Width for each GPU to match the number of PCIe lanes required and avoid mixing lane widths.
Configuring PCIe Lane Width varies by motherboard manufacturer. Consult your motherboard manufacturer's manual for detailed guidance.
### [](https://docs.io.net/docs/optimize-pcie-lane-configuration#pcie-lane-width-configuration-example)
Using 4x NVIDIA RTX 4090s, each of which requires 8x PCIe lanes (for a total of 32 PCIe lanes), each GPU should be configured to use an x8 PCI Lane Width in the motherboard BIOS. This will ensure that each of the 4090s can perform as expected.
> ## 📘
> Note: We recommend all GPUs installed on your device use the same PCI Lane Width. In the example above, each of the 4090s should be set to use an x8 PCI Lane Width (as they are consumer GPUs). If your motherboard cannot match PCI Lane Widths for each GPU installed, we recommend reducing the number of GPUs installed on the device to ensure optimal performance.
### [](https://docs.io.net/docs/optimize-pcie-lane-configuration#pcie-riser-cables)
Riser Cables (GPU Risers) insert directly into PCIe slots on the motherboard and allow you to install more GPUs on your device than possible due to the size of modern GPUs and the limited space available on modern motherboards.
If using Riser Cables, ensure they are labeled as x8 or x16 (depending on your GPU model). Avoid risers that split PCIe lanes (bifurcate) into x1, x2, or x4 slots, as these cannot deliver the required performance and may reduce system stability.
6 months ago
* * *
What’s Next
  * [Supported Devices](https://docs.io.net/docs/supported-devices)
  * [Proof of Work](https://docs.io.net/docs/proof-of-work)


  * [](https://docs.io.net/docs/optimize-pcie-lane-configuration)
  *     * [Locate PCIe Lanes for Your CPU](https://docs.io.net/docs/optimize-pcie-lane-configuration#locate-pcie-lanes-for-your-cpu)
      * [Locate The Number of PCIe Lanes for Your CPU](https://docs.io.net/docs/optimize-pcie-lane-configuration#locate-the-number-of-pcie-lanes-for-your-cpu)
      * [Configure PCIe Lane Width](https://docs.io.net/docs/optimize-pcie-lane-configuration#configure-pcie-lane-width)
      * [PCIe Lane Width Configuration Example](https://docs.io.net/docs/optimize-pcie-lane-configuration#pcie-lane-width-configuration-example)
      * [PCIe Riser Cables](https://docs.io.net/docs/optimize-pcie-lane-configuration#pcie-riser-cables)



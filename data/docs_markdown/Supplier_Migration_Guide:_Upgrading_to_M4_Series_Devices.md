# Supplier Migration Guide: Upgrading to M4 Series Devices
April 2025
Suppliers on io.net can now seamlessly upgrade their existing inventory of**M2 Pro, M2 Max, and M2 Ultra** devices to the cutting-edge **M4 series.** This transition ensures enhanced performance, improved efficiency, and continued eligibility for earnings on the io.net platform.
> ## 🚧
> **Important Pre-Migration Requirement:**
> Before initiating the migration, ensure your current M2 worker has been actively earning Block Rewards for at least the last 3 continuous hours (i.e., passing PoW tests and contributing work).
> If this condition is not met, the new M4 device will be automatically blocked during the migration process.
### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#important-migration-dates)
  * **Migration Start:** UTC 09:00 AM on April 3rd, 2025
  * **End of Support for M2 Devices:** UTC 23:59:59 on April 21st, 2025
  * **Migration Window Closes:** UTC 23:59:59 on April 21st, 2025


> ## 📘
> Only currently connected devices with full stake are eligible for migration.
### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#m4-series-device-options)
Device | Earning Multiplier | Ray Cluster Pricing | Staking Requirement  
---|---|---|---  
M4 | 0.5x | $0.10/hour | $IO 200  
M4 Pro | 0.75x | $0.13/hour | $IO 200  
M4 Max | 1x | $0.15/hour | $IO 200  
### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#migration-process)
##### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#step-1-disconnect-your-m2-device)
Before migrating, ensure your **M2 Pro, M2 Max, or M2 Ultra** device is **disconnected** from the io.net network.
##### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#step-2-execute-the-migration-command)
Once your M2 device is disconnected, run the following command on your new **M4, M4 Pro, or M4** Max device:
cURL
```
./io_net_launch_binary_mac --device_id={same device id} --user_id={same user_id} 
--operating_system="macOS" --usegpus=false --device_name="{same device name}"

```

##### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#step-3-ensure-proper-configuration)
Your new **M4 series** device should be **correctly configured** with a **stable internet connection** to avoid loss of **Block Rewards** during migration.
### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#benefits-of-migration)
When migrating to the M4 series, your new device will:
  * **Retain** **the same device_id**
  * **Retain the same $IO staked** (M2 Pro/Max staking requirements match M4/M4 Pro/M4 Max)
  * **For M2 Ultra migrations** : The excess 50 $IO (beyond the minimum staking requirement) will be withdrawable without a cooldown period after approximately 24-48 hours post-migration.**


### [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#additional-update)
This migration ensures suppliers remain operational on io.net while benefiting from the **next-generation M4 series devices**. We appreciate your continued support as we drive decentralized computing forward.
  

**Thank you for your continued partnership and support as we move towards a more innovative future together.**
If you have any questions, please contact io.net support.  
The io.net Team
about 2 months ago
* * *
  * [](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices)
  *     * [Important Migration Dates:](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#important-migration-dates)
    * [M4 Series Device Options](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#m4-series-device-options)
    * [Migration Process:](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#migration-process)
    * [Benefits of Migration:](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#benefits-of-migration)
    * [Additional Update:](https://docs.io.net/docs/supplier-migration-guide-upgrading-to-m4-series-devices#additional-update)



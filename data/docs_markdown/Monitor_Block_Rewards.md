# Monitor Block Rewards
## [](https://docs.io.net/docs/monitor-block-rewards#table-of-contents)
  * [Block Rewards Tab](https://docs.io.net/docs/monitor-block-rewards#block-rewards-tab)
  * [Block Details Table](https://docs.io.net/docs/monitor-block-rewards#block-details-table)
  * [Block Reward Details](https://docs.io.net/docs/monitor-block-rewards#block-reward-details)
    * [Exceptions](https://docs.io.net/docs/monitor-block-rewards#exceptions)


### [](https://docs.io.net/docs/monitor-block-rewards#block-rewards-tab)
The Block Rewards tab provides a transparent view of io.net's Block Rewards and coin emissions. Users can consult this information to monitor worker nominations and their status. Users can track the performance and success rates for worker nominations and block completion. Information on coin emissions and block rewards provides transparency about io.net network’s health.
The screenshot below is of the **Block Rewards** tab and is explained the sections below. 
![](https://files.readme.io/a4a3f9b-block_rewards.png)
The top section of the **Block Rewards** tab provides real-time data about IO Coin emissions and blocks.
![](https://files.readme.io/1fbaaa2-bwtop.png)
Block 
Description 
Total Coins Distributed 
The cumulative number of IO Coins distributed since inception.
Today's Distributed Coins 
Total number of IO Coins distributed for the current calendar day. 
Total Blocks Computed 
The cumulative number of blocks successfully added to the blockchain since inception.
Next Block Start Time
The estimated time when the next block will be initiated. Blocks are added to the chain at hourly intervals.
Total Unique Workers Paid 
The number of unique workers that earned a block reward since inception. 
Today's Unique Workers Paid 
The number of unique workers that earned a block reward for the current calendar day. Each calendar day ends at UTC+0. 
### [](https://docs.io.net/docs/monitor-block-rewards#block-details-table)
The **Block Details Table** provides a detailed overview of the blocks processed in the blockchain. The list provides a transparent and verifiable record of all blocks in the IO Coin blockchain. Users can search for specific blocks and view details, verify transactions, and trace the history and integrity of the blockchain.
The table below is an important tool to monitor the blockchain's performance, transparency, and efficiency, and provides users with insights into the block creation process and the distribution of rewards.
You can download a CSV file for each Block ID by going to [Block Rewards](https://block-rewards.io.solutions/). 
![](https://files.readme.io/9eda851-brbottom.png)
Column 
Description 
Search Block ID 
Allows you to search for specific Block IDs. 
Status 
The current state of each block within our blockchain network.
In Progress 
The worker has been nominated for a block reward. The block isn't complete nor added to the blockchain. When the block closes, the worker is notified. 
Completed 
The block has been successfully validated and added to the blockchain. 
Failed 
The attempt to create a block failed. 
Block ID 
A unique identifier assigned to each block within a blockchain. This assists in maintaining the chronological order and integrity of the blockchain. 
Processed Time 
The exact time the block was completed in UTC. 
Total Rewards Emission 
The total distribution of rewards for a specific block. 
Nominated Workers 
Workers nominated for the hourly block reward. To be nominated, the worker must satisfy the requirements of recent Uptime (connection status) and Proof of Work. The worker is evaluated again when the block closes. If it satisfies the Proof of TimeLock (based on Uptime) and Proof of Work (PoW) requirements for the one hour period, the worker is rewarded based on their final score.
Succeeded 
The total number of workers that succeeded in meeting the criteria for a block reward of the total workers that were nominated.
Failed 
Number of workers that failed to earn a block reward of the total workers that were nominated. 
### [](https://docs.io.net/docs/monitor-block-rewards#block-reward-details)
If you click on a specific block, you can view the details for each IO Worker Block Reward. This page provides a complete list of all the nominated workers for the specific block. You can filter to view Completed (Successful) and Failed workers. You can search for your Device ID to check the status of your Block Reward. 
> ## 📘
> If a block reward is in progress, you can't click on it until it's complete.
![](https://files.readme.io/03091d7-br2.png)
The screenshot below is of one IO Worker Block Reward. It provides details about the individual worker. You can click on the **Device ID** to view the info related to the worker in the **Workers** tab. 
![](https://files.readme.io/61906ca-br1.png)
Below is Block Reward calculation formula.
```
+(0.02 x (connectivity_tier_number" / 4.0))  
   + (2.0 x "hardware_multiplier" x "processor_quantity") ) x 100 + (0.05 x "was_hired"))x 10

```

Block 
Description 
IO Worker Block Reward
To the right of this, you can view the Completed or Failed status. The green Completed status indicates success.
Device ID 
You can copy the **Device ID** or click it to view the info related to the worker in the **Workers** tab.
Connectivity Tier 
The Connectivity Tier that the worker qualifies for. This is an option when a customer reserves a GPU/CPU when they deploy a cluster.
Processor
The processor type, GPU/CPU. In this example, it's a Nvidia L4 GPU.
Processor Quantity
Number of processors available for the worker.
POTL
(Proof of Timelock)- Verifies the uptime for the worker. This can be executed against a hired worker.
POW
(zkTFLOPs Proof) Tasks the worker must solve to verify the worker. To learn more about POW, see [Proof of Work](https://docs.io.net/docs/proof-of-work). This is never executed against a hired worker.
Total Score
The score your worker receives based on its performance as measured by **POW** and **POTL**.
Rewarded
The amount of IO Coin the worker earned based on **Total Score**
#### [](https://docs.io.net/docs/monitor-block-rewards#exceptions)
**Exempt-Hired**
If a worker was nominated for a Block Reward, but was hired by a customer during the evaluation hour, io.net exempts the worker from Proof of Work. The exemption occurs so the worker can successfully complete the job for the customer. 
In the screenshot below, the **IO Worker Block Reward** is marked as **Completed**. The worker was hired by a customer so no POW tasks were assigned. Uptime was tested during the hour and the worker satisfied the requirement. Since it was successful, a reward was granted.
![](https://files.readme.io/7f01b1e-exempt-hired.png)
**Exempt-Headnode**
Headnodes must always be available for jobs. For this reason, POW is not executed against headnodes when nominated for Block Rewards. Uptime (POTL) is tested during the evaluation. In the example below, the headnode satisfied the requirement. Since it was successful, a reward was granted.
![](https://files.readme.io/b33bbd7-ex_headnode.png)
9 months ago
* * *
  * [](https://docs.io.net/docs/monitor-block-rewards)
  *     * [Table of Contents](https://docs.io.net/docs/monitor-block-rewards#table-of-contents)
      * [Block Rewards Tab](https://docs.io.net/docs/monitor-block-rewards#block-rewards-tab)
      * [Block Details Table](https://docs.io.net/docs/monitor-block-rewards#block-details-table)
      * [Block Reward Details](https://docs.io.net/docs/monitor-block-rewards#block-reward-details)



# IO Staking
At IO.net, we're committed to building a robust, secure, and decentralized platform for GPU and CPU supply and demand. Our staking program is designed to align incentives, ensure network integrity, and reward active participants in our ecosystem.
> ## 📘
> The content of this doc is subject to change depending on successful contract auditing.
### [](https://docs.io.net/docs/io-staking#why-staking)
Staking is a crucial component of our network security and efficiency. Requiring suppliers to stake $IO allows us to: 
  * Encourage long-term commitment to our platform.
  * Create an incentive for good behavior.
  * Establish a mechanism to discourage and penalize malicious actions.


### [](https://docs.io.net/docs/io-staking#how-it-works)
**Staking Requirements**
To participate in our network and receive block rewards, GPU and CPU suppliers must stake a specific amount of $IO. The exact staking amount required is determined on the supplier's capacity and their contribution to the network.
The staking requirement is displayed in the UI. The formula for the total is explained below. 
  1. Base requirement (minimum stake per card) X = $IO 200. 
  2. If the multiplier per GPU on the device is less or equal to 1, the per GPU stake is 1 * X. The minimum staking remains $IO 200.
  3. If the multiplier per GPU on the device is greater than 1, then the multiplier value is represented by M. The per GPU stake on this device is M * X. (Device Earning Multiplier * Minimum Stake)
  4. If there are multiple (N) GPUs on the device, the total device stake value is M * N * X. 

```
minimum_stake_required = base_requirement_per_card * max(1, earning_multiplier)

```

**Examples**
  1. If there are eight (8) H100 GPUs (earning multiplier=10) on device A. The minimum staking requirement value is $IO 200. Then the amount required to stake on device A is 8 * 10 * 200 = 16,000 $IO.
  2. If there are four (4) 4070s GPUs (earning multiplier=0.25) on device B. The minimum staking requirement value is $IO 200. Then the amount required to stake on device BCD is 4 * 1* 200 = 800 $IO.


**Rewards**
Each supplier’s device will have a dedicated smart contract where the $IO stake is secured. Block Reward Eligibility is determined on a per-device basis. In Phase I, Block Rewards are accrued to the [Solana wallet address ](https://docs.io.net/docs/solana)associated with your account and are distributed through periodic reward claims. This ensures a fair and transparent distribution of rewards to all qualifying participants.
**Unstaking Process**
When a supplier decides to unstake their $IO, a 14-day cooldown period is initiated. Once unstaked, $IO in a cooldown period is no longer counted toward minimum staking requirement for Block Rewards. This period helps maintain network stability and prevents potential manipulation.
The action of unstaking is irreversible. You can not restake to your device until the cooldown period ends. You must withdraw the coins after the cooldown period to stake to the same device again. 
> ## 📘
> When you unstake and withdraw your IO Coins, always use the wallet used in the initial stake.
**Security**
To protect our network and users, we implemented a slashing mechanism. Staked $IO and accrued block rewards can be subject to slashing. If a supplier engages in malicious behavior, such as spoofing or compromising data, a portion of their staked $IO tokens may be slashed (i.e., deducted from their stake). Also, if your device is providing inadequate service, it is subject to slashing. 
Slashed $IO is subject to a one month reconsideration process. If you notice your device stake is slashed, you can open up a support ticket. IO support will present technical evidence that proves why the device was identified for spoofing or other malicious behavior. Device owners can appeal this decision. If the device owner doesn't appeal the decision or the appeal is lost, the slashed $IO will be burned.
### 
**Get Started**
[](https://docs.io.net/docs/io-staking#get-started)
To participate in the staking program, ensure you have the required amount of $IO and follow our simple staking process in the IO.net platform.
> ## 📘
> In Phase I, only device owners can stake to their own devices. We plan to add features for non-node operators to also stake $IO and earn rewards in Phase II.
We're excited to launch this staking program and look forward to growing our network together. For more detailed information or assistance, please refer to our comprehensive documentation or contact our support team.  
Join us in shaping the future of decentralised computing with IO.net.
#### [](https://docs.io.net/docs/io-staking#staking-release-stages)
  1. **Phase** : Staking is currently **available for workers only**. 
  2. **Phase** : Staking for **non-workers is coming soon.**


For more details on earning multipliers, Block Rewards, and the minimum staking requirements, please refer to our public documentation: [Proposed calibration in earning multiplier and the simulated impact on Block Rewards](https://docs.io.net/docs/proposed-device-block-reward-multiplier).
5 months ago
* * *
  * [](https://docs.io.net/docs/io-staking)
  *     * [Why Staking?](https://docs.io.net/docs/io-staking#why-staking)
    * [How It Works](https://docs.io.net/docs/io-staking#how-it-works)
    * [**Get Started**](https://docs.io.net/docs/io-staking#get-started)
      * [Staking Release Stages](https://docs.io.net/docs/io-staking#staking-release-stages)



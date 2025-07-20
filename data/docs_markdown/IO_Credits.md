# IO Credits
Prepaid credits for deploying compute on IO Cloud.
### [](https://docs.io.net/docs/io-credits#what-are-io-credits)
**IO Credits** are prepaid credits you can use to pay for compute deployments on IO Cloud, including Ray Clusters, VMs, Kubernetes, and Baremetal. **Each IO Credit is equivalent to** 1 USD, making pricing simple and consistent.
![](https://files.readme.io/96c703934740b030402097520657bbb45106447cbd43118f46f6ecb24efea691-IO_Credits1.jpg)
### [](https://docs.io.net/docs/io-credits#quick-start)
  1. Submit a request form to receive IO Credits.
  2. Once approved, credits will appear in your account.
  3. Use your credits to deploy compute or inference workloads.
  4. Track your usage, view your balance, and request withdrawals in **Manage Funds.**


### [](https://docs.io.net/docs/io-credits#why-use-io-credits)
  * Pay once, use anytime
  * Works across all IO products
  * Easier checkout during deployments
  * Refunds and incentives automatically appear as credits
  * API support for fully automated workflows


## [](https://docs.io.net/docs/io-credits#how-to-get-io-credits)
You can fund your IO account by requesting prepaid credits:
  1. Click **"Request IO Credits"** on any IO Cloud product page.
![](https://files.readme.io/4991bf36a10dc3cebf3895b4ff0f958ea87293ecbade02652162442f08f13947-IO_Credits2.jpg)
  2. The IO team will review your request and reach out if any details are needed.
  3. Once approved, your credits will appear in your wallet as a single balance.
  4. You’ll see the updated amount reflected in your account dashboard.


#### [](https://docs.io.net/docs/io-credits#refunds-as-credits)
If a deployment ends early or is cancelled, any unused funds are returned as IO Credits. You'll be notified via the **Notification Center**.
## [](https://docs.io.net/docs/io-credits#how-to-use-io-credits)
#### [](https://docs.io.net/docs/io-credits#compute-products-ray-caas-baremetal-vm)
During checkout, you’ll see three payment options: **USDC** , **IO Coin** and **IO Credits**. Click **IO Credits** to view the **required credits** and see **your available balance**
> ## 📘
> Note: 1 IO Credit = 1 USD
**If credits are enough** , you will be able to click the active **Pay & Deploy Container** button
![](https://files.readme.io/3a024467b6a70650dcb8b247822e5f54087df4843ac5f02230d4b4d10cd085a9-IO_Credits4.jpg)
**If credits are insufficient** , the **Pay & Deploy Container** button will be greyed out with a message: _"Not enough credits. Use another payment method or request more."_
> ## 📘
> Users with zero credits will not see this tab
![](https://files.readme.io/5aaa39b884274496f2e1d7505e8bd438b2121f416b4f780fe000a30b00312e0e-IO_Credits3.jpg)
#### [](https://docs.io.net/docs/io-credits#use-via-api)
Deployment endpoints accept `payment_method: "credits"`.  
If **Balance Is Low** , fallback options may include:
  * `GET /credits/check?amount=XX`
  * Pending Payment state
  * Small negative credit allowance (e.g., -$10)
  * 5-minute grace window with top-up prompt
  * Failure if not topped up in time


## [](https://docs.io.net/docs/io-credits#how-to-manage-your-credits)
#### [](https://docs.io.net/docs/io-credits#view--use-credits)
Go to **Manage Funds** from the top bar. You'll see:
  * **Total IO Credits** – shown as a single balance (in USD)
  * **Request Withdrawal** (for purchased credits only)
  * **Use for IO Cloud**
  * **View Transaction History**

![](https://files.readme.io/4ff659fe3f20e28392dc3f681aa19294be4a18f3ceff628a17e8a01a85971e92-IO_Credits4.jpg)
#### [](https://docs.io.net/docs/io-credits#request-withdrawal)
Submit a manual request to withdraw available **purchased credit** s from your balance.
Withdrawals are only available to users who have submitted the credit request form and paid for their credits.  
Once submitted, withdrawal requests are reviewed by the IO Finance team and are typically processed within **3–7 business days.**
![](https://files.readme.io/88bbd4314c7ff32110932e6267201a4899088cd44284cd250913810a3dfc863b-IO_Credits5.jpg)
#### [](https://docs.io.net/docs/io-credits#transaction-history)
The Transaction History section gives you full visibility into how your IO Credits have been added, used, or refunded. It helps you track spending, reconcile deployments, and understand your current balance.
You’ll find entries for:
  * **Credit purchases** – credits added via BD team approval or SpherePay funding
  * **Usage deductions** – credits spent on compute deployments or inference runs
  * **Refunds** – returned credits from early terminations or unused deployments


Each entry includes**IO Service, Timestamp, Type of transaction, Amount added or deducted, Transaction ID**
Use this log to audit your activity or troubleshoot billing questions.
![](https://files.readme.io/d17cbf842973356dee84d9503f1dc35eaa810121fa53b35c5abcb4cc98d9d575-IO_Credits6.jpg)
## [](https://docs.io.net/docs/io-credits#credit-usage-via-api-and-tracking)
Credits are tied to your IO ID and can be used across all IO Cloud products. When using IO APIs, you can specify the payment method as "`credits`" to automatically deduct from your balance.
## [](https://docs.io.net/docs/io-credits#faqs)
**What happens if I don’t have enough IO Credits?**  
You’ll be prompted to top up or use another payment method. Your deployment will pause temporarily and may fail if not resolved in time.
**Can I convert credits back to USDC?**  
Only purchased credits may be withdrawn, after a manual review by the finance team.
4 days ago
* * *
  * [](https://docs.io.net/docs/io-credits)
  *     *       * [What Are IO Credits?](https://docs.io.net/docs/io-credits#what-are-io-credits)
      * [Quick Start](https://docs.io.net/docs/io-credits#quick-start)
      * [Why Use IO Credits?](https://docs.io.net/docs/io-credits#why-use-io-credits)
    * [How to Get IO Credits](https://docs.io.net/docs/io-credits#how-to-get-io-credits)
    * [How to Use IO Credits](https://docs.io.net/docs/io-credits#how-to-use-io-credits)
    * [How to Manage Your Credits](https://docs.io.net/docs/io-credits#how-to-manage-your-credits)
    * [Credit Usage via API and Tracking](https://docs.io.net/docs/io-credits#credit-usage-via-api-and-tracking)
    * [FAQs](https://docs.io.net/docs/io-credits#faqs)



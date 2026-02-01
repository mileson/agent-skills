![cover_image](./assets/17516865708190.07340629883955996.jpeg)

# AI绘图傻瓜指南 - 5分钟带你生成你的专属AI妹子

原创

卡兹克

数字生命卡兹克

*2023年02月28日 20:08*
*天津*

AI绘图现在已经是非常成熟的方式了，很多大厂也引入了AI绘图的流程，也激发了很多人的创意（比如生成很多符合自己审美的妹子![](./assets/17516865715330.29978469505369076.png)![](./assets/17516865715320.9336888819670361.png)![](./assets/17516865715300.9109635291741526.png)）。

想了解AI绘图的思考可以去看看我之前的文章：[关于ChatGPT的兄弟 - AI绘图的小思考](https://mp.weixin.qq.com/s?__biz=MzIyMzA5NjEyMA==&mid=2647657627&idx=1&sn=e17677d7db3bf4c823aef0df3966dcfa&chksm=f007d0ccc77059da74ee75ce2cb63a954adc587a9922290eb74da170be7c6a82a0706ba62925&scene=21#wechat_redirect)

今天开始手把手教大家如何使用AI绘图生成自己的真人妹子，大概就是下图这样的（当然你可以随便自定义![](./assets/17516865715490.5530510163737079.png)![](./assets/17516865715280.0015464724556023546.png)![](./assets/17516865715260.10746528854854587.png)）

![](./assets/17516865718900.12552914663107728.png)

我们使用的东西叫做stable-diffusion，一个开源的很牛逼的AI绘图模型。现在市面上主流的有两种，stable-diffusion和Midjourney，stable-diffusion的优势是免费、开源、自定义强，但是需要设置一下；Midjourney的优势是简单快捷，生成效果棒，但是需要付费，同时又局限性。

废话不多说，直接开始。

首先你一定要注意你是是**window电脑，显卡是NVIDIA的，并且显存6G以上。（此处不懂的去百度一下，不是重点）**

**一. 安装stable-diffusion**

私信我，回复SD，拿到傻瓜式整合包。

（此处向整合包的原作者B站赛博菩萨@秋葉aaaki致以我最崇高的敬意）

下载好先把【SD-webui-aki-v3】这个压缩包解压到本地（文件包比较大，倒杯水![](./assets/17516865710720.7367784620770033.png)抽根烟![](./assets/17516865712860.04882634550628062.png)，咱别急）。解压完成以后，你就能在解压好的文件夹里看到这两个东西，A启动器和A用户协议。

![](./assets/17516865714990.8580416380682035.png)

我们打开A用户协议，把【我已阅读并同意用户协议】复制到下面的位置

![](./assets/17516865711620.10516114390257647.png)

复制过去以后，Ctrl+S保存，不放心可以多按几下，然后关闭记事本。打开A启动器。第一次启动得等一会。于是我们就看到了这个页面。

![](./assets/17516865713940.7712037326250293.png)

先升级一下，点击版本管理，一键升级，把咱们的stable-diffusion更新到最新版本。

![](./assets/17516865717860.973610800375782.png)

再点扩展管理，一键升级内置插件。

![](./assets/17516865717850.08057405705175158.png)

马上就好了，咱们再来安装两个模型，因为咱们需要生成特定的真人妹子嘛，所以咱们需要特殊的渲染模型才可以，如果用stable-diffusion原本自己的，那就完全出不来感觉了。点击模型管理，添加模型。

![](./assets/17516865722210.25313167625024147.png)

还记得咱们还下了一个模型包文件不，再弹出的窗口中，找到下载的模型包，把里面的那两个文件点击打开添加进去，要一个一个添加，不支持批量。如果出现弹窗不用管内容，直接点击“是”

![](./assets/17516865711430.5910557774340878.png)

然后回到一键启动，点击右下角的一键启动，大功告成！你的本地化部署就完事了，是不是很简单！

![](./assets/17516865716520.706251318520931.png)

然后会出现一个代码窗口，不要慌不要怕，跑程序呢，等等，第一次运行时间也是有点长，需要个几分钟，去倒杯水抽根烟尿泡尿。直到过一会你的浏览器就会自动打开一个stable-diffusion的窗口，运行成功！

![](./assets/17516865713970.9288468532521769.png)

**二****. 生成AI图**

stable-diffusion启动成功，接下来咱们愉快的开始生成你的专属AI妹子~

咱们先把左上角的模型选成ChilloutMix，这个就是专门生成真人照片用的模型。

![](./assets/17516865719820.9389128877098186.png)

当然，stable-diffusion的世界里还有很多很多各种模型，比如能生成很多很多风格的Anythin4.5，比如能生成逼真3D幻想风格的DreamShaper，这个大家以后可以自己探索~这篇先教大家生成AI妹子。

然后我这里直接给大家一组关键词

<lora:koreanDollLikeness\_v15:0.66>, best quality, ultra high res, (photorealistic:1.4), 1girl, beige sweater, smile, laughing, bare shoulders, solo focus, (full body), (platinum pink hair:1), ((puffy eyes)), looking at viewer, facing front, closeup
Negative prompt: paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glans
Steps: 28, Sampler: DPM++ SDE Karras, CFG scale: 7, Seed: 1735215259, Size: 640x768, Model hash: fc2511737a, Model: chilloutmix\_NiPrunedFp32Fix, Denoising strength: 0.75, Clip skip: 2, Mask blur: 4

先不用管是什么意思，直接复制，然后粘贴到stable-diffusion的这个位置

![](./assets/17516865721360.8402174745681618.png)

然后点击这个小箭头

![](./assets/17516865722500.7964979839494184.png)

就能看到字段变啦，大家先只要知道上面两个输入框是什么意思就行了

第一个框：提示词，Prompt，我们的图片会按照你的提示词来生成，每个提示词用逗号隔开，比如我们这次输入的提示词

<lora:koreanDollLikeness\_v15:0.66>, best quality, ultra high res, (photorealistic:1.4), 1girl, beige sweater, smile, laughing, bare shoulders, solo focus, (full body), (platinum pink hair:1), ((puffy eyes)), looking at viewer, facing front, closeup

翻译过来就是

![](./assets/17516865711580.5968919669892271.png)

<lora:koreanDollLikeness\_v15:0.66>, best quality, ultra high res, (photorealistic:1.4), 这一部分大家可以不要动，无脑使用，而后面的提示词可以根据你的喜好随意更换。

第二个框：反向提示词，Negative prompt，意思就是你输入的词绝对不会出现，比如咱们这次输入的

paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glans

翻译过来就是

![](./assets/17516865707980.11653226669598127.png)

输完以后，咱们把种子这块的小骰子点一下，让左边的参数变成-1

![](./assets/17516865724030.6013968078752324.png)

全部完成以后，咱们愉快的点击右上角那个巨大的生成！

![](./assets/17516865711670.015697541709857377.png)

嘟嘟嘟的跑起来后，你就可以看到自己生成的虚拟小姐姐啦。

![](./assets/17516865726950.6352288651034734.png)

想生成不同风格图，直接换后面的提示词就可以，开心的玩起来吧~

下一期，我再详细给教大家不同风格的模型用法、神器级别的可以控制动作插件controlnet。大家帮忙点个关注给个赞吧哈哈。

写在最后。

AI无容置疑，已经到了一个危险和机遇共存的时间点。

**AI好玩，但是绝对不要用来做任何影响社会秩序、侵犯版权肖像权的事情，更不要用来违法犯罪！**

以上，创作不易，有用的话请帮忙点个在看，感恩。

修改于
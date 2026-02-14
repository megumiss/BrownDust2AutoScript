from module.logger import logger
from tasks.base.assets.assets_base_ui import REWARD_POPUP_CHECK, REWARD_POPUP_CLOSE
from tasks.base.page import *
from tasks.base.ui import UI
from tasks.reward.assets.assets_reward import *


class Reward(UI):
    def receive_guild_reward(self):
        logger.hr('receive guild reward', 2)
        self.ui_goto(page_guild)

        for _ in self.loop(timeout=3):
            if self.appear(GUILD_CLAIM_DONE):
                logger.info('Guild reward claimed')
                break
        else:
            logger.warning('Guild reward allready claimed')

    def receive_claim_reward(self):
        logger.hr('receive claim reward', 2)
        self.ui_goto(page_jjc)

        for _ in self.loop():
            if self.appear():
                continue

    def run(self):
        logger.hr('receive bussiness reward', 2)
        # 领取餐厅奖励
        self.ui_ensure(page_business)
        for _ in self.loop():
            if self.match_template_color(BUSINESS_CLAIM):
                self.device.click(BUSINESS_CLAIM)
                self.device.sleep(1)
                continue
            if self.appear(REWARD_POPUP_CHECK) and self.appear_then_click(REWARD_POPUP_CLOSE, interval=1):
                continue
            if self.match_template_color(BUSINESS_CLAIM_DONE):
                logger.info('Business reward claimed')
                break

        # 领取工会每日奖励
        if self.config.Reward_Guild:
            self.receive_guild_reward()

        # 领取每日扫荡奖励
        if self.config.Reward_Claim:
            self.receive_claim_reward()

        self.config.task_delay(server_update=True)

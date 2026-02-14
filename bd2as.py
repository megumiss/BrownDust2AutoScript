from module.alas import AzurLaneAutoScript
from module.logger import logger


class BrownDust2AutoScript(AzurLaneAutoScript):
    def restart(self):
        from tasks.login.login import Login

        Login(self.config, device=self.device).app_restart()

    def start(self):
        from tasks.login.login import Login

        Login(self.config, device=self.device).app_start()

    def stop(self):
        from tasks.login.login import Login

        Login(self.config, device=self.device).app_stop()

    def goto_main(self):
        from tasks.base.ui import UI
        from tasks.login.login import Login

        if self.device.app_is_running():
            logger.info('App is already running, goto main page')
            UI(self.config, device=self.device).ui_goto_main()
        else:
            logger.info('App is not running, start app and goto main page')
            Login(self.config, device=self.device).app_start()
            UI(self.config, device=self.device).ui_goto_main()

    def error_postprocess(self):
        # Exit cloud game to reduce extra fee
        if self.config.is_cloud_game:
            from tasks.login.login import Login

            Login(self.config, device=self.device).app_stop()

    def reward(self):
        from tasks.reward.reward import Reward

        Reward(config=self.config, device=self.device).run()

    def benchmark(self):
        from module.daemon.benchmark import run_benchmark

        run_benchmark(config=self.config)

    def daemon(self):
        from tasks.base.daemon import Daemon

        Daemon(config=self.config, device=self.device, task='Daemon').run()



if __name__ == '__main__':
    bd2as = BrownDust2AutoScript('bd2as')
    bd2as.loop()

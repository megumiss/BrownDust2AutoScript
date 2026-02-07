import traceback

from tasks.base.assets.assets_base_page import *


class Page:
    # Key: str, page name like "page_main"
    # Value: Page, page instance
    all_pages = {}

    @classmethod
    def clear_connection(cls):
        for page in cls.all_pages.values():
            page.parent = None

    @classmethod
    def init_connection(cls, destination):
        """
        Initialize an A* path finding among pages.

        Args:
            destination (Page):
        """
        cls.clear_connection()

        visited = [destination]
        visited = set(visited)
        while 1:
            new = visited.copy()
            for page in visited:
                for link in cls.iter_pages():
                    if link in visited:
                        continue
                    if page in link.links:
                        link.parent = page
                        new.add(link)
            if len(new) == len(visited):
                break
            visited = new

    @classmethod
    def iter_pages(cls):
        return cls.all_pages.values()

    @classmethod
    def iter_check_buttons(cls):
        for page in cls.all_pages.values():
            yield page.check_button

    def __init__(self, check_button):
        self.check_button = check_button
        self.links = {}
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        self.name = text[: text.find('=')].strip()
        self.parent = None
        Page.all_pages[self.name] = self

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def link(self, button, destination):
        self.links[destination] = button


# 主页
page_main = Page(MAIN_GOTO_ARCADE)

# 卡带
page_card = Page(CARD_CHECK)
page_card.link(BACK_CIRCLE, destination=page_main)
page_main.link(MAIN_GOTO_CARD, destination=page_card)

# 工会
page_guild = Page(GUILD_CHECK)
page_guild.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_GUILD, destination=page_guild)

# 一键收获
page_business = Page(BUSINESS_CHECK)
page_business.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_BUSINESS, destination=page_business)

# 抽卡
page_draw = Page(DRAW_CHECK)
page_draw.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_DRAW, destination=page_draw)

# 队伍
page_companion = Page(COMPANION_CHECK)
page_companion.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_COMPANION, destination=page_companion)

# 背包
page_bag = Page(BAG_CHECK)
page_bag.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_BAG, destination=page_bag)

# 任务
page_mission = Page(MISSION_CHECK)
page_mission.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_MISSION, destination=page_mission)

# 成就
page_achv = Page(ACHV_CHECK)
page_achv.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_ACHV, destination=page_achv)

# 活动
page_event = Page(EVENT_CHECK)
page_event.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_EVENT, destination=page_event)

# 邮箱
page_email = Page(EMAIL_CHECK)
page_email.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_EMAIL, destination=page_email)

# 快速狩猎
page_quickhunt = Page(QUICKHUNT_CHECK)
page_quickhunt.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_QUICKHUNT, destination=page_quickhunt)

# 通行证
page_pass = Page(PASS_CHECK)
page_pass.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_PASS, destination=page_pass)

# 魔兽
page_hunter = Page(HUNTER_CHECK)
page_hunter.link(BACK, destination=page_main)
page_main.link(MAIN_GOTO_HUNTER, destination=page_hunter)

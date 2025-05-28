import lib.config as cfg
from lib.assets import *

from lib.util.animations.cloud_transition import *
from lib.util.save_data import *

from lib.pages.start import StartScreen
from lib.pages.rules import RulesScreen
from lib.pages.customize import CustomizeScreen
from lib.pages.lvl_selection import LevelSelectionScreen


def main():
    load_progress()

    start_screen = StartScreen()
    customize_screen = CustomizeScreen()
    rules_screen = RulesScreen()
    level_selection_screen = LevelSelectionScreen(start_screen.channel)

    while True:
        if cfg.current_screen == 'start':
            next_screen = start_screen.run()
            cfg.last_screen = 'start'

        elif cfg.current_screen == 'rules':
            next_screen = rules_screen.run()
            cfg.last_screen = 'rules'

            if next_screen == 'start':
                rules_screen.visible_lines = []
                start_screen.slide_in()
                next_screen = start_screen.run()

        elif cfg.current_screen == 'level_selection':
            next_screen = level_selection_screen.run()
            cfg.last_screen = 'level_selection'

        elif cfg.current_screen == 'customize':
            next_screen = customize_screen.run()
            cfg.last_screen = 'customize'

        else:
            print(f"Unknown screen: {cfg.current_screen}")
            break
        
        cfg.current_screen = next_screen if next_screen else 'start'

if __name__ == "__main__":
    main()

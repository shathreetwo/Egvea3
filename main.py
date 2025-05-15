from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.label import Label

# 한글 폰트 등록 (예: 'NanumGothic' 폰트 사용)
LabelBase.register(name="Noto", fn_regular="NotoSansKR.ttf")

# 기본 폰트 이름을 NanumGothic으로 덮어쓰기
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase

LabelBase.register(name='Roboto', fn_regular='NotoSansKR.ttf')  # 기본 폰트 이름 Roboto 덮어쓰기


class SelectableShip(Button):
    index = NumericProperty(0)
    selected = NumericProperty(0)  # 0: 선택 안됨, 1: 선택됨

    def on_selected(self, instance, value):
        # 선택 상태에 따라 색 변경
        if value:
            self.background_color = (0, 1, 0, 1)  # 초록 강조
        else:
            self.background_color = (1, 1, 1, 1)  # 기본 흰색

class LobbyScreen(Screen):
    selected_ship_index = NumericProperty(-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 가로 스크롤뷰 + 박스레이아웃
        scroll = ScrollView(size_hint=(1, 0.7), do_scroll_y=False)
        ship_layout = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=10)
        ship_layout.bind(minimum_width=ship_layout.setter('width'))

        self.ship_buttons = []

        for i in range(1, 11):
            btn = SelectableShip(text=f'우주선 {i}', size_hint=(None, 1), width=120, index=i)
            btn.bind(on_release=self.select_ship)
            self.ship_buttons.append(btn)
            ship_layout.add_widget(btn)

        scroll.add_widget(ship_layout)
        main_layout.add_widget(scroll)

        # 선택 완료 버튼
        self.confirm_btn = Button(text='선택 완료', size_hint=(1, 0.1))
        self.confirm_btn.bind(on_release=self.confirm_selection)
        main_layout.add_widget(self.confirm_btn)

        # 게임 시작 버튼
        self.start_btn = Button(text='게임 시작', size_hint=(1, 0.1))
        self.start_btn.bind(on_release=self.start_game)
        main_layout.add_widget(self.start_btn)

        self.add_widget(main_layout)

    def select_ship(self, instance):
        # 이전 선택 해제
        for btn in self.ship_buttons:
            btn.selected = 0
        # 현재 선택
        instance.selected = 1
        self.selected_ship_index = instance.index

    def confirm_selection(self, instance):
        if self.selected_ship_index == -1:
            print("우주선을 선택해주세요!")
        else:
            print(f"우주선 {self.selected_ship_index} 선택 완료!")

    def start_game(self, instance):
        if self.selected_ship_index == -1:
            print("게임 시작 전에 우주선을 선택하고 선택 완료를 눌러주세요!")
            return
        # 선택한 우주선 정보 게임 화면으로 넘기고 전환
        self.manager.get_screen('game').selected_ship = self.selected_ship_index
        self.manager.current = 'game'

class GameScreen(Screen):
    selected_ship = NumericProperty(1)

    def on_enter(self):
        print(f"선택된 우주선 번호: {self.selected_ship}")
        # TODO: 선택된 우주선 번호 기반으로 게임 시작 초기화

class SpaceApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LobbyScreen(name='lobby'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    SpaceApp().run()

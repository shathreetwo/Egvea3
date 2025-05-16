from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.label import Label

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from random import randint

# 한글 폰트 등록 (예: 'NanumGothic' 폰트 사용)
LabelBase.register(name="Noto", fn_regular="NotoSansKR.ttf")

# 기본 폰트 이름을 NanumGothic으로 덮어쓰기
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase

LabelBase.register(name='Roboto', fn_regular='NotoSansKR.ttf')  # 기본 폰트 이름 Roboto 덮어쓰기

from kivy.config import Config

Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '960')
Config.set('graphics', 'resizable', False)  # PC 창 크기 고정 (테스트 편하게)

from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from math import atan2, cos, sin
from math import sin, cos, atan2, radians   # ← radians 추가
from kivy.animation import Animation

from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

# 이 위는 임포트 구역 
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



class SpaceShip(Widget):
    ship_type = NumericProperty(1)
    health = NumericProperty(3)  # 체력 3으로 시작
    invincible_duration = 2  # 무적 시간 (초)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)  # ✨ 크기 고정
        self.size = (50, 50)
        self.pos = (100, 100)  # 초기 위치를 (100,100) 정도로 잡아봅니다.
        self.is_invincible = False

        with self.canvas:
            Color(0, 0.5, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect)

        self.dragging = False
        self.touch_offset = (0, 0)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        #self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dragging = True
            # 터치 위치와 현재 우주선 위치의 차이 저장 (오프셋)
            self.touch_offset = (touch.x - self.x, touch.y - self.y)
            #print(f"Touch down at {touch.pos}, ship pos {self.pos}, touch offset {self.touch_offset}")
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.dragging:
            if not self.parent:
                print("No parent!")
                return super().on_touch_move(touch)

            #print(f"Parent size: {self.parent.width}, {self.parent.height}")

            new_x = touch.x - self.touch_offset[0]
            new_y = touch.y - self.touch_offset[1]

            #print(f"{new_x} , {new_y}")

            max_x = self.parent.width - self.width
            max_y = self.parent.height - self.height
            
            #print(f"Ship size: {self.width}, {self.height}")

            #print(f"{max_x} , {max_y}")

            new_x_clamped = max(0, min(new_x, max_x))
            new_y_clamped = max(0, min(new_y, max_y))
            #new_x_clamped = new_x
            #new_y_clamped = new_y
            

            #print(f"Touch move at {touch.pos}, moving to ({new_x_clamped}, {new_y_clamped})")
            self.pos = (new_x_clamped, new_y_clamped)
            return True
        return super().on_touch_move(touch)


    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            #print(f"Touch up at {touch.pos}")
            return True
        return super().on_touch_up(touch)
    
    def take_damage(self):
        if self.is_invincible:
            return

        self.health -= 1
        print(f"💔 플레이어 체력: {self.health}")

        if self.parent and self.parent.parent:
            self.parent.parent.update_health_ui()  # 체력 UI 갱신

        if self.health <= 0:
            print("💀 게임 오버!")
            if self.parent and self.parent.parent:
                self.parent.parent.game_over()
            return

        self.is_invincible = True
        self.blink_animation()
        Clock.schedule_once(self.end_invincibility, self.invincible_duration)

        # 무적 시작
        self.is_invincible = True
        self.blink_animation()
        Clock.schedule_once(self.end_invincibility, self.invincible_duration)

    def end_invincibility(self, dt):
        self.is_invincible = False
        self.opacity = 1  # 완전하게 보이도록

    def blink_animation(self):
        anim = Animation(opacity=0.2, duration=0.1) + Animation(opacity=1.0, duration=0.1)
        anim.repeat = True
        anim.start(self)

        # 일정 시간 후 애니메이션 멈춤
        def stop_blink(*args):
            anim.cancel(self)
            self.opacity = 1.0
        Clock.schedule_once(stop_blink, self.invincible_duration)
    
class Enemy(Widget):
    enemy_type = NumericProperty(1)  # 1~4번 타입 구분
    speed = NumericProperty(2)

    def __init__(self, **kwargs):
        self.enemy_type = kwargs.pop('enemy_type', 1)
        self.target = kwargs.pop('target', None)  # 추적 대상(SpaceShip)
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (40, 40)

        with self.canvas:
            Color(1, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics)

        # 적 타입 4: 방향 고정용 벡터
        self.dir_x = 0
        self.dir_y = -1  # 기본 아래 방향

        if self.enemy_type in [3, 4] and self.target:
            dx = self.target.center_x - self.center_x
            dy = self.target.center_y - self.center_y
            angle = atan2(dy, dx)
            self.dir_x = cos(angle)
            self.dir_y = sin(angle)

        # 적 타입 2: 사격 후 돌진
        self.has_shot = False
        self.shoot_delay = 0.5
        self.elapsed = 0

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def shoot(self):
        if self.parent and self.parent.parent:  # self.parent: FloatLayout, self.parent.parent: GameScreen
            bullet = EnemyBullet(pos=(self.center_x - 5, self.y))
            self.parent.parent.enemy_bullets.append(bullet)
            self.parent.add_widget(bullet)  # 총알을 layout에 추가
            #print(f"💥 Enemy type {self.enemy_type} at {self.pos} shoots!")

    def move(self, dt=1/60):
        if self.enemy_type == 1:
            # 아래로 돌진
            self.y -= self.speed
            

        elif self.enemy_type == 2:
            # 사격 후 돌진
            self.elapsed += dt
            if not self.has_shot and self.elapsed >= self.shoot_delay:
                self.shoot()
                self.has_shot = True
            elif self.has_shot:
                self.y -= self.speed
            

        elif self.enemy_type == 3:
            # 한 번 방향 고정 후 직진
            self.x += self.dir_x * self.speed
            self.y += self.dir_y * self.speed
           

        elif self.enemy_type == 4:
            # 플레이어 지속 추적
            if self.target:
                dx = self.target.center_x - self.center_x
                dy = self.target.center_y - self.center_y
                angle = atan2(dy, dx)
                self.x += cos(angle) * self.speed
                self.y += sin(angle) * self.speed
           

class EnemyBullet(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 20)
        self.size_hint = (None, None)  # 필수: 크기 고정 안 하면 부모 크기 따라감
        self.pos = kwargs.get('pos', (0, 0))

        with self.canvas:
            Color(1, 1, 0)  # 노란색 총알
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos

    def move(self):
        self.y -= 5  # 아래로 이동
        

class EnemyBullet2(Widget):
    def __init__(self, pos, direction=(0, -1), speed=4, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        self.size_hint = (None, None)
        self.pos = pos
        self.direction = direction
        self.speed = speed
        with self.canvas:
            Color(1, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos

    def move(self):
        dx = self.direction[0] * self.speed
        dy = self.direction[1] * self.speed
        self.x += dx
        self.y += dy


class Boss(Widget):
    boss_type = NumericProperty(1)
    phase = NumericProperty(1)
    pattern_index = NumericProperty(0)
    health = NumericProperty(100)

    def __init__(self,  boss_type=1, game_screen=None, **kwargs):
        #self.boss_type = kwargs.pop('boss_type', 1)  # 인자로 받음
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.size = (120, 120)
        
        self.size_hint = (None, None)  # 필수: 크기 고정 안 하면 부모 크기 따라감
        self.pattern_timer = 0

        with self.canvas:
            Color(0.6, 0, 0.6)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics)

        # 💡 패턴을 보스 타입에 따라 다르게 구성
        if self.boss_type == 1:
            self.patterns = [self.pattern_straight_bullets, self.pattern_circle_bullets]
        elif self.boss_type == 2:
            self.patterns = [self.pattern_spread_bullets, self.pattern_target_player_burst]
        elif self.boss_type == 3:
            self.patterns = [self.pattern_zigzag_spread, self.pattern_circle_bullets]
        else:
            self.patterns = [self.pattern_straight_bullets]
        # 패턴 반복 호출
        #Clock.schedule_interval(self.attack, 1.5)



    def update_graphics(self, *args):
        self.rect.pos = self.pos
        
    def move(self, dt):
        pass  # 현재는 움직이지 않음

    def update(self, dt):
        self.pattern_timer += dt
        if self.pattern_timer > 2:
            self.patterns[self.pattern_index % len(self.patterns)]()
            self.pattern_index += 1
            self.pattern_timer = 0
        self.y -= 0.5  # 보스 이동

    def pattern_straight_bullets(self):
        # 보스 위치 중앙에서 아래로 일직선 총알 여러 발
        for offset in range(-60, 61, 30):  # -60, -30, 0, 30, 60
            bullet = EnemyBullet2(
                pos=(self.center_x + offset, self.y),
                direction=(0, -1)
            )
            self.game_screen.enemy_bullets.append(bullet)
            self.game_screen.layout.add_widget(bullet)

    def pattern_spread_bullets(self):
        # 여러 방향으로 퍼지는 총알
        for angle_deg in range(210, 331, 15):  # 아래 반원 방향
            angle = radians(angle_deg)
            bullet = EnemyBullet2(
                pos=(self.center_x, self.y),
                direction=(cos(angle), sin(angle))
            )
            self.game_screen.enemy_bullets.append(bullet)
            self.game_screen.layout.add_widget(bullet)

    def pattern_target_player(self):
        if not hasattr(self.game_screen, "ship"):
            return
        player = self.game_screen.ship
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        length = max((dx**2 + dy**2)**0.5, 0.1)
        direction = (dx / length, dy / length)

        bullet = EnemyBullet2(
            pos=(self.center_x, self.y),
            direction=direction
        )
        self.game_screen.enemy_bullets.append(bullet)
        self.game_screen.layout.add_widget(bullet)

    def pattern_target_player_burst(self):
        if not hasattr(self.game_screen, "ship"):
            return
        player = self.game_screen.ship
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        length = max((dx**2 + dy**2)**0.5, 0.1)
        direction = (dx / length, dy / length)

        for i in range(5):
            bullet = EnemyBullet2(
                pos=(self.center_x, self.y),
                direction=direction
            )
            self.game_screen.enemy_bullets.append(bullet)
            self.game_screen.layout.add_widget(bullet)
            
    def pattern_circle_bullets(self):
        for angle_deg in range(0, 360, 30):  # 12발
            angle = radians(angle_deg)
            bullet = EnemyBullet2(
                pos=(self.center_x, self.center_y),
                direction=(cos(angle), sin(angle))
            )
            self.game_screen.enemy_bullets.append(bullet)
            self.game_screen.layout.add_widget(bullet)
        
    def pattern_zigzag_spread(self):
        for i in range(-3, 4):  # -3 ~ 3
            dx = i * 0.3
            dy = -1
            length = (dx ** 2 + dy ** 2) ** 0.5
            direction = (dx / length, dy / length)

            bullet = EnemyBullet2(
                pos=(self.center_x, self.y),
                direction=direction
            )
            self.game_screen.enemy_bullets.append(bullet)
            self.game_screen.layout.add_widget(bullet)

    def attack(self, dt):
        for pattern in self.patterns:
            pattern()
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.defeated()

    def defeated(self):
        print("🎉 보스 격파!")
        self.parent.remove_widget(self)




class GameScreen(Screen):
    selected_ship = NumericProperty(1)
    enemies = ListProperty([])
    score = NumericProperty(0)  # 스코어 변수

    def on_enter(self):
        self.clear_widgets()
        self.layout = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.layout)
        self.init_game()
        self.enemy_bullets = []  # on_enter나 init_game에서 초기화
        self.boss = None  # 🛠️ 여기 추가!
        #self.boss = Boss(boss_type=2, game_screen=self)
        Clock.schedule_once(self.spawn_boss, 10)
        
        self.score = 0  # 점수 초기화
        self.score_label = Label(text="Score: 0", size_hint=(None, None),
                                 pos_hint={'right': 0.98, 'top': 0.98},
                                 font_size='20sp', color=(1, 1, 1, 1))
        self.layout.add_widget(self.score_label)
        


    def init_game(self):
        self.ship = SpaceShip(ship_type=self.selected_ship, pos=(self.width / 2 - 25, 50))
        self.layout.add_widget(self.ship)

        # 체력 표시 UI
        self.health_layout = BoxLayout(orientation='horizontal', size_hint=(None, None),
                                       size=(150, 40), pos=(10, self.height - 50))
        self.layout.add_widget(self.health_layout)
        self.update_health_ui()

        self.enemy_spawn_event = Clock.schedule_interval(self.spawn_enemy, 2)
        Clock.schedule_interval(self.update, 1 / 60)

        self.dragging = False
        self.touch_offset = (0, 0)

    def spawn_enemy(self, dt):
        enemy_type = randint(1, 4)
        x = randint(0, int(self.width - 40))
        enemy = Enemy(pos=(x, self.height), enemy_type=enemy_type, target=self.ship)
        self.enemies.append(enemy)
        self.layout.add_widget(enemy)
        #print(f"Spawned enemy type {enemy_type} at {enemy.pos} with size {enemy.size}")

    def update(self, dt):
        for enemy in self.enemies[:]:
            enemy.move(dt)
            if self.ship.collide_widget(enemy):  # 적과 충돌
                print(f"💥 충돌! 게임 오버! 적 종류: {enemy.enemy_type}, 적 위치: {enemy.pos}, 우주선 위치: {self.ship.pos}")
                self.increase_score(10)  # 점수 10점 증가
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.layout.remove_widget(enemy)
                self.ship.take_damage()
                return

            if enemy.y < 0:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.layout.remove_widget(enemy)

        for bullet in self.enemy_bullets[:]:  # 총알과 충돌
            bullet.move()
            if bullet.y < -20:
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                if bullet.parent:
                    self.remove_widget(bullet)
            elif bullet.collide_widget(self.ship):
                print("Ship hit by visible bullet!")
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                if bullet.parent:
                    self.layout.remove_widget(bullet)
                self.ship.take_damage()

        if self.boss and self.boss.y < self.height - 200:
            if self.ship.collide_widget(self.boss):
                print("💥 보스와 충돌! 게임 오버!")
                self.ship.take_damage()

            
                
    def game_over(self):
        Clock.unschedule(self.update)
        Clock.unschedule(self.spawn_enemy)

        if self.boss:
            Clock.unschedule(self.boss.attack)
            # self.layout.remove_widget(self.boss)  # 보스는 남겨둠
            self.boss = None

        # 총알들만 제거
        for bullet in self.enemy_bullets[:]:
            if bullet in self.layout.children:
                self.layout.remove_widget(bullet)
        self.enemy_bullets.clear()

        # 우주선 제거
        if self.ship in self.layout.children:
            self.layout.remove_widget(self.ship)

        self.ship.dragging = False
        self.dragging = False

        print("게임 오버!")


    def on_touch_down(self, touch):
        # 항상 드래그 시작으로 처리
        self.dragging = True
        self.touch_offset = (touch.x - self.ship.x, touch.y - self.ship.y)
        return True

    def on_touch_move(self, touch):
        if self.dragging:
            new_x = touch.x - self.touch_offset[0]
            new_y = touch.y - self.touch_offset[1]

            max_x = self.width - self.ship.width
            max_y = self.height - self.ship.height

            new_x_clamped = max(0, min(new_x, max_x))
            new_y_clamped = max(0, min(new_y, max_y))

            self.ship.pos = (new_x_clamped, new_y_clamped)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.dragging = False
        return True
    
    def shoot(self, pos):
        bullet = EnemyBullet(pos=pos)
        self.enemy_bullets.append(bullet)
        self.layout.add_widget(bullet)

    def spawn_boss(self, dt):
        boss_type = randint(1, 2)
        self.boss = Boss(boss_type=boss_type, game_screen=self)

        # 위치를 먼저 지정한 뒤에 레이아웃에 추가해야 함
        self.boss.center_x = self.width / 2
        self.boss.top = self.height - 20

        self.layout.add_widget(self.boss)
        print(f"🚨 보스 등장! 타입: {boss_type}")

        if hasattr(self, 'enemy_spawn_event'):
            Clock.unschedule(self.enemy_spawn_event)

        self.start_boss()



    def start_boss(self):
        # 보스 패턴 시작 (보스가 이미 생성되고 부모에 추가된 후)
        Clock.schedule_interval(self.boss.attack, 1.5)


    def update_health_ui(self):
        self.health_layout.clear_widgets()
        for i in range(self.ship.health):
            heart = Image(source='images/heart.png', size_hint=(None, None), size=(30, 30))
            self.health_layout.add_widget(heart)


    def increase_score(self, amount):
        self.score += amount
        self.score_label.text = f"Score: {self.score}"




class SpaceApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LobbyScreen(name='lobby'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    SpaceApp().run()

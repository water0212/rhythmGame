import pygame
import random

class Score:
    def __init__(self, music_path, note_data, note_image_path):
        """ 初始化樂譜物件
        music_path: 音樂路徑
        note_data: 音符數據 (包含時間、位置、速度)
        note_image_path: 音符圖片路徑
        """
        self.music_path = music_path
        self.note_data = note_data  # [ (time, position, speed), (time, position, speed), ... ]
        self.note_image = pygame.image.load(note_image_path)  # 載入音符圖片
        self.scaled_image = pygame.transform.scale(self.note_image, (30, 30))

    def load_music(self):
        """ 加載音樂檔案 """
        pygame.mixer.music.load(self.music_path)

    def start_music(self):
        """ 開始播放音樂 """
        pygame.mixer.music.play()
class Note:
    def __init__(self, x, y, speed, image):
        """ 初始化音符物件
        x: x 位置
        y: y 位置 (音符的初始位置)
        speed: 下落速度
        image: 音符圖片
        """
        self.x = x
        self.y = y
        self.speed = speed
        self.image = image

    def update(self):
        """ 更新音符位置 """
        self.y += self.speed  # 音符隨著速度向下移動

    def draw(self, screen):
        """ 在屏幕上繪製音符 """
        screen.blit(self.image, (self.x, self.y))  # 將音符圖片繪製在指定位置
        
class NoteManager:
    """用於管理4個下落音符陣列
        其對應D,F,J,K
    """
    def __init__(self, note_positions, note_images,hit_result_manager,hitCircleEffectManager,comboEffectManager):
        """初始化4個音符陣列，對應D,F,J,K"""
        self.note_columns = {
        'D' :[],
        'F':[],
        'J':[],
        'K':[]
        }
        self.key_mapping = ['D', 'F', 'J', 'K'] #對應0 1 2 3
        self.note_positions = note_positions
        self.note_image = note_images
    def input_note(self, note_time, position, speed):
        """在指定時間點，將音符插入對應的位置
        note_time: 音符出現的時間
        position: 0 (D), 1 (F), 2 (J), 3 (K) -> 決定插入哪一列
        speed: 音符的下落速度
        """
        if position in range(4):  # 位置必須是 0, 1, 2, 3
            column = self.key_mapping[position]
            x_pos = self.note_positions[position]
            new_note = Note(x_pos, -50, speed, self.note_image)
            self.note_columns[column].append(new_note)
    def update_notes(self):
        """更新所有音符的位置，並移除超出螢幕的音符"""
        for column in self.note_columns.values():
            for note in column:
                note.update()
                if note.y > HEIGHT:  # 如果音符超出螢幕範圍，則刪除
                    comboEffectManager.reset_combo()
                    column.remove(note)
    def draw_notes(self, screen):
        for column in self.note_columns.values():
            for note in column:
                note.draw(screen)

    def check_hit(self, key_index,judgment_line):
        score = 0
        if key_index in range(4):
            column = self.key_mapping[key_index]
            if self.note_columns[column]:
                note = self.note_columns[column][0]
                result = judgment_line.check_hit(note.y)  # 判定是否命中
                if result == 'perfect':
                    score += 10  # 完美命中
                    color = (0, 255, 0)
                    comboEffectManager.increase_combo()
                elif result == 'great':
                    score += 5  # 很好命中
                    color = (255, 255, 0)
                    comboEffectManager.increase_combo()
                elif result == 'miss':
                    score += 0  # 錯過
                    color = (255, 0, 0)
                    comboEffectManager.reset_combo()
                else :
                    return -1
                self.note_columns[column].remove(note)
                hit_result_manager.add_result(result, (100, 100), color)
                hitCircleEffectManager.add_effect((self.note_positions[key_index],note.y),YELLOW)
            else:
                print("error")
        return score

class Score_Font:
    """ 用於顯示右上角分數的模塊 """
    def __init__(self, font_size=36, font_color=(255, 255, 255), position=(0, 0)):
        """
        初始化字體模塊
        :param font_size: 字體大小 (默認 36)
        :param font_color: 字體顏色 (默認白色)
        :param position: 顯示位置 (x, y) (默認右上角)
        """
        self.font = pygame.font.Font(None, font_size)  # 字體物件
        self.font_color = font_color  # 字體顏色
        self.position = position  # 顯示位置
        self.score_value = 0  # 分數

    def update_score(self, value):
        """ 更新分數
        :param value: 要增加的分數
        """
        self.score_value += value

    def reset_score(self):
        """ 重置分數 """
        self.score_value = 0

    def draw(self, screen, width):
        """ 在畫面上繪製分數
        :param screen: Pygame 繪製的屏幕
        :param width: 屏幕的寬度，用於右上角對齊
        """
        score_text = self.font.render(f"Score: {self.score_value}", True, self.font_color)
        x = width - score_text.get_width() - 10  # 右上角對齊
        y = self.position[1]  # 使用指定的 y 值
        screen.blit(score_text, (x, y))
 
class JudgmentLine:
    def __init__(self, image_path, y_position = 500, judgment_size = 100, checkRate = 0.4):
        """
        初始化判定線模塊
        :param image_path: 判定線圖片路徑
        :param y_position: 判定線的Y軸位置，預設700
        :param judgment_size: 判定範圍的大小，預設50
        :param checkRate: 判定比率，預設0.4
        """
        self.image = pygame.image.load(image_path)
        self.y_position = y_position
        self.judgment_size = judgment_size  # 判定區域大小
        self.checkRate = checkRate

    def draw(self, screen):
        """ 在屏幕上繪製判定線 """
        #screen.blit(self.image, (0, self.y_position))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, self.y_position + 20, WIDTH, 3))  # 繪製下方文字行

        # 顯示按鍵標籤
        key_labels = ['D', 'F', 'J', 'K']
        font = pygame.font.Font(None, 36)
        for i, label in enumerate(key_labels):
            text = font.render(label, True, (255, 255, 255))
            screen.blit(text, (note_positions[i], self.y_position + 20))

    def check_hit(self, note_y):
        """ 判定音符是否命中，根據音符的位置和判定線範圍
        :param note_y: 音符的當前y坐標
        :param key_index: 音符的按鍵索引 (0: D, 1: F, 2: J, 3: K)
        :return: 判斷結果: 'miss', 'perfect', 'great'
        """
        if note_y >= self.y_position - self.judgment_size*self.checkRate and note_y <= self.y_position + self.judgment_size*self.checkRate:
            return 'perfect'  
        elif note_y >= self.y_position - self.judgment_size and note_y <= self.y_position + self.judgment_size:
            return 'great'
        elif note_y >= self.y_position - self.judgment_size*2 and note_y <= self.y_position + self.judgment_size*2:
            return 'miss' 
        else :
            return 'return'
class HitResult:
    """ 單一的命中結果顯示（例如：Perfect、Great、Miss） """
    def __init__(self, text, position, font, color, lifespan=1000, float_speed=-0.2):
        """
        :param text: 顯示的文字內容 (例如：'Perfect', 'Great', 'Miss')
        :param position: 初始位置 (x, y)
        :param font: 字體物件
        :param color: 文字的顏色
        :param lifespan: 文字持續時間（毫秒）
        :param float_speed: 每幀向上浮動的速度
        """
        self.text = text
        self.x, self.y = position
        self.font = font
        self.color = color
        self.alpha = 255  # 透明度 (從 255 開始逐漸減少)
        self.lifespan = lifespan  # 持續時間 (毫秒)
        self.float_speed = float_speed  # 文字的浮動速度
        self.creation_time = pygame.time.get_ticks()  # 創建時間

    def update(self):
        """ 更新文字的浮動和透明度 """
        self.y += self.float_speed  # 文字位置上浮
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifespan:
            self.alpha = 0  # 完全透明
        else:
            self.alpha = max(255 - int(255 * (elapsed_time / self.lifespan)), 0)  # 計算透明度

    def draw(self, screen):
        """ 在屏幕上繪製文字，並應用透明效果 """
        if self.alpha > 0:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(self.alpha)  # 設置透明度
            screen.blit(text_surface, (self.x, self.y))            
class HitResultManager:
    """ 管理多個命中結果的效果 """
    def __init__(self, font):
        """
        :param font: 字體物件，用於繪製命中效果的字體
        """
        self.results = []  # 儲存所有的 HitResult 物件
        self.font = font

    def add_result(self, text, position, color):
        """ 新增一個新的命中結果 """
        new_result = HitResult(text, position, self.font, color)
        self.results.append(new_result)

    def update(self):
        """ 更新所有的命中結果，並移除已經結束的效果 """
        for result in self.results[:]:
            result.update()
            if result.alpha <= 0:  # 如果透明度為 0，則刪除該效果
                self.results.remove(result)

    def draw(self, screen):
        """ 繪製所有的命中結果 """
        for result in self.results:
            result.draw(screen)
class HitCircleEffect:
    def __init__(self, position, color, lifetime=500):
        """ 
        position: 中心位置 (x, y)
        color: 圓形顏色
        lifetime: 存在的時間 (毫秒)
        """
        self.position = position
        self.color = color
        self.lifetime = lifetime
        self.start_time = pygame.time.get_ticks()

    def update(self):
        """ 更新效果的存活時間 """
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.lifetime:
            return False  # 告知外部，效果已結束
        return True

    def draw(self, screen):
        """ 繪製圓環效果 """
        elapsed = pygame.time.get_ticks() - self.start_time
        radius_outer = int(20 + (30 * (elapsed / self.lifetime)))  # 外圓的半徑隨時間變大
        radius_inner = int(radius_outer * 0.8)  # 內圓的半徑 (可調整大小)
        alpha = max(0, 255 - int(255 * (elapsed / self.lifetime)))  # 透明度隨時間變小
        # 1. 創建一個透明的 Surface，準備在上面畫出圓環
        surface = pygame.Surface((radius_outer * 2, radius_outer * 2), pygame.SRCALPHA)

        # 2. 畫出外圓
        pygame.draw.circle(surface, self.color + (alpha,), (radius_outer, radius_outer), radius_outer)
        
        # 3. 畫出內圓，這部分會使中間變成透明
        pygame.draw.circle(surface, (0, 0, 0, 0), (radius_outer, radius_outer), radius_inner)

        # 4. 把這個圓環繪製到屏幕上
        screen.blit(surface, (self.position[0] - radius_outer, self.position[1] - radius_outer))
class HitCircleEffectManager:
    """ 用於管理多個命中擴散效果的管理器 """
    def __init__(self):
        """ 初始化管理器，創建一個用於存放圓形效果的列表 """
        self.effects = []  # 存放 HitCircleEffect 物件的列表

    def add_effect(self, position, color):
        """ 新增一個圓形擴散效果
        :param position: 命中效果的中心位置 (x, y)
        :param color: 圓形的顏色 (RGB)
        """
        new_effect = HitCircleEffect(position, color)
        self.effects.append(new_effect)

    def update(self):
        """ 更新所有的圓形效果，並移除已經過期的效果 """
        for effect in self.effects[:]:
            if not effect.update():  # 如果效果已過期
                self.effects.remove(effect)

    def draw(self, screen):
        """ 繪製所有的圓形擴散效果 """
        for effect in self.effects:
            effect.draw(screen)
class ComboEffectManager:
    def __init__(self,font):
        """
        :param font: 字體物件，用於繪製命中效果的字體
        """
        self.combo = 0
        self.font = font
    def reset_combo(self):
        """ 重置連擊 """
        self.combo = 0
    def increase_combo(self):
        """ 連擊數字加1 """
        self.combo += 1
    def __drawColor(self):
        if self.combo <= 20:
            return WHITE
        elif self.combo <=100:
            return YELLOW
        else :
            return RED
    def draw(self, screen):
        """ 在左上角顯示連擊數字 """
        combo_text = f"Combo: {self.combo}"
        text_surface = self.font.render(combo_text, True,self.__drawColor())
        screen.blit(text_surface, (10, 10))
class SoundManager:
    def __init__(self,sound_file):
        self.last_played = 0
        pygame.mixer.init()
        self.sound = sound_file

    def play(self): #如果同時按下則只會有一次聲音
        current_time = pygame.time.get_ticks()
        if current_time - self.last_played >= 100:
            self.sound.play()
            self.last_played = current_time
        
#------------------------------------------------------------------
# 初始化 Pygame

pygame.init()

# 屏幕大小
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("下落式節奏遊戲")
#字體
font = pygame.font.Font(None, 48)
# 顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
# 時鐘控制
clock = pygame.time.Clock()
FPS = 120
# 創建樂譜
note_data = [
    (i * 200, 0, 5)  # 每秒一個音符，位置 0（D），速度 5
    for i in range(180)  # 持續 30 秒
]
# 樂譜初始化
score = Score('pythonProject/test.mp3', note_data, 'pythonProject/note.png')
score.load_music()
score.start_music()
# 按鍵對應的 X 位置
note_positions = {
    0: 180,  # D
    1: 360,  # F
    2: 540,  # J
    3: 720   # K
}
####----------------------------------------------初始化-----------------------
# 遊戲變數
notes = []
note_width = 100  # 每個音符的寬度
# 創建 HitResultManager
hit_result_manager = HitResultManager(font)
#HitCircleEffect創建
hitCircleEffectManager = HitCircleEffectManager()
#ComboEffectManager創建
comboEffectManager = ComboEffectManager(font)
# 創建判定線
judgment_line = JudgmentLine('pythonProject/note.png')
#note_manager創建
note_manager = NoteManager(note_positions, score.scaled_image,hit_result_manager,hitCircleEffectManager,comboEffectManager) 
# 分數
score_value = 0
#score_font創建
score_font = Score_Font(font_size=36, font_color=WHITE, position=(WIDTH - 10, 10))
# 按鍵音效
hit_sounds = pygame.mixer.Sound('pythonProject/pop.mp3')
# SoundManager創建
soundManager = SoundManager(hit_sounds)
####----------------------------------------------初始化-----------------------
# 主遊戲循環
running = True
start_time = pygame.time.get_ticks()  # 獲取遊戲開始的時間

while running:
    screen.fill(BLACK)

    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 玩家鍵盤判定 (D, F, J, K)
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]:
                i = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k].index(event.key)
                get_value = note_manager.check_hit(i, judgment_line)
                soundManager.play() #播放音效
                if get_value != -1: #如果是有效鍵位
                    score_value += get_value
                    score_font.update_score(get_value)
    # 獲取當前時間
    current_time = pygame.mixer.music.get_pos()

    # 音符生成
    for note_info in score.note_data:
        note_time, position, speed = note_info
        if current_time >= note_time:  # 如果當前時間達到了音符的出現時間
            note_manager.input_note(note_time, position, speed)
            score.note_data.remove(note_info)  # 移除已經生成的音符

    # 音符更新與繪製
    note_manager.update_notes()
    note_manager.draw_notes(screen)


    # 繪製判定線
    judgment_line.draw(screen)
    # 顯示擊中結果
    hit_result_manager.update()
    hit_result_manager.draw(screen)
    # 顯示擊中反饋
    hitCircleEffectManager.update()
    hitCircleEffectManager.draw(screen)
    # 顯示combo數
    comboEffectManager.draw(screen)
    # 顯示分數
    score_font.draw(screen, WIDTH)
    # 更新屏幕
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

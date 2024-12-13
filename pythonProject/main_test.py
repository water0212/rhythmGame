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
note_data=[(584.7968578338623, 2, 5),
(1013.7962818145752, 2, 5),
(1462.5794410705566, 2, 5),
(1861.9484424591064, 2, 5),
(2282.4248790740967, 3, 5),
(2696.39892578125, 3, 5),
(3137.8597736358643, 3, 5),
(3557.5613498687744, 3, 5),
(3940.9253120422363, 1, 5),
(4405.67512512207, 1, 5),
(4815.329265594482, 1, 5),
(5308.16216468811, 1, 5),
(5734.184694290161, 0, 5),
(6109.8451137542725, 0, 5),
(6551.516962051392, 0, 5),
(6988.080930709839, 0, 5),
(7438.8951778411865, 3, 5),
(7872.033786773682, 2, 5),
(8283.629131317139, 1, 5),
(8784.053993225098, 0, 5),
(9199.25971031189, 3, 5),
(9587.548446655273, 2, 5),
(10014.039707183838, 1, 5),
(10426.412534713745, 0, 5),
(10870.583486557007, 2, 5),
(11301.343154907227, 3, 5),
(11734.194707870483, 1, 5),
(12136.371803283691, 0, 5),
(12581.668329238892, 2, 5),
(12993.143272399902, 1, 5),
(13492.441844940186, 3, 5),
(13879.791927337646, 0, 5),
(14354.543399810791, 0, 5),
(14356.89754486084, 1, 5),
(14360.254716873169, 3, 5),
(14361.769390106201, 2, 5),
(14743.422937393188, 2, 5),
(15190.386009216309, 3, 5),
(15607.86361694336, 0, 5),
(16013.825130462646, 2, 5),
(16444.763135910034, 3, 5),
(16892.05403327942, 1, 5),
(17280.59024810791, 0, 5),
(17811.43469810486, 2, 5),
(18175.953102111816, 3, 5),
(18556.06575012207, 0, 5),
(18999.883604049683, 1, 5),
(19432.68485069275, 3, 5),
(19844.806385040283, 2, 5),
(20278.65309715271, 1, 5),
(20689.73250389099, 0, 5),
(21138.623666763306, 2, 5),
(21568.943691253662, 2, 5),
(22001.65123939514, 1, 5),
(22442.605209350586, 1, 5),
(22876.03850364685, 3, 5),
(23301.449489593506, 3, 5),
(23686.56177520752, 0, 5),
(24128.770065307617, 0, 5),
(24560.26930809021, 3, 5),
(24959.828567504883, 2, 5),
(25426.492881774902, 1, 5),
(25826.392364501953, 0, 5),
(26275.44493675232, 3, 5),
(26684.10129547119, 2, 5),
(27145.781469345093, 1, 5),
(27519.305658340454, 0, 5),
(28036.8923664093, 0, 5),
(28039.63966369629, 3, 5),
(28046.925973892212, 2, 5),
(29644.366455078125, 2, 5),
(30303.705406188965, 3, 5),
(30971.52442932129, 2, 5),
(31460.32042503357, 1, 5),
(31909.590911865234, 0, 5),
(32306.497526168823, 3, 5),
(32721.145820617676, 2, 5),
(33177.55169868469, 1, 5),
(33775.56891441345, 3, 5),
(34423.979473114014, 2, 5),
(34864.84785079956, 0, 5),
(35487.354707717896, 3, 5),
(36118.20192337036, 2, 5),
(36587.93206214905, 3, 5),
(37213.142585754395, 2, 5),
(37854.964208602905, 3, 5),
(38302.386474609375, 2, 5),
(38722.28665351868, 3, 5),
(39150.6151676178, 2, 5),
(39578.7796497345, 1, 5),
(40007.693004608154, 0, 5),
(40638.70282173157, 3, 5),
(41251.97525024414, 2, 5),
(41709.70959663391, 3, 5),
(42325.19454956055, 2, 5),
(42967.988443374634, 1, 5),
(43449.27997589111, 0, 5),
(44081.33358955383, 3, 5),
(44678.49202156067, 2, 5),
(45186.0360622406, 3, 5),
(45601.917934417725, 2, 5),
(46018.49002838135, 1, 5),
(46471.101236343384, 0, 5),
(46883.8960647583, 2, 5),
(47327.32219696045, 1, 5),
(47529.91719245911, 3, 5),
(48175.3692150116, 0, 5),
(48638.92407417297, 2, 5),
(49055.84354400635, 3, 5),
(49228.18465232849, 1, 5),
(49839.77265357971, 0, 5),
(50303.15728187561, 2, 5),
(50763.57765197754, 3, 5),
(51542.764377593994, 2, 5),
(52000.225257873535, 1, 5),
(52439.81308937073, 0, 5),
(53338.30256462097, 3, 5),
(53720.74933052063, 2, 5),
(54141.81275367737, 3, 5),
(54360.48455238342, 2, 5),
(54796.2016582489, 3, 5),
(54998.22778701782, 2, 5),
(55460.91814041138, 0, 5),
(55886.52129173279, 1, 5),
(56095.84040641785, 0, 5),
(56492.837142944336, 1, 5),
(56685.652685165405, 0, 5),
(57115.592670440674, 3, 5),
(57565.23342132568, 2, 5),
(57770.21903991699, 1, 5),
(58217.9557800293, 0, 5),
(58436.69099807739, 3, 5),
(58877.8130531311, 2, 5),
(59294.741344451904, 1, 5),
(59513.50231170654, 3, 5),
(59753.84016036987, 0, 5),
(59964.172077178955, 2, 5),
(60155.5242061615, 1, 5),
(60587.43305206299, 3, 5),
(61013.995361328125, 2, 5),
(61229.76107597351, 2, 5),
(61667.51570701599, 1, 5),
(61890.58847427368, 1, 5),
(62318.616819381714, 0, 5),
(62734.687519073486, 3, 5),
(62945.330810546875, 3, 5),
(63359.91735458374, 2, 5),
(63600.203466415405, 2, 5),
(64042.18120574951, 3, 5),
(64444.59099769592, 1, 5),
(64666.83979034424, 1, 5),
(65088.59844207764, 2, 5),
(65320.06878852844, 2, 5),
(65771.861743927, 0, 5),
(66200.03671646118, 0, 5),
(66412.55278587341, 0, 5),
(66635.10031700134, 0, 5),
(66833.12005996704, 0, 5),
(67052.34761238098, 0, 5),
(67473.8025188446, 2, 5),
(67885.02497673035, 3, 5),
(68092.54021644592, 3, 5),
(68525.66547393799, 1, 5),
(68746.85640335083, 1, 5),
(69186.44399642944, 2, 5),
(69585.66446304321, 3, 5),
(69820.64576148987, 3, 5),
(70242.38271713257, 2, 5),
(70485.20250320435, 2, 5),
(70899.11170005798, 3, 5),
(71293.07527542114, 1, 5),
(71511.44213676453, 1, 5),
(71950.84924697876, 2, 5),
(72204.36806678772, 1, 5),
(72419.05303001404, 3, 5),
(72624.08514022827, 0, 5),
(73060.40425300598, 2, 5),
(73268.55154037476, 2, 5),
(73494.91686820984, 3, 5),
(73682.48362541199, 3, 5),
(73926.1426448822, 1, 5),
(74297.61095046997, 0, 5),
(74717.84682273865, 3, 5),
(74944.8558807373, 2, 5),
(75412.74828910828, 1, 5),
(75624.70955848694, 0, 5),
(75830.43999671936, 2, 5),
(76072.28465080261, 1, 5),
(76494.43955421448, 3, 5),
(76698.6002445221, 3, 5),
(76912.70680427551, 2, 5),
(77103.16963195801, 0, 5),
(77314.177942276, 1, 5),
(77548.73509407043, 3, 5),
(77742.66119003296, 2, 5),
(78204.93431091309, 2, 5),
(78426.29165649414, 2, 5),
(78826.89423561096, 3, 5),
(79033.90760421753, 3, 5),
(79232.40633010864, 3, 5),
(79447.79057502747, 1, 5),
(79894.55146789551, 2, 5),
(80117.91939735413, 2, 5),
(80340.68818092346, 0, 5),
(80537.49985694885, 0, 5),
(80773.61435890198, 1, 5),
(81187.71452903748, 3, 5),
(81596.22712135315, 2, 5),
(81819.44508552551, 1, 5),
(82232.87672996521, 0, 5),
(82458.34488868713, 2, 5),
(82683.73079299927, 2, 5),
(82926.09281539917, 1, 5),
(83128.53164672852, 3, 5),
(83342.51470565796, 0, 5),
(83556.23216629028, 2, 5),
(83802.65731811523, 1, 5),
(84009.82613563538, 3, 5),
(84207.08770751953, 0, 5),
(84393.59683990479, 2, 5),
(84620.60422897339, 1, 5),
(85023.44913482666, 3, 5),
(85238.46502304077, 0, 5),
(85476.63350105286, 2, 5),
(86337.63117790222, 3, 5),
(86537.29028701782, 3, 5),
(86976.72266960144, 0, 5),
(87180.91268539429, 0, 5),
(88019.73099708557, 2, 5),
(88237.9056930542, 2, 5),
(88704.77766990662, 1, 5),
(88887.10446357727, 1, 5),
(89744.28362846375, 3, 5),
(89959.96255874634, 3, 5),
(90401.34592056274, 0, 5),
(90599.58691596985, 0, 5),
(91039.51926231384, 2, 5),
(91489.27326202393, 1, 5),
(91676.49121284485, 1, 5),
(92129.42309379578, 3, 5),
(92335.57124137878, 3, 5),
(93160.83068847656, 2, 5),
(93375.68755149841, 3, 5),
(93840.82527160645, 1, 5),
(94042.69618988037, 0, 5),
(94891.67423248291, 2, 5),
(95095.93577384949, 3, 5),
(95540.99531173706, 1, 5),
(95756.82182312012, 0, 5),
(96608.3878993988, 3, 5),
(96806.91165924072, 2, 5),
(97272.71003723145, 0, 5),
(97467.42243766785, 1, 5),
(97695.60904502869, 2, 5),
(97921.57382965088, 0, 5),
(98107.18388557434, 3, 5),
(98350.91705322266, 1, 5),
(98738.987159729, 2, 5),
(98931.24194145203, 0, 5),
(99164.61486816406, 3, 5),
(100069.15636062622, 2, 5),
(100295.78776359558, 0, 5),
(100495.13120651245, 3, 5),
(100710.85209846497, 1, 5),
(100918.19281578064, 2, 5),
(101793.76740455627, 3, 5),
(101984.45339202881, 3, 5),
(102209.11569595337, 2, 5),
(102418.24049949646, 2, 5),
(102646.48885726929, 1, 5),
(103478.58209609985, 0, 5),
(103689.18890953064, 0, 5),
(103918.2834148407, 1, 5),
(104110.16674041748, 1, 5),
(104344.90795135498, 2, 5),
(104555.62062263489, 2, 5),
(104761.31196022034, 3, 5),
(104958.01515579224, 3, 5),
(105185.29815673828, 2, 5),
(105743.47896575928, 3, 5),
(106447.20430374146, 2, 5),
(106873.4561920166, 3, 5),
(107492.18792915344, 0, 5),
(108193.10660362244, 1, 5),
(108641.71619415283, 2, 5),
(109258.16698074341, 3, 5),
(109889.14151191711, 2, 5),
(110330.699634552, 2, 5),
(110561.62257194519, 1, 5),
(110798.43730926514, 3, 5),
(111006.15091323853, 0, 5),
(111213.55648040771, 2, 5),
(111422.99766540527, 1, 5),
(111627.11091041565, 3, 5),
(111807.42163658142, 3, 5),
(112052.73361206055, 2, 5),
(112484.3873500824, 2, 5),
(112702.58946418762, 0, 5),
(112913.53888511658, 3, 5),
(113344.8245048523, 2, 5),
(113798.12426567078, 0, 5),
(113997.31130599976, 0, 5),
(114216.22176170349, 3, 5),
(114418.01447868347, 1, 5),
(114634.03458595276, 2, 5),
(115080.7590007782, 3, 5),
(115459.91916656494, 0, 5),
(115665.51752090454, 0, 5),
(115912.66603469849, 2, 5),
(116124.56889152527, 2, 5),
(116330.58280944824, 1, 5),
(116748.85339736938, 3, 5),
(117207.96031951904, 0, 5),
(117401.40719413757, 0, 5),
(117628.28679084778, 3, 5),
(117835.98036766052, 3, 5),
(118048.0417728424, 1, 5),
(118493.56098175049, 2, 5),
(118891.03646278381, 0, 5),
(119337.70389556885, 3, 5),
(119532.24368095398, 3, 5),
(119774.35870170593, 2, 5),
(120196.9289302826, 1, 5),
(120613.77568244934, 3, 5),
(120840.43283462524, 3, 5),
(121084.38034057617, 2, 5),
(121260.42194366455, 0, 5),
(121486.02123260498, 3, 5),
(121948.60525131226, 2, 5),
(122340.50674438477, 0, 5),
(122555.25631904602, 0, 5),
(122766.46990776062, 2, 5),
(122979.25992012024, 2, 5),
(123228.24854850769, 1, 5),
(123408.28485488892, 3, 5),
(123615.01688957214, 0, 5),
(124070.89276313782, 2, 5),
(124292.37909317017, 2, 5),
(124489.21747207642, 1, 5),
(124699.87983703613, 1, 5),
(124909.20133590698, 3, 5),
(125111.85903549194, 0, 5),
(125337.3598575592, 2, 5),
(125532.56554603577, 1, 5),
(125755.88626861572, 3, 5),
(126393.11833381653, 2, 5),
(127031.96902275085, 3, 5),
(127468.82696151733, 2, 5),
(127943.97373199463, 1, 5),
(128345.18976211548, 0, 5),
(128788.97852897644, 1, 5),
(129192.23375320435, 3, 5),
(129653.62615585327, 2, 5),
(130063.39354515076, 0, 5),
(130472.92490005493, 1, 5),
(130911.21644973755, 3, 5),
(131337.41040229797, 2, 5),
(131750.2223968506, 1, 5),
(132207.417678833, 0, 5),
(132630.14216423035, 2, 5),
(133058.69693756104, 3, 5),
(133469.53077316284, 1, 5),
(133919.80786323547, 0, 5),
(134335.1180076599, 2, 5),
(134744.25287246704, 3, 5),
(135202.0432472229, 1, 5),
(135615.8480167389, 0, 5),
(136056.45866394043, 2, 5),
(136484.25455093384, 1, 5),
(136920.78251838684, 3, 5),
(137325.52332878113, 0, 5),
(137751.64670944214, 2, 5),
(137992.69695281982, 1, 5),
(138204.01258468628, 3, 5),
(138419.90633010864, 0, 5),
(138614.2632484436, 2, 5),
(138838.35978507996, 1, 5),
(139071.2179660797, 3, 5),
(139262.8116130829, 0, 5)
]
# 樂譜初始化
score = Score('test.mp3', note_data, 'note.png')
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
judgment_line = JudgmentLine('note.png')
#note_manager創建
note_manager = NoteManager(note_positions, score.scaled_image,hit_result_manager,hitCircleEffectManager,comboEffectManager) 
# 分數
score_value = 0
#score_font創建
score_font = Score_Font(font_size=36, font_color=WHITE, position=(WIDTH - 10, 10))
# 按鍵音效
hit_sounds = pygame.mixer.Sound('pop.mp3')
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

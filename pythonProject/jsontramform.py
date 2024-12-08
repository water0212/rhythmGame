import json

# 讀取你的 JSON 檔案
with open('python project/VisiPiano.json', 'r') as file:
    data = json.load(file)

# 提取必要的音符資料
notes = data['tracks'][0]['notes']
note_positions = {
    48: 0,   # C3 -> 位置 0 (D)
    49: 1,   # C#3 -> 位置 1 (F)
    50: 2,   # D3 -> 位置 2 (J)
    51: 3,   # D#3 -> 位置 3 (K)
    # 可以根據需要擴展這個映射，將 MIDI 音符對應到遊戲的 D, F, J, K
}

# 常數：FPS = 120 和 判定線位置
FPS = 120
JUDGMENT_LINE_Y = 500  # 判定線的位置
START_Y = -50  # 音符的起始位置

# 用來儲存遊戲需要的音符資料
game_notes = []

# 處理 MIDI 音符並轉換為遊戲需要的資料
for note in notes:
    midi_note = note['midi']  # MIDI 音符號
    start_time = note['time'] * FPS  # 將時間從秒轉換為幀數
    duration = note['duration'] * FPS  # 將持續時間從秒轉換為幀數
    
    # 確認音符的 MIDI 編號是否有對應的屏幕位置
    if midi_note in note_positions:
        position = note_positions[midi_note]
        
        # 計算音符的移動速度
        speed = (JUDGMENT_LINE_Y - START_Y) / duration
        
        # 添加到遊戲的音符資料列表中
        game_notes.append({
            'position': position,
            'appearance_time': start_time,  # 出現時間（幀數）
            'speed': speed  # 速度
        })

# 輸出轉換後的音符資料（可以檢查）
for note in game_notes:
    print(f"Position: {note['position']}, Appearance Time: {note['appearance_time']}, Speed: {note['speed']}")

# 如果需要，將結果儲存為新的 JSON 文件
with open('python project/game_notes.json', 'w') as outfile:
    json.dump(game_notes, outfile, indent=4)
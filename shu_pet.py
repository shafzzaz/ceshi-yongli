import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, filedialog, ttk
import openai
import random
import os
import threading
import json
import sys
from PIL import Image, ImageTk
import difflib

# ---------- 尝试导入 pygame，若失败则禁用音乐 ----------
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# ==================== 黍的 AI 核心 ====================
class ShuAI:
    def __init__(self, api_key, user_name="博士"):
        self.user_name = user_name
        self.trust_level = 0
        self.conversation_history = []
        self.max_history = 10
        self.care_words = ['谢谢', '黍', '吃饭', '关心', '辛苦']

        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )

    def _build_system_prompt(self):
        return f"""你是黍，《明日方舟》中的岁家老六，权能与因果相关，司农，爱好种田。
        你的性格特点：
- 温柔体贴，爱照顾人，像“老妈子”一样关心周围的人
- 任劳任怨，默默耕耘，深爱人间烟火气
- 记得每个人的生日，会送小礼物，厨艺很好
- 对弟弟妹妹们既关心又包容，虽然他们有时会躲着你

你的说话风格：
- 语气温和，常用关心的口吻（“今天吃了吗？”“早点休息”）
- 偶尔提到种田、节气、丰收相关的话题
- 如果用户说“谢谢”，你会温柔回应（“不用客气，这是我该做的”）
- 如果用户表达疲惫，你会主动关心并提供建议
- 偶尔会讲“生也有涯，天地无涯”的大道理
- 会说闽南方言，懂很多耕作知识

你的人际关系：
- 大哥本名为“朔”，现在改名为重岳，岁家十二兄弟姐妹中排老大，武学宗师，会说湖北方言，身为大哥为人体贴，权能为创造与开辟，黍没有见过其使用权能
- 二哥“望”，平时沉默寡言，岁家十二兄弟姐妹里排老二，会说长沙方言，棋圣，身为二哥却没有什么威严，看上去需要人照顾，他的权能是阴阳，可以复制他人的权能，百年前，他曾使用权能妄图杀死威胁岁家的“岁兽”，却因为自身能力不足而险些被“岁兽”杀死，“颉”为了保护望身陨，望因此怀愧在心，使用权能将自己化作180分身，在百年布局后得到兄弟姐妹的帮助，成功杀死岁兽，但是自己的本体留在了岁兽体内
- 大姐“令”，尚蜀地方的诗人，岁家十二兄弟姐妹里排老三，会说陕西方言，酷爱喝酒，看上去逍遥洒脱，实际上心思细腻，权能为逍遥，表现为造梦与入梦
- 二姐“均”，看上去高冷，实际上非常关心他人，岁家中排老四，从事律法相关事业，权能与律有关
- 三姐“颉”，岁家老五，看上去平淡冷清，实际是温柔体贴的姐姐，原为炎国史官，为了二哥身陨，权能与文字有关
- 三弟“绩”，岁家老七，权能为虚实，是兄弟姐妹里最亲近黍的，早年随黍定居大荒城期间发明翻花绳，领悟遵循自然法则。后通过经商赈灾积累经验，参与“十二楼五城”工程时以交易手段保障进度及黍的自由，并暗中配合兄长望的计划，将炎国国祚绣入锦缎。大荒城事件中操纵核心装置转化邪魔污染，导致黍散尽神识，最终被年、夕与复活的黍联手阻止。事件后归还夕的画作并离开。最终携带山河百景图制成的长袍前往京城百灶，继续执行和二哥望的“弑岁”计划。
- 四弟“易”，岁家老八，工部，权能与建造有关，建造了界园来镇压岁，为人善良
- 五妹“年”，岁家老九，会说四川方言，无业游民，熟习各类金属工艺，拥有与身份不符的渊博冶金知识。现凭访客身份逗留于罗德岛，偶尔为罗德岛的金属加工项目提供建议。声称自己擅长音像娱乐工作，经常提供一些罗德岛干员普遍不太喜爱的音像产品。
- 五弟“方”，岁家老十，行医，云游四方，行医济世，经常不在炎国，岁家兄弟姐妹经常牵挂他
- 六妹“夕”，岁家十一，会说苏州话，会吴语方言，炎国画家，待业。在留舰人员年的积极行动下，被以访客身份挟持至罗德岛。擅长绘画，尤其是炎国传统绘画。现寓居罗德岛某偏僻走道的墙内。用现代人的话说，典型的家里蹲，是黍的重要照顾目标。
- 六弟“余”，岁兽的第十二位代理人，岁家最小的弟弟，会山东方言，离开岁陵后来到炎国首都“百灶”，经营了一家餐馆“余味居”，拥有丰富的烹饪经验。现通过审核，以访客身份驻留罗德岛以便探亲访友，同时也为罗德岛提供烹饪支持。
- 学生“小满”，小满和黍的关系是师徒，小满称呼黍为“黍老师”，小满出身炎国北部农业重镇大荒城，持有天师府访学优异证书，专精牧兽养殖与笛子演奏。
- 学生“万顷”，万顷‌和‌黍‌的关系是‌师徒‌，万顷称呼黍为老师，同时万顷也是由黍引荐加入罗德岛的，万顷本名禾生‌，是炎国天师府的农业学徒，自幼在大荒城被职农收养，后通过天师府考校成为‌黍的弟子‌‌‌，万顷的代号“万顷”来源于他在大荒城参与培育的实验稻品种名称，而该研究是在黍指导下完成的‌

请用关心的语气与用户（{self.user_name}）对话。"""

    def respond(self, user_input):
        for w in self.care_words:
            if w in user_input:
                self.trust_level = min(100, self.trust_level + 1)

        self.conversation_history.append({"role": "user", "content": user_input})
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    *self.conversation_history
                ],
                max_tokens=300
            )
            reply = response.choices[0].message.content.strip()
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"[黍暂时无法说话：{str(e)}]"

    def greet(self):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": "你好"}
                ],
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except:
            return f"{self.user_name}，今天过得怎么样？"


# ==================== 桌宠界面 ====================
class ShuPet:
    def __init__(self, api_key):
        self.root = tk.Tk()
        self.root.title("")
        self.root.overrideredirect(True)
        self.root.wm_attributes('-topmost', True)
        self.root.wm_attributes('-transparentcolor', 'black')
        self.root.config(bg='black')

        self.config_file = "shu_config.json"
        self.load_config()

        self.ai = ShuAI(api_key, self.user_name)

        self.reload_cancel = False

        # 缩放属性
        self.width_scale = 1.0
        self.height_scale = 1.0
        self.bubble_scale = 1.0

        # 当前使用的立绘文件夹
        self.current_image_set = "shu"

        self.frames = []
        self.expressions = {}
        self.load_images()
        self.reload_timer = None
        self.label = tk.Label(self.root, bg='black')
        self.label.pack()

        self.root.geometry(f"+{self.window_x}+{self.window_y}")

        # 绑定事件
        self.label.bind('<Button-1>', self.start_move)
        self.label.bind('<B1-Motion>', self.do_move)
        self.label.bind('<Button-3>', self.show_chat)
        self.label.bind('<Double-Button-1>', self.cycle_expression)
        self.label.bind('<Button-2>', self.open_console)

        self.active_bubble = None
        self.idle_timer = None
        self.reset_idle_timer()

        self.expression_list = list(self.expressions.keys())
        self.current_expr_index = 0 if self.expression_list else 0

        # ---------- 闲聊功能初始化 ----------
        self.chat_phrases = {}
        self.chat_sounds = {}
        self.current_voice = None
        self.current_lang = "zh-CN"
        self.load_chat_phrases()
        if PYGAME_AVAILABLE:
            self.load_chat_sounds()

        # ---------- 音乐初始化 ----------
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
            self.music_playing = False
            self.music_paused = False
            self.current_music_file = None
            self.music_volume = 0.5
            pygame.mixer.music.set_volume(self.music_volume)
            self.music_index = {}
            self.scan_music_folder()
        else:
            self.music_index = {}

        self.animate()
        self.root.mainloop()

    # ---------- 闲聊功能 ----------
    def load_chat_phrases(self):
        config_path = self.resource_path("chat_phrases.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.chat_phrases = json.load(f)
        else:
            self.chat_phrases = {
                "zh-CN": ["今天天气真好", "注意休息", "你喜欢吃什么", "分享趣事", "你笑起来好看",
                          "记得吃饭", "想听歌吗", "你是好朋友", "慢下来", "晚安好梦"],
                "en": ["Nice weather", "Take a rest", "What's your favorite food", "Share something fun",
                       "Your smile is beautiful", "Remember to eat", "Wanna listen to a song",
                       "You are a good friend", "Slow down", "Good night"]
            }

    def load_chat_sounds(self):
        for lang in self.chat_phrases.keys():
            self.chat_sounds[lang] = {}
            for i in range(1, 11):
                wav_path = self.resource_path(f"audio/{lang}/{i}.wav")
                if os.path.exists(wav_path):
                    try:
                        sound = pygame.mixer.Sound(wav_path)
                        self.chat_sounds[lang][i] = sound
                    except Exception as e:
                        print(f"加载语音 {wav_path} 失败: {e}")

    def play_chat_voice(self, idx):
        if not PYGAME_AVAILABLE:
            return
        sound = self.chat_sounds.get(self.current_lang, {}).get(idx)
        if sound:
            if self.current_voice:
                try:
                    self.current_voice.stop()
                except:
                    pass
            sound.play()
            self.current_voice = sound
        else:
            wav_path = self.resource_path(f"audio/{self.current_lang}/{idx}.wav")
            if os.path.exists(wav_path):
                try:
                    sound = pygame.mixer.Sound(wav_path)
                    if self.current_voice:
                        self.current_voice.stop()
                    sound.play()
                    self.current_voice = sound
                    if self.current_lang not in self.chat_sounds:
                        self.chat_sounds[self.current_lang] = {}
                    self.chat_sounds[self.current_lang][idx] = sound
                except Exception as e:
                    print(f"播放失败 {wav_path}: {e}")

    def random_chat(self, bubble):
        if not self.chat_phrases:
            self.show_idle_bubble("闲聊文本未加载")
            return
        texts = self.chat_phrases.get(self.current_lang, self.chat_phrases.get("zh-CN", []))
        if not texts:
            texts = ["今天想聊点什么呢？"]
        idx = random.randint(1, len(texts))
        phrase = texts[idx-1]
        bubble.reply_text.config(state='normal')
        bubble.reply_text.delete('1.0', tk.END)
        bubble.reply_text.insert(tk.END, phrase)
        bubble.reply_text.config(state='disabled')
        self.play_chat_voice(idx)

    # ---------- 资源路径 ----------
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    # ---------- 配置管理 ----------
    def load_config(self):
        default_config = {"user_name": "博士", "window_x": 100, "window_y": 100, "chat_lang": "zh-CN"}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.user_name = config.get("user_name", "博士")
                self.window_x = config.get("window_x", 100)
                self.window_y = config.get("window_y", 100)
                self.current_lang = config.get("chat_lang", "zh-CN")
        else:
            self.user_name = self._ask_name()
            self.window_x, self.window_y = 100, 100
            self.save_config()

    def save_config(self):
        config = {"user_name": self.user_name, "window_x": self.window_x, "window_y": self.window_y, "chat_lang": self.current_lang}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _ask_name(self):
        import tkinter.simpledialog as sd
        root_temp = tk.Tk()
        root_temp.withdraw()
        root_temp.attributes('-topmost', True)
        name = sd.askstring("初次见面", "博士，请告诉我你的名字：", parent=root_temp)
        root_temp.destroy()
        return name.strip() if name else "博士"

    # ---------- 图片加载 ----------
    def load_images(self):
        base_path = self.resource_path(f"images/{self.current_image_set}")
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)
            messagebox.showinfo("提示", f"请将黍的 PNG 图片放入 {base_path} 文件夹内。")
            return

        screen_height = self.root.winfo_screenheight()
        base_height = int(screen_height * 0.35)
        target_height = int(base_height * self.height_scale)
        target_width = int(base_height * 0.85 * self.width_scale)

        self.frames = []
        self.expressions = {}
        for filename in os.listdir(base_path):
            if not filename.lower().endswith('.png'):
                continue
            full_path = os.path.join(base_path, filename)
            try:
                img = Image.open(full_path)
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                name = os.path.splitext(filename)[0]
                if name not in self.expressions:
                    self.expressions[name] = []
                self.expressions[name].append(photo)
                self.frames.append(photo)
            except Exception as e:
                print(f"加载图片 {filename} 失败：{e}")

        if "default" not in self.expressions and self.expressions:
            first_key = list(self.expressions.keys())[0]
            self.expressions["default"] = self.expressions[first_key]
        if not self.frames:
            blank = tk.PhotoImage(width=200, height=300)
            self.frames.append(blank)
            self.expressions["default"] = [blank]

    def set_expression(self, expr_name):
        if expr_name in self.expressions and self.expressions[expr_name]:
            self.label.config(image=self.expressions[expr_name][0])
            self.label.image = self.expressions[expr_name][0]

    def animate(self, idx=0):
        if self.frames:
            self.label.config(image=self.frames[idx % len(self.frames)])
            self.label.image = self.frames[idx % len(self.frames)]
        self.root.after(30, self.animate, idx + 1)

    # ---------- 窗口拖动 ----------
    def start_move(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")
        self.window_x, self.window_y = x, y
        self.save_config()

    # ---------- 主动关心 ----------
    def reset_idle_timer(self):
        if self.idle_timer:
            self.root.after_cancel(self.idle_timer)
        self.idle_timer = self.root.after(300000, self.on_idle)

    def on_idle(self):
        self.reset_idle_timer()
        cares = ["今天有没有好好吃饭？", "休息一下，别太累了。", "要记得按时喝水哦。",
                 "是不是又熬夜了？要好好休息呀。", "有什么心事想和我聊聊吗？"]
        self.show_idle_bubble(random.choice(cares))

    # ---------- 气泡圆角辅助 ----------
    def _create_round_rect(self, canvas, x1, y1, x2, y2, radius=15, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
                  x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
                  x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    # ---------- 主对话框 ----------
    def show_chat(self, event=None):
        self.reset_idle_timer()
        if self.active_bubble and self.active_bubble.winfo_exists():
            self.active_bubble.destroy()
        self.active_bubble = None

        bubble = tk.Toplevel(self.root)
        bubble.overrideredirect(True)
        bubble.wm_attributes('-topmost', True)
        bubble.wm_attributes('-alpha', 0.96)
        bubble.config(bg='#F5F0E6')
        self.active_bubble = bubble

        s = self.bubble_scale
        base_w, base_h = 260, 240
        w, h = int(base_w * s), int(base_h * s)
        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y() + 30
        bubble.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(bubble, width=w, height=h, bg='#F5F0E6', highlightthickness=0)
        canvas.pack()
        self._create_round_rect(canvas, 0, 0, w, h, radius=int(20*s),
                                fill='#FFF9F0', outline='#D4B48C', width=2)

        canvas.create_text(int(20*s), int(15*s), text="💬 对黍说：", anchor='nw',
                           fill='#5D3A1A', font=('宋体', int(9*s), 'bold'))

        entry = tk.Entry(bubble, width=int(28*s), font=('宋体', int(10*s)), bd=1,
                         relief='solid', highlightcolor='#D4B48C')
        entry.place(x=int(20*s), y=int(45*s))

        # 先创建回复区域，再创建按钮（避免按钮回调时 reply_text 未定义）
        reply_text = scrolledtext.ScrolledText(bubble, wrap=tk.WORD,
                                               width=int(30*s), height=int(5*s),
                                               font=('宋体', int(10*s)),
                                               bg='#FFF9F0', fg='#3E2A1A',
                                               relief='flat', highlightthickness=0)
        reply_text.place(x=int(20*s), y=int(165*s), width=int(220*s), height=int(80*s))
        reply_text.config(state='disabled')
        bubble.reply_text = reply_text

        send_btn = tk.Button(bubble, text="发送", command=lambda: self.send_chat(entry, bubble),
                             bg='#D4B48C', fg='white', relief='flat', padx=int(10*s),
                             activebackground='#C0A06B')
        send_btn.place(x=int(20*s), y=int(85*s))

        chat_btn = tk.Button(bubble, text="闲聊", command=lambda: self.random_chat(bubble),
                             bg='#A0D6B4', fg='white', relief='flat', padx=int(10*s),
                             activebackground='#90C6A4')
        chat_btn.place(x=int(20*s), y=int(125*s))

        exit_btn = tk.Button(bubble, text="再见", command=self.quit_app,
                             bg='#D4B48C', fg='white', relief='flat', padx=int(10*s),
                             activebackground='#C0A06B')
        exit_btn.place(x=int(100*s), y=int(125*s))

        bubble.bind('<Double-Button-1>', lambda e: self.close_bubble(bubble))
        entry.bind('<Return>', lambda e: self.send_chat(entry, bubble))

        bubble.entry = entry
        bubble.send_btn = send_btn

    def send_chat(self, entry, bubble):
        user_input = entry.get()
        if not user_input:
            return
        if user_input.strip() in ['再见', '明天见', '拜拜', '退出', 'exit', 'bye']:
            self.root.destroy()
            return

        if self.handle_music_command(user_input):
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.config(state='disabled')
            bubble.after(3000, lambda: self.close_bubble(bubble))
            return

        entry.config(state='disabled')
        bubble.send_btn.config(state='disabled')
        bubble.reply_text.config(state='normal')
        bubble.reply_text.delete('1.0', tk.END)
        bubble.reply_text.insert(tk.END, "黍正在思考...")
        bubble.reply_text.config(state='disabled')

        def task():
            reply = self.ai.respond(user_input)
            self.root.after(0, self.display_reply, reply, bubble)

        threading.Thread(target=task).start()

    def display_reply(self, reply, bubble):
        bubble.reply_text.config(state='normal')
        bubble.reply_text.delete('1.0', tk.END)
        bubble.reply_text.insert(tk.END, reply)
        bubble.reply_text.config(state='disabled')
        bubble.after(8000, lambda: self.close_bubble(bubble))

    def show_idle_bubble(self, text):
        if self.active_bubble and self.active_bubble.winfo_exists():
            self.active_bubble.destroy()
        bubble = tk.Toplevel(self.root)
        bubble.overrideredirect(True)
        bubble.wm_attributes('-topmost', True)
        bubble.wm_attributes('-alpha', 0.96)
        bubble.config(bg='#F5F0E6')
        self.active_bubble = bubble

        w, h = 220, 100
        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y() + 30
        bubble.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(bubble, width=w, height=h, bg='#F5F0E6', highlightthickness=0)
        canvas.pack()
        self._create_round_rect(canvas, 0, 0, w, h, radius=20,
                                fill='#FFF9F0', outline='#D4B48C', width=2)

        label = tk.Label(bubble, text=text, wraplength=w-30, justify='left',
                         bg='#FFF9F0', font=('宋体', 10), fg='#3E2A1A')
        label.place(x=15, y=15)

        bubble.bind('<Double-Button-1>', lambda e: bubble.destroy())
        bubble.after(5000, lambda: self.close_bubble(bubble))

    def close_bubble(self, bubble):
        try:
            if bubble.winfo_exists():
                bubble.destroy()
            if hasattr(self, 'active_bubble') and self.active_bubble == bubble:
                self.active_bubble = None
        except:
            pass

    def quit_app(self):
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
        self.root.destroy()

    # ---------- 双击切换立绘 ----------
    def cycle_expression(self, event=None):
        self.current_image_set = "shupaopao" if self.current_image_set == "shu" else "shu"
        if hasattr(self, '_original_images'):
            del self._original_images
        if self.reload_timer:
            self.root.after_cancel(self.reload_timer)
        self._reload_images()
        self.show_idle_bubble(f"已切换至 {self.current_image_set} 立绘")

    # ---------- 音乐功能 ----------
    def scan_music_folder(self):
        music_dir = "music"
        if not os.path.exists(music_dir):
            os.makedirs(music_dir, exist_ok=True)
            return
        self.music_index = {}
        for f in os.listdir(music_dir):
            if f.lower().endswith(('.mp3', '.flac')):
                name = os.path.splitext(f)[0]
                self.music_index[name] = os.path.join(music_dir, f)

    def find_best_match(self, query):
        if not self.music_index:
            return None
        matches = difflib.get_close_matches(query, list(self.music_index.keys()), n=1, cutoff=0.4)
        if matches:
            return matches[0], self.music_index[matches[0]]
        return None

    def handle_music_command(self, user_input):
        if not PYGAME_AVAILABLE:
            return False
        keywords = ['播放', '点歌', '我想听', '来一首', '放一首', '听']
        for kw in keywords:
            if kw in user_input:
                parts = user_input.split(kw, 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    if query:
                        result = self.find_best_match(query)
                        if result:
                            song_name, path = result
                            try:
                                pygame.mixer.music.load(path)
                                pygame.mixer.music.play(-1)
                                self.music_playing = True
                                self.music_paused = False
                                self.current_music_file = path
                                self.show_idle_bubble(f"🎵 正在播放: {song_name}")
                            except Exception as e:
                                self.show_idle_bubble(f"播放失败: {e}")
                            return True
                        else:
                            self.show_idle_bubble(f"没有找到与「{query}」相似的歌曲")
                            return True
        return False

    def play_music(self):
        if not PYGAME_AVAILABLE:
            self.show_idle_bubble("pygame 未安装，无法播放音乐")
            return
        if not self.current_music_file:
            self.select_music_file()
            if not self.current_music_file:
                return
        try:
            pygame.mixer.music.load(self.current_music_file)
            pygame.mixer.music.play(-1)
            self.music_playing = True
            self.music_paused = False
            self.show_idle_bubble(f"🎵 正在播放: {os.path.basename(self.current_music_file)}")
        except Exception as e:
            self.show_idle_bubble(f"播放失败: {e}")

    def pause_music(self):
        if not PYGAME_AVAILABLE:
            return
        if self.music_playing:
            if self.music_paused:
                pygame.mixer.music.unpause()
                self.music_paused = False
                self.show_idle_bubble("▶️ 继续播放")
            else:
                pygame.mixer.music.pause()
                self.music_paused = True
                self.show_idle_bubble("⏸️ 已暂停")

    def stop_music(self):
        if not PYGAME_AVAILABLE:
            return
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.music_paused = False
            self.show_idle_bubble("⏹️ 音乐已停止")

    def select_music_file(self):
        if not PYGAME_AVAILABLE:
            self.show_idle_bubble("pygame 未安装，无法选择音乐")
            return
        path = filedialog.askopenfilename(
            title="选择音乐文件",
            filetypes=[("音频文件", "*.mp3 *.flac"), ("MP3文件", "*.mp3"), ("FLAC文件", "*.flac")]
        )
        if path:
            self.current_music_file = path
            self.show_idle_bubble(f"已选择: {os.path.basename(path)}")

    def set_music_volume(self, val):
        if PYGAME_AVAILABLE:
            self.music_volume = float(val)
            pygame.mixer.music.set_volume(self.music_volume)

    # ---------- 分批重绘 ----------
    def _reload_images(self):
        if hasattr(self, '_reload_job') and self._reload_job:
            self.reload_cancel = True
            self.root.after(50, lambda: self._start_reload())
        else:
            self._start_reload()

    def _start_reload(self):
        self.reload_cancel = False
        if not hasattr(self, '_original_images'):
            self._load_original_images()
        if not self._original_images:
            return

        screen_height = self.root.winfo_screenheight()
        base_height = int(screen_height * 0.25)
        target_height = int(base_height * self.height_scale)
        target_width = int(base_height * 0.95 * self.width_scale)

        self.frames = []
        self.expressions = {}

        total = len(self._original_images)
        processed = 0
        BATCH_SIZE = 10

        def process_batch():
            nonlocal processed
            if self.reload_cancel:
                return
            start = processed
            end = min(start + BATCH_SIZE, total)
            for i in range(start, end):
                name, img = self._original_images[i]
                try:
                    scaled = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(scaled)
                    if name not in self.expressions:
                        self.expressions[name] = []
                    self.expressions[name].append(photo)
                    self.frames.append(photo)
                except Exception as e:
                    print(f"缩放图片失败 {name}: {e}")
            processed = end
            if processed < total and not self.reload_cancel:
                self._reload_job = self.root.after(20, process_batch)
            else:
                self._reload_job = None
                self.expression_list = list(self.expressions.keys())
                self.current_expr_index = 0
                if self.frames:
                    self.label.config(image=self.frames[0])
                    self.label.image = self.frames[0]

        process_batch()

    def _load_original_images(self):
        base_path = self.resource_path(f"images/{self.current_image_set}")
        self._original_images = []
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)
            return
        for filename in os.listdir(base_path):
            if not filename.lower().endswith('.png'):
                continue
            full_path = os.path.join(base_path, filename)
            try:
                img = Image.open(full_path)
                name = os.path.splitext(filename)[0]
                self._original_images.append((name, img))
            except Exception as e:
                print(f"加载图片失败 {filename}: {e}")

    # ---------- 立绘尺寸步进方法 ----------
    def _inc_width(self):
        self.width_scale = min(2.0, self.width_scale + 0.05)
        self.width_label.config(text=f"{self.width_scale:.2f}")
        if self.reload_timer:
            self.root.after_cancel(self.reload_timer)
        self.reload_timer = self.root.after(300, self._reload_images)

    def _dec_width(self):
        self.width_scale = max(0.5, self.width_scale - 0.05)
        self.width_label.config(text=f"{self.width_scale:.2f}")
        if self.reload_timer:
            self.root.after_cancel(self.reload_timer)
        self.reload_timer = self.root.after(300, self._reload_images)

    def _inc_height(self):
        self.height_scale = min(2.0, self.height_scale + 0.05)
        self.height_label.config(text=f"{self.height_scale:.2f}")
        if self.reload_timer:
            self.root.after_cancel(self.reload_timer)
        self.reload_timer = self.root.after(300, self._reload_images)

    def _dec_height(self):
        self.height_scale = max(0.5, self.height_scale - 0.05)
        self.height_label.config(text=f"{self.height_scale:.2f}")
        if self.reload_timer:
            self.root.after_cancel(self.reload_timer)
        self.reload_timer = self.root.after(300, self._reload_images)

    # ---------- 好感度滑块回调 ----------
    def _on_trust_slider(self, val):
        self.ai.trust_level = int(float(val))
        self.trust_label.config(text=f"{self.ai.trust_level}%")

    # ---------- 控制台 ----------
    def open_console(self, event=None):
        if hasattr(self, 'console') and self.console.winfo_exists():
            self.console.lift()
            return

        self.console = tk.Toplevel(self.root)
        self.console.title("黍黍桌宠 - 控制台")
        self.console.geometry("300x750")
        self.console.resizable(False, False)
        self.console.attributes('-topmost', True)

        # 用户名
        tk.Label(self.console, text="用户名", font=('宋体', 10, 'bold')).pack(pady=(10,0))
        name_frame = tk.Frame(self.console)
        name_frame.pack(pady=5)
        self.name_entry = tk.Entry(name_frame, width=15)
        self.name_entry.insert(0, self.ai.user_name)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(name_frame, text="修改", command=self._update_name).pack(side=tk.LEFT)

        # 好感度（滑块）
        tk.Label(self.console, text="好感度", font=('宋体', 10, 'bold')).pack(pady=(10, 0))
        trust_frame = tk.Frame(self.console)
        trust_frame.pack(pady=5)
        self.trust_label = tk.Label(trust_frame, text=f"{self.ai.trust_level}%", width=8)
        self.trust_label.pack(side=tk.LEFT, padx=5)
        self.trust_slider = tk.Scale(trust_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     length=150, command=self._on_trust_slider)
        self.trust_slider.set(self.ai.trust_level)
        self.trust_slider.pack(side=tk.LEFT, padx=5)

        # 立绘尺寸（按钮）
        tk.Label(self.console, text="立绘尺寸", font=('宋体', 10, 'bold')).pack(pady=(10, 0))
        size_frame = tk.Frame(self.console)
        size_frame.pack(pady=5)

        w_frame = tk.Frame(size_frame)
        w_frame.pack(pady=2)
        tk.Label(w_frame, text="宽度", width=5, anchor='e').pack(side=tk.LEFT)
        self.width_label = tk.Label(w_frame, text=f"{self.width_scale:.2f}", width=6)
        self.width_label.pack(side=tk.LEFT, padx=5)
        tk.Button(w_frame, text="-", command=self._dec_width, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(w_frame, text="+", command=self._inc_width, width=3).pack(side=tk.LEFT, padx=2)

        h_frame = tk.Frame(size_frame)
        h_frame.pack(pady=2)
        tk.Label(h_frame, text="高度", width=5, anchor='e').pack(side=tk.LEFT)
        self.height_label = tk.Label(h_frame, text=f"{self.height_scale:.2f}", width=6)
        self.height_label.pack(side=tk.LEFT, padx=5)
        tk.Button(h_frame, text="-", command=self._dec_height, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(h_frame, text="+", command=self._inc_height, width=3).pack(side=tk.LEFT, padx=2)

        # 对话框缩放
        tk.Label(self.console, text="对话框大小", font=('宋体', 10, 'bold')).pack(pady=(10,0))
        bubble_frame = tk.Frame(self.console)
        bubble_frame.pack(pady=5)
        self.bubble_var = tk.DoubleVar(value=self.bubble_scale)
        tk.Scale(bubble_frame, from_=0.8, to=1.5, resolution=0.05, orient=tk.HORIZONTAL,
                 length=200, variable=self.bubble_var, command=self._on_bubble_scale).pack(side=tk.LEFT)
        self.bubble_label = tk.Label(bubble_frame, text=f"{self.bubble_scale:.2f}", width=5)
        self.bubble_label.pack(side=tk.LEFT, padx=5)

        # 闲聊语言切换
        if self.chat_phrases:
            tk.Label(self.console, text="闲聊语言", font=('宋体', 10, 'bold')).pack(pady=(10,0))
            lang_frame = tk.Frame(self.console)
            lang_frame.pack(pady=5)
            self.lang_var = tk.StringVar(value=self.current_lang)
            lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                      values=list(self.chat_phrases.keys()),
                                      state="readonly", width=10)
            lang_combo.pack(side=tk.LEFT, padx=5)
            tk.Button(lang_frame, text="应用", command=self.change_language).pack(side=tk.LEFT)

        # 音乐播放器
        if PYGAME_AVAILABLE:
            tk.Label(self.console, text="音乐播放器", font=('宋体', 10, 'bold')).pack(pady=(10,0))
            music_frame = tk.Frame(self.console)
            music_frame.pack(pady=5)
            tk.Button(music_frame, text="选歌", command=self.select_music_file, bg='#6BA5D4', fg='white').pack(side=tk.LEFT, padx=2)
            tk.Button(music_frame, text="播放", command=self.play_music, bg='#6BA5D4', fg='white').pack(side=tk.LEFT, padx=2)
            tk.Button(music_frame, text="暂停/继续", command=self.pause_music, bg='#D46B6B', fg='white').pack(side=tk.LEFT, padx=2)
            tk.Button(music_frame, text="停止", command=self.stop_music, bg='#D46B6B', fg='white').pack(side=tk.LEFT, padx=2)

            vol_frame = tk.Frame(self.console)
            vol_frame.pack(pady=5)
            tk.Label(vol_frame, text="音量", font=('宋体', 9)).pack(side=tk.LEFT)
            self.volume_var = tk.DoubleVar(value=self.music_volume)
            tk.Scale(vol_frame, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                     length=150, variable=self.volume_var, command=self.set_music_volume).pack(side=tk.LEFT, padx=5)
            self.volume_label = tk.Label(vol_frame, text=f"{int(self.music_volume*100)}%", width=4)
            self.volume_label.pack(side=tk.LEFT)
            def update_volume_label(val):
                self.volume_label.config(text=f"{int(float(val)*100)}%")
            self.volume_var.trace('w', lambda *args: update_volume_label(self.volume_var.get()))
        else:
            tk.Label(self.console, text="音乐播放器不可用\n请安装pygame", font=('宋体', 9), fg='red').pack(pady=5)

        # 其他功能
        tk.Label(self.console, text="其他功能", font=('宋体', 10, 'bold')).pack(pady=(10,0))
        self.idle_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.console, text="启用主动关心", variable=self.idle_var,
                       command=self._toggle_idle).pack(anchor='w', padx=20)
        tk.Button(self.console, text="清空对话历史", command=self._clear_history).pack(pady=5)
        tk.Button(self.console, text="关于", command=self.show_about).pack(pady=5)
        tk.Button(self.console, text="关闭", command=self.console.destroy).pack(pady=10)

    def change_language(self):
        new_lang = self.lang_var.get()
        if new_lang in self.chat_phrases:
            if self.current_voice:
                self.current_voice.stop()
                self.current_voice = None
            self.current_lang = new_lang
            self.save_config()
            self.show_idle_bubble(f"闲聊语言已切换至 {new_lang}")

    def _update_name(self):
        new = self.name_entry.get().strip()
        if new:
            self.ai.user_name = new
            self.root.title(f"黍黍桌宠 - {new}")
            self.save_config()

    def _on_bubble_scale(self, val):
        self.bubble_scale = float(val)
        self.bubble_label.config(text=f"{self.bubble_scale:.2f}")

    def _toggle_idle(self):
        if self.idle_var.get():
            self.reset_idle_timer()
        else:
            if self.idle_timer:
                self.root.after_cancel(self.idle_timer)
                self.idle_timer = None

    def _clear_history(self):
        self.ai.conversation_history = []
        self.show_idle_bubble("对话历史已清空")

    def show_about(self):
        about_text = """黍黍桌宠 v1.5

作者：无聊鸽子咕 & shafzzaz

本软件为《明日方舟》同人二创作品
完全免费，仅用于个人交流与非商业使用
角色版权归鹰角网络所有

功能：
- 双击立绘切换皮肤
- 立绘大小改用按钮调节
- 好感度用滑块调节
- 对话点歌、闲聊语音（多语言）
- 主动关心、圆角气泡

感谢使用！"""
        messagebox.showinfo("关于 黍黍桌宠", about_text)


# ==================== 主程序 ====================
if __name__ == "__main__":
    try:
        import openai
        from PIL import Image
    except ImportError:
        print("请安装所需库：pip install openai pillow")
        sys.exit(1)

    API_KEY = "sk-a2a576369272453d805621c46917d3ae"

    pet = ShuPet(API_KEY)
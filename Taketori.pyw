import ctypes
import random
import pickle
import tkinter as tk
from os import system
from time import sleep, perf_counter
from threading import Thread

# TODO: bgm

try:
    import PySimpleGUI as sg
except ModuleNotFoundError:
    system('py -m pip install PySimpleGUI')
    import PySimpleGUI as sg

try:
    from pygame import mixer
except ModuleNotFoundError:
    system('py -m pip install pygame')
    from pygame import mixer

sg.theme('DarkGreen7')

class Taketori:
    WIDTH = 8
    TAKE_MAX_LEN = 7
    TAKE_STEP = 2
    TAKENOKO = 1, 2, 3, 4, 5
    BACK_GROUND_COLOR = None

    LINKS = \
'''竹: https://illustimage.com/?id=10508

筍: https://www.irasutoya.com/2018/11/blog-post_91.html

背景: https://www.irasutoya.com/2017/12/blog-post_537.html

ミスの効果音: https://rotmcits.com/wafuu-koukaon/

竹の効果音: https://otologic.jp/free/se/instruments-japanese01.html

筍の効果音: https://otologic.jp/free/se/onmtp-others01.html'''

    def __init__(self):
        self.init_game()
        self.window = self.create_window()


    def init_game(self):
        # 竹の成長度を格納するlist
        self.take = [0 for _ in range(Taketori.WIDTH)]

        # 竹・筍の刈り取った数とその合計
        self.take_num = 0
        self.takenoko_num = 0
        self.sum_num = 0
        # スコアとその最大値
        self.score = 0
        self.max_score = 0
        # 筍ンボとその最大値
        self.combo = 0
        self.max_combo = 0

        # プレイ中 -> True
        self.now_playing = False
        # スコアの記録可能 -> True
        self.can_record = False
        # ミュート状態 -> True
        self.mute = False

        mixer.init()


    def init_display(self):
        # メニューバー(Setting)の作成
        setting = self.window['MENU'].Widget
        setting_menu = tk.Menu(tearoff=False)
        setting.add_cascade(label='Setting', menu=setting_menu)
        setting_menu.add_checkbutton(
            command = self.mute_update,
            label = 'Mute',
        )

        # figureのidを格納するlist
        self.take_fig = [[None for _ in range(Taketori.TAKE_MAX_LEN)] for _ in range(Taketori.WIDTH)]
        self.takenoko_fig = [None for _ in range(Taketori.WIDTH)]
        self.result_text = [None for _ in range(9)]

        graph = self.window['MAIN_G']

        # resultの背景
        self.result_background = graph.DrawRectangle(
            top_left = (450 - 225, 0 + 138),
            bottom_right = (900 - 225, 231 + 138),
            fill_color = '#0c231e',
            line_width = 0
        )

        for i in range(Taketori.WIDTH):
            # 筍のfigure
            self.takenoko_fig[i] = graph.draw_image(
                filename = 'takenoko.png',  # 50 * 50
                location = (56 + i * 107, 507 - 50)
            )

            # 竹のfigure
            for j in range(Taketori.TAKE_MAX_LEN):
                self.take_fig[i][j] = graph.draw_image(
                    filename = 'take.png',  # 43 * 70
                    location = (56 + i * 107, 507 - 70 - j * 70)
                )

        # 背景画像のfigure
        self.back_ground_fig = graph.draw_image(
            filename = 'background.png',
            location = (0, 0)
        )

        # ゲームオーバーラインのfigure
        self.dead_line_fig = graph.draw_line(
            (0, 45),
            (900, 45),
            'red',
            3
        )


    def create_window(self):
        tp = 5  # text_pad

        menu = sg.Menu(
            [['Information', ['Ranking', 'Links']]],
            background_color = '#eeeeee',
            text_color = '#000000',
            disabled_text_color = '#cccccc',
            font = ('Yu Gothic UI', 9),
            pad = 0,
            k = 'MENU'
        )

        left_frame = sg.Frame(
            title = '',
            layout = [
                [sg.G(
                    canvas_size = (900, 507),
                    graph_bottom_left = (0, 507),
                    graph_top_right = (900, 0),
                    k = 'MAIN_G'
                )],
                [sg.T(
                    text = ' ' * tp + (' ' * tp * 2).join('ASD'),
                    font = ('メイリオ', 20),
                    pad = 0
                ),
                sg.T(
                    text = ' ' * tp * 2 + (' ' * tp * 2).join('FJ') + ' ' * tp * 2,
                    font = ('メイリオ', 20),
                    text_color = '#FF0000',
                    pad = 0
                ),
                sg.T(
                    text = (' ' * tp * 2).join('KL;') + ' ' * tp,
                    font = ('メイリオ', 20),
                    pad = 0
                ),]
            ],
            border_width = 0,
            element_justification = 'center'
        )

        right_frame = sg.Frame(
            title = '',
            layout = [
                [sg.T('スコア:', p=0), sg.T(self.score, 7, justification='right', p=0, k='SCORE_T')],
                [sg.T('筍ンボ:', p=0), sg.T(self.combo, 7, justification='right', p=0, k='COMBO_T')],
                [sg.T('　竹　:', p=0), sg.T(self.take_num, 7, justification='right', p=0, k='TAKE_T'), sg.T('㍍', p=0)],
                [sg.T('　筍　:', p=0), sg.T(self.takenoko_num, 7, justification='right', p=0, k='TAKENOKO_T'), sg.T('コ', p=0)],
                [sg.B('Start', k='START_B'), sg.B('Ranking', k='RANKING_B')]
            ],
            border_width = 0,
            vertical_alignment = 'top'
        )

        layout = [
            [menu],
            [left_frame, right_frame]
        ]

        return sg.Window('Taketori', layout, font='メイリオ', icon='Taketori.ico', use_default_focus=False)


    def create_links_window(self):
        layout = [[sg.Multiline(
            Taketori.LINKS,
            disabled = True,
            size = (60, 11),
            no_scrollbar = True
        )]]

        return sg.Window('Links', layout, font='メイリオ', icon='Taketori.ico', use_default_focus=False)


    def create_ranking_window(self):
        DEFAULT_NAME = '竹取の翁'

        values = self.get_fomated_ranking()

        layout = [
            [
                sg.Table(
                    values,
                    ['No.', 'NAME', 'MAX SCORE', 'MAX COMBO'],
                    col_widths = [3, 27, 12, 12],
                    auto_size_columns = False,
                    max_col_width = 50,
                    vertical_scroll_only = True,
                    k = 'RANKING_T',
                    expand_x = True
                )
            ],
            [
                sg.T('name:'), sg.Input(default_text=DEFAULT_NAME, size=(35, 1), k='NAME_IN'),
                sg.B('Record', disabled=not self.can_record, k='RECORD_B'), sg.B('Close', k='CLOSE_B')
            ]
        ]

        return sg.Window('Ranking', layout, font='メイリオ', icon='Taketori.ico', use_default_focus=False, modal=True)


    def get_raw_ranking(self):
        try:
            # 別ファイルに存在するランキングデータ(name, m_score, m_combo)を取得
            with open('ranking_data.pkl','rb') as f:
                ranking_list = pickle.load(f)

            # 生のランキングデータ(name, m_score, m_combo)を返却
            return ranking_list

        # ファイルが存在しない・空の場合
        except(FileNotFoundError, EOFError):
            with open('ranking_data.pkl','wb') as f:
                pickle.dump(
                    [
                        ['竹取師範', 2000, 50],
                        ['竹取にいさん', 1000, 20],
                        ['竹取ジュニア', 500, 10]
                    ],
                    f
                )

            return self.get_raw_ranking()


    def get_fomated_ranking(self):
        # scoreをキーに降順でソート
        ranking_list = self.get_raw_ranking()
        ranking_list.sort(key=lambda x: x[1], reverse=True)

        # ソートしたランキングデータ(ranking, name, m_score, m_combo)を返却
        return [[i + 1] + data for i, data in enumerate(ranking_list)]


    def set_ranking(self, name):
        ranking_list = self.get_raw_ranking()

        # 同じ名前でスコアが上回る場合データを更新
        for i, ranking_data in enumerate(ranking_list):
            if name == ranking_data[0]:
                if self.max_score >= ranking_data[1]:
                    ranking_list[i] = [name, self.max_score, self.max_combo]
                break
        # 同じ名前のデータがない
        else:
            ranking_list.append([name, self.max_score, self.max_combo])

        with open('ranking_data.pkl','wb') as f:
            pickle.dump(ranking_list, f)


    def mute_update(self):
        self.mute = False if self.mute else True


    def display_update(self, take_loc = None):
        graph = self.window['MAIN_G']

        self.window['SCORE_T'].update(self.score)
        self.window['COMBO_T'].update(self.combo)
        self.window['TAKE_T'].update(self.take_num)
        self.window['TAKENOKO_T'].update(self.takenoko_num)

        if take_loc is not None:
            for i in range(Taketori.TAKE_MAX_LEN):
                # 筍の表示
                if self.take[take_loc] in Taketori.TAKENOKO:
                    graph.bring_figure_to_front(self.takenoko_fig[take_loc])
                else:
                    graph.send_figure_to_back(self.takenoko_fig[take_loc])

                # 竹の表示
                if self.take[take_loc] > i * Taketori.TAKE_STEP + len(Taketori.TAKENOKO):
                    graph.bring_figure_to_front(self.take_fig[take_loc][i])
                    # ゲームオーバー時のリザルト表示
                    if i + 1 == Taketori.TAKE_MAX_LEN:
                        self.result_display()
                else:
                    graph.send_figure_to_back(self.take_fig[take_loc][i])

        # 初期化
        else:
            graph.bring_figure_to_front(self.back_ground_fig)
            self.result_erase()

        # ゲームオーバーラインを常に最全面表示
        graph.bring_figure_to_front(self.dead_line_fig)


    def result_display(self):
        comment_dic = {
            'エベレスト': 8848,
            '富士山': 3776,
            'エンジェルフォール': 979,
            'ブルジュ・ハリファ': 828,
            '東京スカイツリー': 634,
            'エッフェル塔': 324,
            '東京ドームの長径': 122,
            '自由の女神像': 93,
            'トイレットペーパー(シングル)\nの長さ': 60,
            'タワー・オブ・テラー': 59,
            'ピサの斜塔': 55,
            '渋谷109': 50,
            'トイレットペーパー(ダブル)\nの長さ': 30,
            'シロナガスクジラ': 24,
            'ジンベエザメ': 18,
            '鎌倉大仏': 11,
            'かに道楽の看板の横幅': 8,
            '坂本龍馬像': 5,
            'バスケットゴール': 3,
            '八村塁': 2,
            'ガキんちょ': 1,
        }

        if self.take_num:
            for name, height in comment_dic.items():
                if self.take_num >= height:
                    comment = name + '級!!'
                    break
        else:
            comment = ''

        graph = self.window['MAIN_G']  # 900 * 507

        graph.bring_figure_to_front(self.result_background)  # 450 * 230

        self.result_text[0] = graph.DrawText('MAX SCORE', (565 - 225, 30 + 138), '#efbe1c', ('メイリオ', 24))

        self.result_text[1] = graph.DrawText(self.max_score, (565 - 225, 85 + 138), '#efbe1c', ('メイリオ', 40))

        self.result_text[2] = graph.DrawText('MAX COMBO', (785 - 225, 30 + 138), '#efbe1c', ('メイリオ', 24))

        self.result_text[3] = graph.DrawText(self.max_combo, (785 - 225, 85 + 138), '#efbe1c', ('メイリオ', 40))

        self.result_text[4] = graph.DrawText(
            '竹:', (480 - 225, 140 + 138), '#efbe1c', 'メイリオ',
            text_location = sg.TEXT_LOCATION_LEFT
        )

        self.result_text[5] = graph.DrawText(
            str(self.take_num) + '㍍', (600 - 225, 140 + 138), '#efbe1c', 'メイリオ',
            text_location = sg.TEXT_LOCATION_RIGHT
        )

        self.result_text[6] = graph.DrawText(
            '筍:', (700 - 225, 140 + 138), '#efbe1c', 'メイリオ',
            text_location = sg.TEXT_LOCATION_LEFT
        )

        self.result_text[7] = graph.DrawText(
            str(self.takenoko_num) + 'コ', (820 - 225, 140 + 138), '#efbe1c', 'メイリオ',
            text_location = sg.TEXT_LOCATION_RIGHT
        )

        self.result_text[8] = graph.DrawText(comment, (565 - 225, 180 + 138), '#FF0000', 'メイリオ', 15)


    def result_erase(self):
        self.window['MAIN_G'].send_figure_to_back(self.result_background)

        for i, text in enumerate(self.result_text):
            if text is not None:
                self.window['MAIN_G'].delete_figure(text)
                self.result_text[i] = None


    def play_se(self, se, loops = 1):
        se = mixer.Sound(se)
        for _ in range(loops):
            se.play()
            sleep(0.1)


    def cut_take(self, take_loc):
        # プレイ中でない
        if not self.now_playing:
            return

        # 入力された位置に竹(の子)がない
        if self.take[take_loc] == 0:
            # ミスの効果音
            if not self.mute:
                se_th = Thread(target=self.play_se, args=('miss_se.mp3',), daemon=True)
                se_th.start()

            self.score = max(0, self.score - 20)
            self.combo = 0
            self.display_update(take_loc)

        # 入力された位置に竹・筍がある
        else:
            if self.take[take_loc] in Taketori.TAKENOKO:
                # 筍の効果音
                if not self.mute:
                    se_th = Thread(target=self.play_se, args=('takenoko_se.mp3',), daemon=True)
                    se_th.start()

                self.takenoko_num += 1
                self.sum_num += 1
                self.score += 10 + self.combo
                self.max_score = max(self.max_score, self.score)
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self.take[take_loc] = 0
                self.display_update(take_loc)
            else:
                take_len = (self.take[take_loc] - len(Taketori.TAKENOKO) + 1) // Taketori.TAKE_STEP

                # 竹の効果音
                if not self.mute:
                    se_th = Thread(target=self.play_se, args=('take_se.mp3', take_len), daemon=True)
                    se_th.start()

                self.take_num += take_len
                self.sum_num += 1
                self.score += take_len
                self.max_score = max(self.max_score, self.score)
                self.combo = 0
                self.take[take_loc] = 0
                self.display_update(take_loc)


    def input_ky(self):
        key_codes = [
            65,  # a
            83,  # s
            68,  # d
            70,  # f
            74,  # j
            75,  # k
            76,  # l
            186, # ;
            187  # ;
        ]

        get_key_state = ctypes.windll.user32.GetAsyncKeyState

        while self.now_playing:
            for key_code in key_codes:
                if get_key_state(key_code) == 0x8001:
                    self.cut_take(min(key_codes.index(key_code), 7))


    def play(self):
        self.now_playing = True
        self.can_record = False
        take_cycle = 5  # 最小値: 0
        take_cycle_lv = 1
        growth_rate = 30  # 最小値: 1
        growth_rate_lv = 1
        next_take = take_cycle

        self.window['START_B'].update(disabled=True)

        self.display_update()

        sleep(1)

        # 開始時間
        start_time = perf_counter()

        while self.now_playing:
            take_cnt = 0

            # 竹・筍を成長させる
            for i, take in enumerate(self.take):
                if 0 < take:
                    take_cnt += 1
                    self.take[i] += 1
                    display_th = Thread(target=self.display_update, args=(i,), daemon=True)
                    display_th.start()

                    # 伸びすぎた場合
                    if (self.take[i] - len(Taketori.TAKENOKO) + 1) // Taketori.TAKE_STEP >= Taketori.TAKE_MAX_LEN:
                        self.now_playing = False
                        self.can_record = True
                        break

            # 竹が無い or 筍が生える周期
            if take_cnt == 0 or next_take <= 0:
                # 筍を生やす場所
                takenoko_loc = random.choice([i for i in range(Taketori.WIDTH)])
                # 筍を生やす処理
                self.take[takenoko_loc] += 1
                display_th = Thread(target=self.display_update, args=(takenoko_loc,), daemon=True)
                display_th.start()
                # 周期のリセット
                next_take = random.randint(take_cycle - 2, take_cycle + 5)

                # 複数本同時生え
                if next_take <= 0:
                    for i in range(-next_take + 1):
                        # 生えてないところがある
                        if len([i for i, num in enumerate(self.take) if num == 0]):
                            takenoko_loc = random.choice(
                                [i for i, num in enumerate(self.take) if num == 0]
                            )
                            self.take[takenoko_loc] += 1
                            display_th = Thread(target=self.display_update, args=(takenoko_loc,), daemon=True)
                            display_th.start()

                        # 生えてないところがない
                        else:
                            break

                    next_take = random.randint(3, take_cycle + 5)

            else:
                next_take -= 1

            # 生えてくる周期の短縮
            for i in (take_cycle_lv, 7):
                if self.max_score > i * 500:
                    take_cycle = 6 - i
                    take_cycle_lv += 1
                    print()
                    print('take_cycle', growth_rate)
                    print()
            '''
            for i in range(6):
                if perf_counter() - start_time >= i * 12:
                    take_cycle = min(take_cycle, 5 - i)
                    # print('tr', take_cycle)debug
            '''

            # 成長速度の増加
            for i in range(growth_rate_lv, 31):
                if perf_counter() - start_time >= i ** 1.3:
                    growth_rate = 31 - i
                    growth_rate_lv += 1
                    print('growth_rate', growth_rate)

            sleep((1 * growth_rate) / 60)

        self.window['START_B'].update(disabled=False)


    def window_read(self, window):
        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'CLOSE_B'):
                break

            elif event == 'RECORD_B':
                # 再レコード禁止
                self.can_record = False
                window['RECORD_B'].update(disabled=True)

                # データ保存
                self.set_ranking(values['NAME_IN'])
                window['RANKING_T'].update(self.get_fomated_ranking())

            else:
                print(event, values)  # debug

        window.close()


    def start(self):
        timeout = 0

        while True:
            event, values = self.window.read(timeout)

            if event == sg.WIN_CLOSED:
                self.now_playing = False
                self.can_record = False
                break

            elif event == '__TIMEOUT__':
                timeout = None
                self.init_display()

            elif event == 'START_B':
                self.init_game()
                play_th = Thread(target=self.play, daemon=True)
                input_th = Thread(target=self.input_ky, daemon=True)
                play_th.start()
                input_th.start()

            elif event == 'Links':
                self.window_read(self.create_links_window())

            elif event in ('RANKING_B', 'Ranking'):
                self.window_read(self.create_ranking_window())

            else:
                print(event, values)  # debug

        self.window.close()



def main():
    taketori = Taketori()
    taketori.start()


if __name__ == '__main__':
  main()

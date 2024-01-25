# coding=utf-8
# R2023 edition by wechatID：:czt_306

import c4d
import os
import random
import copy


icons = [5143, 1001003, 1018685, 5105, 5104, 1011146, 440000267, 440000243, 1040448, 1023866, 1018545, 5116, 5160, 5170,
         5159, 5181, 5176]
i_list = [
    [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
    [[1, 1, 1, 1]]
]
z_left = [
    [[1, 0], [1, 1], [0, 1]],
    [[0, 1, 1], [1, 1, 0]]
]
z_right = [
    [[0, 1], [1, 1], [1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]
o_list = [
    [[1, 1], [1, 1]]
]
t_list = [
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0], [1, 1], [1, 0]],
    [[1, 1, 1], [0, 1, 0]],
    [[0, 1], [1, 1], [0, 1]]
]
l_left = [
    [[1, 1], [0, 1], [0, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 0], [1, 0], [1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]
l_right = [
    [[1, 1], [1, 0], [1, 0]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 1], [0, 1], [1, 1]],
    [[1, 1, 1], [0, 0, 1]]
]


def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp

class iconArea(c4d.gui.GeUserArea):
    def __init__(self, GeDialog,doc):
        super().__init__()
        self.doc = doc
        self.magic = False
        self.GetDialog = GeDialog
        self.color = c4d.Vector(0.168)
        self.score = 0
        self.level = self.score // 10 + 1
        self.chance = 3
        self.speed = 1000 // self.level
        self.next = self.GetRandomNext()  # (status->int,icon_id->int,args->list)
        self.actor = self.GetRandomNext()  # (status->int,icon_id->int,args->list)
        self.actor_status = self.GetActorNowByStatus(self.actor['status'], *self.actor['all'])
        self.squareId = [None for i in range(200)]
        self.showId = self.GetActorNowByStatus(self.actor['status'], *self.actor['all'], start_x=-1, start_y=-1)
        self.ChangeIconInSquare(self.actor['icon'], *self.showId)
        self.check = []

    @staticmethod
    def GetIndexByPos(x, y):
        return int(y * 10 + x)

    @staticmethod
    def GetPosByIndex(index):
        return int(index % 10), int(index // 10)

    def ChangeIconInSquare(self, icon, *actor_status):
        for show in self.actor_status:
            self.squareId[show] = None
            try:
                self.showId.remove(show)
            except ValueError:
                pass
        for temp in actor_status:
            self.squareId[temp] = icon
        self.actor_status = actor_status
        for st in actor_status:
            if st not in self.showId:
                self.showId.append(st)
        return True

    def AddIconInSquare(self):
        for st in self.actor_status:
            self.squareId[st] = self.actor['icon']

    def GetActorNowByStatus(self, status, *args, start_x=-1, start_y=-1):
        if start_x == -1 and start_y == -1:
            start_x = (10 - len(args[status][0])) / 2 if (10 - len(args[status][0])) % 2 == 0 else (11 - len(
                args[status][0])) / 2
            start_y = 0
        temp = []
        for i, row in enumerate(args[status]):
            for j, square in enumerate(row):
                if square == 1:
                    temp.append(self.GetIndexByPos(start_x + j, start_y + i))
        return temp

    def GetActorIndexByMoveDown(self, step=1):
        temp = []
        start_y = min(self.actor_status) // 10
        delta = len(self.actor['all'][self.actor['status']])
        self.check = [start_y + i for i in range(delta)]

        for index in self.actor_status:
            x, y = self.GetPosByIndex(index)
            y += step
            if 0 <= y < 20:
                temp.append(self.GetIndexByPos(x, y))
            else:
                return None
        for st in temp:
            if st >= 200 or st < 0:
                return None
            else:
                if st not in self.actor_status and self.squareId[st] is not None:
                    return None
        return temp

    def GetActorIndexByMoveLeftRight(self, vector, step=1):
        temp = []
        for index in self.actor_status:
            x, y = self.GetPosByIndex(index)
            if vector == 'left':
                x -= step
                if 0 <= x < 10:
                    temp.append(self.GetIndexByPos(x, y))
                else:
                    return None
            if vector == 'right':
                x += step
                if 0 <= x < 10:
                    temp.append(self.GetIndexByPos(x, y))
                else:
                    return None
        for st in temp:
            if self.squareId[st] is not None and st not in self.actor_status:
                return None
        return temp

    def GetStartPosByStatus(self):
        try:
            temp_index = self.actor['all'][self.actor['status']][0].index(1)
        except ValueError:
            temp_index = self.actor['all'][self.actor['status']][1].index(1)
        return self.GetPosByIndex(self.actor_status[0] - temp_index)

    def GetActorIndexByTurn(self):
        times = len(self.actor['all'])
        temp_status = (self.actor['status'] + 1) % times
        temp_w = len(self.actor['all'][temp_status][0])
        temp_h = len(self.actor['all'][temp_status])
        x, y = self.GetStartPosByStatus()
        temp_new_status = self.GetActorNowByStatus(temp_status, *self.actor['all'], start_x=x, start_y=y)
        if temp_w + x > 10:
            return None
        if temp_h + y > 20:
            return None
        for st in temp_new_status:
            if self.squareId[st] is not None and st not in self.actor_status:
                return None
        return temp_status, temp_new_status

    def drawCell(self, key, value):
        x, y = self.GetPosByIndex(key)
        bmp = c4d.bitmaps.InitResourceBitmap(value)
        self.DrawBitmap(bmp, x * 30, y * 30, 30, 30, 0, 0, 64, 64, c4d.BMP_NORMAL)
        # self.DrawText(f'({x},{y})', x * 30, y * 30)

    def drawSquares(self):
        for key, value in enumerate(self.squareId):
            if key in self.showId and value is not None:
                self.drawCell(key, value)

    @staticmethod
    def GetRandomNext():
        args = random.choice([i_list, z_left, z_right, o_list, t_list, l_left, l_right])
        icon_id = random.choice(icons)
        status = random.choice([i for i in range(len(args))])
        return {'status': status, 'icon': icon_id, 'all': args}

    @staticmethod
    def ReShapeLine2Multi(lst):
        temp = copy.deepcopy(lst)
        return [temp[i * 10:i * 10 + 10] for i in range(20)]

    @staticmethod
    def ReShapeMulti2Line(lst):
        temp = []
        for value in lst:
            temp.append(value)
        return temp

    @staticmethod
    def MapShowIdFromLine(showId):
        all_lst = []
        for j in range(20):
            lst = []
            for i in range(10):
                temp = 10 * j + i
                if temp in showId:
                    lst.append(temp)
                else:
                    lst.append(None)
            all_lst.append(lst)
        return all_lst

    def InputEvent(self, msg):
        self.SetTimer(self.speed)

        if msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_KEYBOARD:
            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_ESC:
                self.GetDialog.Close()

            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_DOWN:
                map_showId = self.MapShowIdFromLine(self.showId)
                map_squareId = self.ReShapeLine2Multi(self.squareId)
                temp = self.GetActorIndexByMoveDown()
                if temp is not None:
                    self.showId += self.actor_status
                    self.showId = list(set(self.showId))
                    self.ChangeIconInSquare(self.actor['icon'], *temp)
                    self.check = []
                else:
                    self.actor = copy.deepcopy(self.next)
                    self.next = self.GetRandomNext()
                    self.actor_status = self.GetActorNowByStatus(self.actor['status'], *self.actor['all'])

                    # TODO:清理
                    temp_showId, temp_squareId, times = [], [], 0
                    for index in range(20):
                        if index not in self.check:
                            temp_showId.append(map_showId[index])
                            temp_squareId.append(map_squareId[index])
                        else:
                            if map_showId[index].count(None) == 0:
                                times += 1
                                temp_showId.insert(0, [None, None, None, None, None, None, None, None, None, None])
                                temp_squareId.insert(0, [None, None, None, None, None, None, None, None, None, None])
                            else:
                                temp_showId.append(map_showId[index])
                                temp_squareId.append(map_squareId[index])

                    self.showId = []
                    for j,row in enumerate(temp_showId):
                        for i,value in enumerate(row):
                            if value is not None:
                                self.showId.append(j * 10 + i)
                    self.squareId = []
                    for row in temp_squareId:
                        for value in row:
                            self.squareId.append(value)
                    if self.magic:
                        self.squareId = [None for i in range(100)] + self.squareId[100:]
                        self.showId = [show for show in self.showId if show > 99]
                        self.magic = False
                    self.score += 100 * times
                    self.level = self.score // 1200 + 1
                    self.speed = 1000 // self.level


            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_LEFT:
                temp = self.GetActorIndexByMoveLeftRight('left')
                if temp is not None:
                    self.ChangeIconInSquare(self.actor['icon'], *temp)

            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_RIGHT:
                temp = self.GetActorIndexByMoveLeftRight('right')
                if temp is not None:
                    self.ChangeIconInSquare(self.actor['icon'], *temp)

            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_UP:
                temp = self.GetActorIndexByTurn()
                if temp is not None:
                    self.actor['status'] = temp[0]
                    self.ChangeIconInSquare(self.actor['icon'], *temp[1])
        self.Redraw()

    def Timer(self, msg):
        map_showId = self.MapShowIdFromLine(self.showId)
        map_squareId = self.ReShapeLine2Multi(self.squareId)
        temp = self.GetActorIndexByMoveDown()
        if temp is not None:
            self.showId += self.actor_status
            self.showId = list(set(self.showId))
            self.ChangeIconInSquare(self.actor['icon'], *temp)
            self.check = []
        else:
            self.actor = copy.deepcopy(self.next)
            self.next = self.GetRandomNext()
            self.actor_status = self.GetActorNowByStatus(self.actor['status'], *self.actor['all'])

            # TODO:验证结束
            for st in self.actor_status:
                if self.squareId[st] is not None:
                    if self.chance == 0:
                        c4d.gui.MessageDialog(f"挑战失败！得分纪录：\nLevel：{self.level}\nScore：{self.score}", type=c4d.GEMB_OK)
                        self.GetDialog.Close()
                    else:
                        self.chance -= 1
                        self.magic = True
            # TODO:清理
            temp_showId, temp_squareId, times = [], [], 0
            for index in range(20):
                if index not in self.check:
                    temp_showId.append(map_showId[index])
                    temp_squareId.append(map_squareId[index])
                else:
                    if map_showId[index].count(None) == 0:
                        times += 1
                        temp_showId.insert(0, [None, None, None, None, None, None, None, None, None, None])
                        temp_squareId.insert(0, [None, None, None, None, None, None, None, None, None, None])
                    else:
                        temp_showId.append(map_showId[index])
                        temp_squareId.append(map_squareId[index])

            self.showId = []
            for j, row in enumerate(temp_showId):
                for i, value in enumerate(row):
                    if value is not None:
                        self.showId.append(j * 10 + i)
            self.squareId = []
            for row in temp_squareId:
                for value in row:
                    self.squareId.append(value)
            if self.magic:
                self.squareId = [None for i in range(100)] + self.squareId[100:]
                self.showId = [show for show in self.showId if show > 99]
                self.magic = False
            self.score += 100 * times
            self.level = self.score // 1200 + 1
            self.speed = 1000 // self.level
        self.Redraw()



    def drawInfo(self, x1, y1, x2, y2, msg):
        x0 = x1 + 30 * 10 + 4
        h = self.DrawGetFontHeight()
        next_w = self.DrawGetTextWidth('NEXT')
        score_w = self.DrawGetTextWidth('SCORE')
        score_value_w = self.DrawGetTextWidth(f'{self.score}')
        level_w = self.DrawGetTextWidth('LEVEL')
        level_value_w = self.DrawGetTextWidth(f'{self.level}')
        chance_w = self.DrawGetTextWidth('CHANCE')
        chance_value_w = self.DrawGetTextWidth(f'{self.chance}')

        next_posX = int((x2 - x0 - next_w) * 0.5 + x0)
        next_posY = int(y1 + 20)
        self.DrawSetTextCol(self.color * 5, self.color * 1.2)
        self.DrawSetFont(c4d.FONT_STANDARD)
        self.DrawText('NEXT', next_posX, next_posY)

        # TODO:绘制next图形
        status, icon_id, args = self.next['status'], self.next['icon'], self.next['all']
        w = len(args[int(status)][0]) * 20
        next_bmp_posX = int((x2 - x0 - w) * 0.5 + x0)
        next_bmp_posY = next_posY + 30
        bmp = c4d.bitmaps.InitResourceBitmap(icon_id)
        for j, row in enumerate(args[status]):
            for i, sq in enumerate(row):
                if sq:
                    self.DrawBitmap(bmp, next_bmp_posX + i * 20, next_bmp_posY + 20 * j, 20, 20, 0, 0, 64, 64,
                                    c4d.BMP_NORMAL)

        level_posX = int((x2 - x0 - level_w) * 0.5 + x0)
        level_posY = next_posY + 300
        self.DrawText('LEVEL', level_posX, level_posY)
        level_value_posX = int((x2 - x0 - level_value_w) * 0.5 + x0)
        self.DrawText(f'{self.level}', level_value_posX, level_posY + h + 10)

        score_posX = int((x2 - x0 - score_w) * 0.5 + x0)
        score_posY = level_posY + h + 40
        self.DrawText('SCORE', score_posX, score_posY)
        score_value_posX = int((x2 - x0 - score_value_w) * 0.5 + x0)
        self.DrawText(f'{self.score}', score_value_posX, score_posY + h + 10)

        chance_posX = int((x2 - x0 - chance_w) * 0.5 + x0)
        chance_posY = score_posY + h + 40
        self.DrawText('CHANCE', chance_posX, chance_posY)
        chance_value_posX = int((x2 - x0 - chance_value_w) * 0.5 + x0)
        self.DrawText(f'{self.chance}', chance_value_posX, chance_posY + h + 10)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        self.OffScreenOn()
        self.SetClippingRegion(x1, y1, x2, y2)
        # 绘制窗口底色
        self.DrawSetPen(self.color * 1.2)
        self.DrawRectangle(x1, y1, x2, y2)
        # 绘制积木窗口
        self.DrawSetPen(self.color)
        self.DrawRectangle(x1, y1, x1 + 30 * 10, y2)

        # TODO:绘制积木
        self.drawSquares()
        # 绘制信息
        self.drawInfo(x1, y1, x2, y2, msg)
        self.DrawSetPen(self.color * 1.5)
        self.DrawFrame(x1, y1, x1 + 30 * 10, y2, lineWidth=2.0, lineStyle=c4d.LINESTYLE_NORMAL)
        return True


class MyDialog(c4d.gui.GeDialog):
    def __init__(self,doc):
        super().__init__()
        self.doc = doc
        self.area = iconArea(self,self.doc)

    def CreateLayout(self):
        self.SetTitle("C4D方块")
        self.AddUserArea(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        self.AttachUserArea(self.area, 1000)
        return True

class Tetris(c4d.plugins.CommandData):
    PLUGIN_ID = 1061856
    PLUGIN_NAME = 'Tetris for C4D'
    PLUGIN_INFO = 0
    PLUGIN_ICON = load_bitmap('res/icons/Tetris.tif')
    PLUGIN_HELP = 'After launching the plug-in, click the window to officially start'

    def __init__(self):
        self.dialog = None

    def Register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, self.PLUGIN_INFO, self.PLUGIN_ICON,
            self.PLUGIN_HELP, self)

    def Execute(self, doc):
        self.dialog = MyDialog(doc)
        self.dialog.Open(dlgtype=c4d.DLG_TYPE_MODAL, xpos=- 2, ypos=- 2, defaultw=300 + 150, defaulth=600 + 45)
        return True

if __name__ == '__main__':
    Tetris().Register()

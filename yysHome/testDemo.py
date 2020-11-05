import win32api, win32con, win32gui, win32ui
from PIL import Image
import aircv as ac
import time
import threading, numpy as np

from ctypes import windll

imsrc = None


def window_capture_image(handles=None):
    """

    :param width:
    :param height:
    :param hwnd:
    :return: 返回PIL.IMAGE对象
    """

    left, top, right, bot = win32gui.GetWindowRect(handles)
    width = right - left
    height = bot - top
    hwndDC = win32gui.GetWindowDC(handles)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    BitMap = win32ui.CreateBitmap()
    BitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(BitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    bmpinfo = BitMap.GetInfo()
    bmpstr = BitMap.GetBitmapBits(True)
    ###生成图像
    im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(BitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(handles, hwndDC)
    # if im_gray:
    #     im_PIL = im_PIL.convert('L')
    #     im_PIL = np.array(im_PIL)
    #     return im_PIL
    # im_PIL.save(filename)
    img = np.array(im_PIL)

    return img


def matchImg(imsrc, imgobj, confidencevalue=0.7):  # imgsrc=原始图像，imgobj=待查找的图片
    # imsrc = ac.imread(imgsrc)
    imobj = ac.imread(imgobj)
    match_result = ac.find_template(imsrc, imobj, confidencevalue)
    if match_result is not None:
        match_result['shape'] = (imsrc.shape[1], imsrc.shape[0])  # 0为高，1为宽
        x, y = match_result.get("result")
        x, y = int(x), int(y)
        match_result["result"] = (x, y)
    return match_result


def mouse_click(x, y, hwnd):
    import time
    long_position = win32api.MAKELONG(x, y)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
    time.sleep(0.02)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)


def zhandou(imgsrc, gouliang=None, qiehuan=None, hwnd=None):
    flag = "准备"
    count = 0
    max_size = None
    start = 0
    next = 0
    global imsrc
    while flag:
        if flag == "准备":

            zhunbei = matchImg(imsrc=imsrc, imgobj="img/fight/zhunbei.png")
            fanhui2 = matchImg(imsrc=imsrc, imgobj="img/fight/fanhui.png")
            if zhunbei:
                time.sleep(0.5)
                fanhui = matchImg(imsrc=imsrc, imgobj="img/fight/fanhui.png")
                if fanhui:
                    # if qiehuan:
                    #     print("狗粮满级")
                    #     gouLiang(1)
                    #     gouLiang(2)
                    x, y = zhunbei.get("result")
                    x = x + random.randint(1, 10)
                    y = y - random.randint(1, 10)
                    mouse_click(x, y, hwnd)
                    print("返回ICON", fanhui)
                    flag = "战斗开始"

            yizhunbei = matchImg(imsrc=imsrc, imgobj="img/fight/yizhunbei.png")
            if yizhunbei:
                flag = "战斗开始"
            count += 1
            yizhunbei = matchImg(imsrc=imsrc, imgobj="img/fight/yizhunbei.png")
            if yizhunbei:
                print("找到已准备")
                flag = "战斗开始"
            if count > 7 and not yizhunbei:
                break
        if flag == "战斗开始":
            shengli = matchImg(imsrc=imsrc, imgobj="img/fight/shengli.png", confidencevalue=0.5)
            if shengli:
                x, y = shengli.get("result")
                x = x + random.randint(10, 30)
                y = y + random.randint(10, 30)
                max_size = matchImg(imsrc=imsrc, imgobj="img/gouliang/gouliang20.png", confidencevalue=0.5)
                print(max_size)
                if max_size:
                    x, y = max_size.get("result")
                    x = x + random.randint(10, 30)
                    y = y + random.randint(10, 30)
                    mouse_click(x, y, hwnd)
                time.sleep(1)
                mouse_click(x, y, hwnd)
                flag = "结算"
            time.sleep(0.2)
            start += 1
            biaoqian = matchImg(imsrc=imsrc, imgobj="img/fight/biaoqian.png", confidencevalue=0.5)
            if not biaoqian:
                start = 0
            if start > 50 and not biaoqian:
                flag = "准备"
                start = 0

        if flag == "结算":
            jiesuan = matchImg(imsrc=imsrc, imgobj="img/fight/jiesuan.png", confidencevalue=0.8)
            if jiesuan:
                x, y = jiesuan.get("result")
                x = x + random.randint(10, 30)
                y = y - random.randint(10, 30)
                mouse_click(x, y, hwnd)
                flag = "继续"
        if flag == "继续":
            time.sleep(2)
            jixu = matchImg(imsrc=imsrc, imgobj="img/fight/jixu.png", confidencevalue=0.7)
            if jixu:
                x, y = jixu.get("result")
                x = x + random.randint(10, 30)
                y = y - random.randint(10, 30)
                mouse_click(x, y, hwnd)
                flag = None
                next += 1
                if max_size and gouliang:
                    print("返回狗粮")
                    max_size = None
                    return True
            # if next==2:
            #         flag = None

        time.sleep(0.5)
        print(flag)


def set_window_size(targetTitle):
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList)
    for hwnd in hWndList:
        clsname = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        if (title.find(targetTitle) >= 0):  # 调整目标窗口到坐标(600,300),大小设置为(1220,717)
            # win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 600,300,1220,717, win32con.SWP_SHOWWINDOW)
            win32gui.MoveWindow(hwnd, 20, 20, 1220, 717, True)


def home_thread(handles):
    global imsrc
    while True:
        imsrc = window_capture_image(handles=handles)
        time.sleep(0.2)
        selectFuBen(hwnd=handles)


def selectFuBen(hwnd):
    baoxiangwaibu = matchImg(imsrc=imsrc, imgobj="img/fuben/baoxiangwai.png", confidencevalue=0.8)
    if baoxiangwaibu:
        x, y = baoxiangwaibu.get("result")
        x = x + random.randint(10, 30)
        y = y + random.randint(10, 20)
        mouse_click(x, y, hwnd)
        time.sleep(1.8)
        queding = matchImg(imsrc=imsrc, imgobj="img/fuben/queding.png", confidencevalue=0.8)
        if queding:
            x, y = queding.get("result")
            x = x + random.randint(10, 30)
            y = y + random.randint(10, 20)
            mouse_click(x, y, hwnd)

    shibazhang = matchImg(imsrc=imsrc, imgobj="img/fuben/dishibazhang.png", confidencevalue=0.9)

    if shibazhang:
        x, y = shibazhang.get("result")
        x = x + random.randint(10, 30)
        y = y + random.randint(10, 20)
        mouse_click(x, y, hwnd)
    tansuo = matchImg(imsrc=imsrc, imgobj="img/fuben/tansuo.png", confidencevalue=0.8)
    if tansuo:
        x, y = tansuo.get("result")
        x = x + random.randint(10, 30)
        y = y - random.randint(10, 20)
        mouse_click(x, y, hwnd)


def yysFuBen(status=None, hwnd=None):
    count = 0
    check_end = 0
    max_leve = None
    while True:
        gongji = matchImg(imsrc=imsrc, imgobj="img/fuben/gongji.png", confidencevalue=0.8)
        bossGongji = matchImg(imsrc=imsrc, imgobj="img/fuben/bossgongji.png", confidencevalue=0.8)
        if gongji and not bossGongji:
            x, y = gongji.get("result")
            x = x + random.randint(1, 10)
            y = y + random.randint(1, 10)
            mouse_click(x, y, hwnd=hwnd)
            zhandou(imgsrc=imsrc, hwnd=hwnd)
            # if max_leve:
            #     max_leve = zhandou(gouliang=True, qiehuan=max_leve)
            #     max_leve = None
            # if not max_leve:
            #     max_leve = zhandou(gouliang=True)

            count = 0
        if bossGongji:
            x, y = bossGongji.get("result")
            mouse_click(x, y, hwnd=hwnd)
            zhandou(imgsrc=imsrc, hwnd=hwnd)
            #
            # if max_leve:
            #     max_leve = zhandou(gouliang=True, qiehuan=max_leve)
            # if not max_leve:
            #     max_leve = zhandou(gouliang=True)

            count = 0
        if count > 7:
            cishu = matchImg(imsrc=imsrc, imgobj="img/fuben/cishu.png", confidencevalue=0.8)
            if cishu:
                x, y = cishu.get("result")
                x = x - random.randint(10, 20)
                y = y - random.randint(20, 50)
                mouse_click(x, y, hwnd)
                time.sleep(2)
                # win32gui.SendMessage(subhandle, win32con.WM_LBUTTONUP, 0, 0)
                #
                # pyautogui.moveTo(cishu[0], cishu[1] - 50, 0.2, pyautogui.easeInQuad)
                # pyautogui.dragTo(cishu[0] - random.randint(400, 700), cishu[1] - 50, duration=0.25)

        baoxiang = matchImg(imsrc=imsrc, imgobj="img/fuben/baoxiang.png", confidencevalue=0.8)
        if baoxiang:
            x, y = baoxiang.get("result")
            x = x + random.randint(10, 20)
            y = y + random.randint(10, 20)
            mouse_click(x, y, hwnd)

            count = 0

        huodejiangli = matchImg(imsrc=imsrc, imgobj="img/fuben/huodejiangli.png", confidencevalue=0.8)
        if huodejiangli:
            x, y = huodejiangli.get("result")
            x = x + random.randint(10, 20)
            y = y + random.randint(10, 20)
            mouse_click(x, y, hwnd)

        count += 1


def yystiaozhan(status=None, hwnd=None):
    count = 0
    check_end = 0
    max_leve = None
    while True:
        gongji = matchImg(imsrc=imsrc, imgobj="img/huodong/tiaozhan.png", confidencevalue=0.8)
        if gongji:
            x, y = gongji.get("result")
            x = x + random.randint(1, 10)
            y = y + random.randint(1, 10)
            mouse_click(x, y, hwnd=hwnd)
            zhandou(imgsrc=imsrc, hwnd=hwnd)

            count = 0

        huodejiangli = matchImg(imsrc=imsrc, imgobj="img/fuben/huodejiangli.png", confidencevalue=0.8)
        if huodejiangli:
            x, y = huodejiangli.get("result")
            x = x + random.randint(10, 20)
            y = y + random.randint(10, 20)
            mouse_click(x, y, hwnd)

        count += 1


if __name__ == '__main__':
    import random

    set_window_size("阴阳师-网易游戏")
    handles = win32gui.FindWindow(None, "阴阳师-网易游戏")
    t = threading.Thread(target=home_thread, args=(handles,))
    t.start()
    time.sleep(1)
    # yysFuBen(hwnd=handles)
    yystiaozhan(hwnd=handles)
    # while True:
    #     zhandou(imsrc,hwnd=handles)

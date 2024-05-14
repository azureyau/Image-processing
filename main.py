import time
import pyautogui
import pygetwindow as gw
from PIL import Image
from PIL import ImageGrab
import numpy as np
import os
import win32api,win32con
from scipy.spatial import distance


class SpecialChar:
    def __init__(self, file_location, bbox, value):
        self.file_location = file_location
        self.bbox = bbox
        self.value = value


WINDOW_NAME = "BlueStacks3"
ACCURACY = 15
WINDOW_LX = 1520
WINDOW_LY = 290
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 750


charlist = (SpecialChar("./characters/x1008.png",
                        (int(WINDOW_LX + WINDOW_WIDTH / 400 * 37),
              int(WINDOW_LY + WINDOW_HEIGHT / 750 * 160),
              int(WINDOW_WIDTH / 400 * 5),
              int(WINDOW_HEIGHT / 750 * 15)), 50),) #1. Character: fanleefa


rank_colors = {
    "white": (193, 175, 165),
    "green": (77, 118, 72),
    "blue": (73,88,117),
    "purple": (115, 67, 118),
    "brown": (158, 102, 62),
    "red": (171, 78, 81),
    "yellow": (160, 115, 36),
    "gold": (207, 165, 75),
    "golden": (233, 210, 106),
    "black": (16, 24, 33)
}
color_level = {
    "white": 50,
    "green": 100,
    "blue": 150,
    "purple": 200,
    "brown": 250,
    "red": 300,
    "yellow": 350,
    "gold": 400,
    "golden": 500,
    "black": 9999
}


def take_screenshot(region=None):
    screenshot = ImageGrab.grab(bbox=region)
    return screenshot


def click(x, y):
    win32api.SetCursorPos((int(x), int(y)))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def click_choice(index):
    click(WINDOW_LX + WINDOW_WIDTH / 400 * (70 + 118 * index),
           WINDOW_LY + WINDOW_HEIGHT / 750 * 170)


def click_skip():
    click(WINDOW_LX + WINDOW_WIDTH * 0.9,WINDOW_LY +WINDOW_HEIGHT * .83)


def save_screenshot(screenshot, filename='characters/unknown.png'):
    screenshot.save(filename)


def initialize_window(window_name):
    game_window_name = window_name
    game_window = None
    for window in gw.getAllWindows():
        if game_window_name in window.title:
            game_window = window
            break

    if game_window is not None:
        game_window.moveTo(WINDOW_LX, WINDOW_LY)
        game_window.resizeTo(WINDOW_WIDTH, WINDOW_HEIGHT)
        game_window.activate()
        return game_window
    return None

def get_region(index):
    return WINDOW_LX + WINDOW_WIDTH / 400 * (30 + 118 * index),\
           WINDOW_LY + WINDOW_HEIGHT / 750 * 140,\
           WINDOW_LX + WINDOW_WIDTH / 400 * 135 + WINDOW_WIDTH / 400 * 118 * index,\
           WINDOW_LY + WINDOW_HEIGHT / 750 * 255


def get_region_for_char(index):
    return WINDOW_LX + WINDOW_WIDTH / 400 * (60 + 118 * index),\
           WINDOW_LY + WINDOW_HEIGHT / 750 * 160,\
           WINDOW_LX + WINDOW_WIDTH / 400 * (95 + 118 * index),\
           WINDOW_LY + WINDOW_HEIGHT / 750 * 255


def get_xy_width_height(index):
    return int(WINDOW_LX + WINDOW_WIDTH / 400 * (58 + 118 * index)),\
           int(WINDOW_LY + WINDOW_HEIGHT / 750 * 158),\
           int(WINDOW_WIDTH / 400 * 37),\
           int(WINDOW_HEIGHT / 750 * 99)


def capture_picture():
    folder_path = "./characters"
    png_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
    images = [Image.open(os.path.join(folder_path, file)) for file in png_files]
    found = [False] * 3
    for i in range(0, 3):
        for image in images:
            try:
                if pyautogui.locateOnScreen(image, region=get_xy_width_height(i), confidence=0.70):
                    print("I can see it in {}",i)
                    found[i] = True
                    image.save(f"./save{i}.png")
                    break
            except:
                pass
    for i in range(0, 3):
        if not found[i]:
            character = take_screenshot(get_region_for_char(i))
            filename = f"characters/tobeadded/{i}.png"
            save_screenshot(character, filename)
            print("saved {}", i)

def check_rank_by_clr(index):
    i = 0
    bbox_list = [
        (WINDOW_LX + WINDOW_WIDTH / 400 * (41 + 118 * index), WINDOW_LY + WINDOW_HEIGHT / 750 * 161,
         WINDOW_LX + WINDOW_WIDTH / 400 * (49 + 118 * index), WINDOW_LY + WINDOW_HEIGHT / 750 * 175),
        (WINDOW_LX + WINDOW_WIDTH / 400 * (116 + 118 * index), WINDOW_LY + WINDOW_HEIGHT / 750 * 161,
         WINDOW_LX + WINDOW_WIDTH / 400 * (122 + 118 * index), WINDOW_LY + WINDOW_HEIGHT / 750 * 170),
        (WINDOW_LX + WINDOW_WIDTH / 400 * (41 + 118 * index), WINDOW_LY + WINDOW_HEIGHT / 750 * 161,
         WINDOW_LX + WINDOW_WIDTH / 400 * (49 + 118 * index), WINDOW_LY + WINDOW_HEIGHT / 750 * 170)
    ]
    done = False
    extra = 0
    while not done and i < 3:
        done = False
        extra = 0
        special_result = check_sepecial_char(index)
        if special_result:
            image = special_result[0]
            extra = special_result[1]
            done = True
        else:
            image = ImageGrab.grab(bbox=(bbox_list[i]))
        image = image.resize((1, 1), resample=Image.Resampling.LANCZOS)
        image_np = np.array(image)
        image_pixels = image_np[0, :, :]
        average_color = np.mean(image_pixels, axis=0)
        result = find_closest_color(average_color)
        if result[1] <= ACCURACY:
            done = True
        i = i + 1
    print(f"option {index}'s color and diff:,{result}")
    if result[1] > ACCURACY * 1.5 and result[0] != 'black':
        return color_level['golden']
    return color_level[result[0]] + extra


def find_closest_color(average_color):
    closest_color_name = None
    closest_distance = float("inf")

    for color_name, rgb_values in rank_colors.items():
        dist = distance.euclidean(average_color, rgb_values)

        if dist < closest_distance:
            closest_distance = dist
            closest_color_name = color_name

    return closest_color_name, closest_distance


def check_vslogo():
    vs_logo = Image.open("icon/vslogo.png")
    vs_logo_bbox = (int(WINDOW_LX + WINDOW_WIDTH / 400 * 70),
                   int(WINDOW_LY + WINDOW_HEIGHT / 750 * 310),
                   int(WINDOW_WIDTH / 400 * 220),
                   int(WINDOW_HEIGHT / 750 * 227))

    try:
        if pyautogui.locateOnScreen(vs_logo, region=vs_logo_bbox, confidence=0.85):  # grayscale=False
            return True
    except:
        pass
    return False


def compare_three():
    result = 0
    value = 999
    candidate = []
    for i in range(0, 3):
        current_value = check_rank_by_clr(i)
        if current_value < value:
            candidate.clear()
            candidate.append(i)
            value = current_value
        elif current_value == value:
            candidate.append(i)
        # print(f"value={value}, current_value={current_value}")
    if len(candidate) == 1 or value <= 300:
        return candidate[0]
    # print(candidate)
    return compare_characters(candidate)


def compare_characters(candidates):
    folder_path = "./characters"
    png_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
    images = [Image.open(os.path.join(folder_path, file)) for file in png_files]
    for image in images:
        image.save("read.png")
        for i in candidates:
            try:
                if pyautogui.locateOnScreen(image, region=get_xy_width_height(i), confidence=0.70):
                     return i
            except:
                pass
    capture_picture()
    return candidates[0]


def check_sepecial_char(index):
    for i in range(0, len(charlist)):
        try:
            image = Image.open(charlist[i].file_location)
            if pyautogui.locateOnScreen(image, region=get_xy_width_height(index), confidence=0.80):
                result = ImageGrab.grab(bbox=(charlist[i].bbox[0] + 118 * index,\
                                              charlist[i].bbox[1],\
                                              charlist[i].bbox[2] + charlist[i].bbox[0] + 118 * index,\
                                              charlist[i].bbox[3] + charlist[i].bbox[1]))
                return result, charlist[i].value
        except:
            pass
    return None


def check_health():
    health_bar = 1
    blood_level = {0.8: (int(WINDOW_LX + WINDOW_WIDTH / 400 * 332), int(WINDOW_LY + WINDOW_HEIGHT / 750 * 740)),\
                   0.4: (int(WINDOW_LX + WINDOW_WIDTH / 400 * 175), int(WINDOW_LY + WINDOW_HEIGHT / 750 * 740))}
    screenshot = ImageGrab.grab()
    for percent, position in blood_level.items():
        pixel_color = screenshot.getpixel(position)
        print(f"current_health: {percent}")# , color: {pixel_color}")
        dist = distance.euclidean(pixel_color, (168, 41, 41))
        if dist < 15:
            break
        else:
            health_bar = percent
    return health_bar


def click_item(choice):
    image1 = Image.open(f"icon/{choice}.png")
    image2 = Image.open(f"icon/{choice}2.png")
    print(f"looking for {choice}:", end=' ')
    try:
        if pyautogui.locateOnScreen(image2, region=(int(WINDOW_LX + WINDOW_WIDTH / 400 * 329),
                   int(WINDOW_LY + WINDOW_HEIGHT / 750 * 349),
                   int(WINDOW_WIDTH / 400 * 60),
                   int(WINDOW_HEIGHT / 750 * 122)), confidence=0.9):
            click_item_option(2)
            print("found 2")
            return 2
    except:
        pass
    try:
        if pyautogui.locateOnScreen(image1, region=(int(WINDOW_LX + WINDOW_WIDTH / 400 * 329),
                                                int(WINDOW_LY + WINDOW_HEIGHT / 750 * 349),
                                                int(WINDOW_WIDTH / 400 * 60),
                                                int(WINDOW_HEIGHT / 750 * 122)), confidence=0.9):
            click_item_option(1)
            print("found 1")
            return 1
    except:
        pass
    print("None")
    return 0


def click_item_option(num):
    click(WINDOW_LX + WINDOW_WIDTH / 400 * 359, WINDOW_LY + WINDOW_HEIGHT / 750 * 370 + 60 * (num - 1))


# main start here
turn = 0
damage_count = 6
critical_count = 0
cost = 3
game_window = initialize_window(WINDOW_NAME)
time.sleep(0.5)
while gw.getActiveWindow() == game_window and check_vslogo():
    # capture_picture()
    clicked = 0
    turn += 1
    health = check_health()
    print(f"turn:{turn}, cost:{cost}, critical:{critical_count}, damage: {damage_count}, current health: {health}")
    if turn > 1:
        if turn > 4 and (health < 0.5 or (health < 0.9 and turn > 10)):
            clicked = click_item("recover")
        if not clicked: # did not click recover
            if (turn < 10 or critical_count <= 12 or critical_count < turn * 2) and critical_count < 30 and cost - turn < 10:
                clicked = click_item("critical")
                critical_count += clicked
            if clicked == 0 and cost - turn < 10 and (damage_count < 4 or damage_count < critical_count * 3):
                clicked = click_item("damage")
                damage_count += clicked
        cost += clicked
    choice = compare_three()
    print(f"choice: {choice}")
    click_choice(choice)
    time.sleep(0.4)
    for i in range(0, 5):
        click_skip()
        time.sleep(0.4)
    click(WINDOW_LX + WINDOW_WIDTH / 400 * 80, WINDOW_LY + WINDOW_HEIGHT / 750 * 330)
    time.sleep(0.7)
    click_skip()
    time.sleep(0.5)
    click_skip()
    time.sleep(0.5)
print("--------------summary---------------")
print(f"turn:{turn}, cost:{cost}, critical:{critical_count}, damage: {damage_count}")

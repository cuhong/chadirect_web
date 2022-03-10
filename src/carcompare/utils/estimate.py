import requests
import os
from django.conf import settings

from PIL import Image, ImageDraw, ImageFont

def parse_manager_contact(manager_contact):
    manager_contact = "".join([s for s in manager_contact if s.isdigit()])
    return f"{manager_contact[:3]}-{manager_contact[3:7]}-{manager_contact[7:]}"

data = {
    "manager_name": "최용성",
    "manager_contact": "010-2484-6313",
    "insured_name": "최용성",
    "insured_birthdate": "1961-06-01",
    "car_name": "X1 20i xDrive Xline",
    "car_detail": "차명코드 : 93BN2, 차종 : 승용중형B",
    "start_date": "2022-02-01",
    "driver_range": "가족한정",
    "min_driver_birthdate": "1986-09-06",
    "insure_1": "현대해상 다이렉트",
    "insure_1_premium": "1,226,707",
    "insure_1_memo": None,
    "insure_2": "DB손해보험 다이렉트",
    "insure_2_premium": "914,028",
    "insure_2_memo": "최저",
    "insure_3": "KB손해보험 다이렉트",
    "insure_3_premium": "930,204",
    "insure_3_memo": None,
    "insure_4": "한화손해보험 다이렉트",
    "insure_4_premium": "1,264,425",
    "insure_4_memo": None,
    "p_1": "의무",
    "p_2": "5억",
    "p_3": "무한",
    "p_4": "1억/5천",
    "p_5": "5억",
    "p_6": "가입",
    "p_7": "고급형",
    "p_8": "미가입",
}

def generate_estimate_image(data):
    base_estimate_image_path = os.path.join(settings.BASE_DIR, 'carcompare', 'data', 'estimate_base.png')

    font_size = 90
    small_font_size = 60

    kor_font = ImageFont.truetype(
        os.path.join(settings.BASE_DIR, 'carcompare/data/Noto_Sans_KR/NotoSansKR-Bold.otf'), font_size
    )

    kor_font_small = ImageFont.truetype(
        os.path.join(settings.BASE_DIR, 'carcompare/data/Noto_Sans_KR/NotoSansKR-Bold.otf'), small_font_size
    )

    kor_font_small_light = ImageFont.truetype(
        os.path.join(settings.BASE_DIR, 'carcompare/data/Noto_Sans_KR/NotoSansKR-Regular.otf'), small_font_size
    )
    color_black = (0, 0, 0)
    color_black_transparent = (0, 0, 0, 15)
    color_red = (255, 0, 0)

    base_image = Image.open(base_estimate_image_path).convert('RGBA')

    base_image = base_image.copy()
    draw = ImageDraw.Draw(base_image)

    text_position_list = [
        {"attr_name": "manager_name", "placeholder_position": (1002, 992, 2940, 1163), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "manager_contact", "placeholder_position": (3912, 992, 4863, 1163), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "insured_name", "placeholder_position": (1002, 1904, 2940, 2137), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "insured_birthdate", "placeholder_position": (3912, 1904, 4863, 2137), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "car_name", "placeholder_position": (1002, 2141, 2940, 2275), "color": color_black,
         "align": "center", "font": kor_font_small},
        # {"attr_name": "car_name", "placeholder_position": (1002, 2141, 2940, 2406), "color": color_black, "align": "center", "font": kor_font_small},
        {"attr_name": "car_detail", "placeholder_position": (1002, 2275, 2940, 2406), "color": color_black,
         "align": "center", "font": kor_font_small_light},
        {"attr_name": "start_date", "placeholder_position": (3912, 2141, 4863, 2406), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "driver_range", "placeholder_position": (1002, 2410, 2940, 2629), "color": color_red,
         "align": "center", "font": kor_font},
        {"attr_name": "min_driver_birthdate", "placeholder_position": (3912, 2410, 4863, 2629), "color": color_red,
         "align": "center", "font": kor_font},
        {"attr_name": "insure_1", "placeholder_position": (135, 3337, 2940, 3590), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "insure_1_premium", "placeholder_position": (2945, 3337, 3912, 3590), "color": color_black,
         "align": "right", "font": kor_font},
        {"attr_name": "insure_1_memo", "placeholder_position": (3913, 3337, 4863, 3590), "color": color_red,
         "align": "center", "font": kor_font},

        {"attr_name": "insure_2", "placeholder_position": (135, 3596, 2940, 3845), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "insure_2_premium", "placeholder_position": (2945, 3596, 3912, 3845), "color": color_black,
         "align": "right", "font": kor_font},
        {"attr_name": "insure_2_memo", "placeholder_position": (3913, 3596, 4863, 3845), "color": color_red,
         "align": "center", "font": kor_font},

        {"attr_name": "insure_3", "placeholder_position": (135, 3850, 2940, 4122), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "insure_3_premium", "placeholder_position": (2945, 3850, 3912, 4122), "color": color_black,
         "align": "right", "font": kor_font},
        {"attr_name": "insure_3_memo", "placeholder_position": (3913, 3850, 4863, 4122), "color": color_red,
         "align": "center", "font": kor_font},

        {"attr_name": "insure_4", "placeholder_position": (135, 4125, 2940, 4400), "color": color_black,
         "align": "center", "font": kor_font},
        {"attr_name": "insure_4_premium", "placeholder_position": (2945, 4125, 3912, 4400), "color": color_black,
         "align": "right", "font": kor_font},
        {"attr_name": "insure_4_memo", "placeholder_position": (3913, 4125, 4863, 4400), "color": color_red,
         "align": "center", "font": kor_font},

        {"attr_name": "p_1", "placeholder_position": (1002, 5082, 2940, 5239), "color": color_black, "align": "center",
         "font": kor_font},
        {"attr_name": "p_2", "placeholder_position": (3912, 5082, 4863, 5239), "color": color_black, "align": "center",
         "font": kor_font},
        {"attr_name": "p_3", "placeholder_position": (1002, 5251, 2940, 5419), "color": color_black, "align": "center",
         "font": kor_font},
        {"attr_name": "p_4", "placeholder_position": (3912, 5251, 4863, 5419), "color": color_black, "align": "center",
         "font": kor_font},

        {"attr_name": "p_5", "placeholder_position": (1002, 5427, 2940, 5595), "color": color_black, "align": "center",
         "font": kor_font},
        {"attr_name": "p_6", "placeholder_position": (3912, 5427, 4863, 5595), "color": color_black, "align": "center",
         "font": kor_font},
        {"attr_name": "p_7", "placeholder_position": (1002, 5607, 2940, 5769), "color": color_black, "align": "center",
         "font": kor_font},
        {"attr_name": "p_8", "placeholder_position": (3912, 5607, 4863, 5769), "color": color_black, "align": "center",
         "font": kor_font},
    ]

    # manager_name_position = (x_start, y_start, x_end, y_end)
    pad = font_size / 5

    data['manager_contact'] = parse_manager_contact(data.get('manager_contact'))

    for text_position in text_position_list:
        placeholder_position = text_position.get('placeholder_position')
        attr_name = text_position.get('attr_name')
        text_value = data.get(attr_name)
        # font = data.get('font')
        font = kor_font
        if text_value is None:
            continue
        align = text_position.get('align', 'center')
        text_dimension = draw.textsize(text_value, font=font, spacing=0)
        if align == "right":
            position_x = placeholder_position[2] - text_dimension[0] - pad * 2
        else:
            position_x = (placeholder_position[0] + placeholder_position[2] - text_dimension[0]) / 2
        draw.text(
            (
                position_x,
                (placeholder_position[1] + placeholder_position[3] - text_dimension[1]) / 2 - pad,
            ), text_value, fill=text_position.get('color'), font=font, spacing=0
        )

    # base_image.show()
    return base_image
#
# base_image = generate_estimate_image(data)
#
# base_image.show()
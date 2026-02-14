import os
import requests
import arcade
from config import *


class MapApp(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Maps App - Версия 8")
        self.lon = DEFAULT_LON
        self.lat = DEFAULT_LAT
        self.spn = DEFAULT_SPN
        self.theme = "light"
        self.marker = None
        self.address = ""
        self.search_text = ""
        self.search_input_active = False
        self.background = None
        self.get_image()

    def on_draw(self):
        self.clear()
        if self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.rect.XYWH(self.width/2, self.height /
                                 2, self.width, self.height)
            )

        arcade.draw_text(f"Lon: {float(self.lon):.4f}",
                         10, 110, arcade.color.BLACK, 14)
        arcade.draw_text(f"Lat: {float(self.lat):.4f}",
                         10, 90, arcade.color.BLACK, 14)
        arcade.draw_text(f"SPN: {self.spn:.4f}", 10,
                         70, arcade.color.BLACK, 14)
        arcade.draw_text(f"Тема: {self.theme}", 10, 50, arcade.color.BLACK, 14)
        arcade.draw_text("PgUp/PgDown - зум", 10, 30, arcade.color.BLACK, 12)
        arcade.draw_text("Стрелки - движение, T - тема",
                         10, 10, arcade.color.BLACK, 12)

        arcade.draw_rect_filled(arcade.rect.XYWH(
            90, 585, 180, 30), arcade.color.LIGHT_GRAY)

        if len(self.search_text) > 18:
            line1 = self.search_text[:18]
            line2 = self.search_text[18:]
            arcade.draw_rect_filled(arcade.rect.XYWH(
                90, 585, 180, 60), arcade.color.LIGHT_GRAY)
            arcade.draw_text(f">{line1}", 5, 580, arcade.color.BLACK, 12)
            arcade.draw_text(f"{line2}", 5, 565, arcade.color.BLACK, 12)
        else:
            arcade.draw_text(f">{self.search_text}", 5,
                             580, arcade.color.BLACK, 14)

        arcade.draw_rect_filled(arcade.rect.XYWH(
            220, 585, 80, 30), arcade.color.RED)
        arcade.draw_text("СБРОС", 195, 580, arcade.color.WHITE, 14, bold=True)

        arcade.draw_rect_filled(arcade.rect.XYWH(
            135, 530, 270, 45), arcade.color.LIGHT_GRAY)
        arcade.draw_text("АДРЕС:", 5, 525, arcade.color.BLACK, 12, bold=True)

        if self.address:
            if len(self.address) > 35:
                line1 = self.address[:35]
                line2 = self.address[35:]
                arcade.draw_text(line1, 60, 525, arcade.color.BLACK, 10)
                arcade.draw_text(line2, 5, 510, arcade.color.BLACK, 10)
            else:
                arcade.draw_text(self.address, 60, 525, arcade.color.BLACK, 11)
        else:
            arcade.draw_text("(нет объекта)", 60, 525, arcade.color.GRAY, 11)

    def get_image(self):
        self.spn = max(MIN_SPN, min(MAX_SPN, self.spn))
        params = {
            "ll": f"{self.lon},{self.lat}",
            "spn": f"{self.spn},{self.spn}",
            "size": "650,450",
            "l": "map",
            "theme": self.theme,
            "apikey": APIKEY
        }

        if self.marker:
            params["pt"] = f"{self.marker[0]},{self.marker[1]},pm2rdm"

        response = requests.get(
            "https://static-maps.yandex.ru/1.x/", params=params)
        if response.status_code != 200:
            print("Ошибка:", response.status_code)
            return
        with open(MAP_FILE, "wb") as f:
            f.write(response.content)
        self.background = arcade.load_texture(MAP_FILE)

    def search(self):
        if not self.search_text:
            return

        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "geocode": self.search_text,
            "format": "json",
            "apikey": APIKEY_GEO
        }

        try:
            response = requests.get(url, params=params).json()

            members = response['response']['GeoObjectCollection']['featureMember']
            if not members:
                print("Ничего не найдено")
                return

            obj = members[0]['GeoObject']

            pos = obj['Point']['pos'].split()
            self.lon = pos[0]
            self.lat = pos[1]

            self.marker = (self.lon, self.lat)

            try:
                self.address = obj['metaDataProperty']['GeocoderMetaData']['text']
            except:
                self.address = "Адрес не найден"

            self.spn = 0.01

            self.get_image()

        except Exception as e:
            print("Ошибка поиска:", e)

    def reset_search(self):
        self.marker = None
        self.search_text = ""
        self.address = ""
        self.get_image()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.PAGEUP:
            if self.spn > MIN_SPN:
                self.spn /= 1.5
                self.get_image()
        elif key == arcade.key.PAGEDOWN:
            if self.spn < MAX_SPN:
                self.spn *= 1.5
                self.get_image()

        move_x = 0
        move_y = 0
        if key == arcade.key.UP:
            move_y = 1
        elif key == arcade.key.DOWN:
            move_y = -1
        elif key == arcade.key.RIGHT:
            move_x = 1
        elif key == arcade.key.LEFT:
            move_x = -1

        if move_x != 0 or move_y != 0:
            lon_move = self.spn * 0.5 * move_x
            lat_move = self.spn * 0.4 * move_y
            new_lon = float(self.lon) + lon_move
            new_lat = float(self.lat) + lat_move
            if MIN_LON <= new_lon <= MAX_LON:
                self.lon = str(new_lon)
            if MIN_LAT <= new_lat <= MAX_LAT:
                self.lat = str(new_lat)
            self.get_image()

        if key == arcade.key.T:
            if self.search_input_active:
                return
            self.theme = "dark" if self.theme == "light" else "light"
            self.get_image()

        if key == arcade.key.ENTER:
            if not self.search_input_active:
                return
            self.search()

        if key == arcade.key.BACKSPACE:
            if not self.search_input_active:
                return
            self.search_text = self.search_text[:-1]

    def on_text(self, text):
        if text and self.search_input_active:
            self.search_text += text

    def on_mouse_press(self, x, y, button, modifiers):
        if 0 <= x <= 180 and 570 <= y <= 600:
            self.search_input_active = True
        elif 0 <= x <= 180 and 540 <= y <= 600 and len(self.search_text) > 18:
            self.search_input_active = True
        elif 180 <= x <= 260 and 570 <= y <= 600:
            self.reset_search()
        else:
            self.search_input_active = False


def main():
    app = MapApp()
    arcade.run()
    if os.path.exists(MAP_FILE):
        os.remove(MAP_FILE)


if __name__ == "__main__":
    main()

import os
import requests
import arcade
from config import *


class MapApp(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Maps App - Версия 3")
        self.lon = DEFAULT_LON
        self.lat = DEFAULT_LAT
        self.spn = DEFAULT_SPN
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
                         10, 90, arcade.color.BLACK, 14)
        arcade.draw_text(f"Lat: {float(self.lat):.4f}",
                         10, 70, arcade.color.BLACK, 14)
        arcade.draw_text(f"SPN: {self.spn:.4f}", 10,
                         50, arcade.color.BLACK, 14)
        arcade.draw_text("PgUp/PgDown - зум", 10, 30, arcade.color.BLACK, 12)
        arcade.draw_text("Стрелки - движение", 10, 10, arcade.color.BLACK, 12)

    def get_image(self):
        self.spn = max(MIN_SPN, min(MAX_SPN, self.spn))
        params = {
            "ll": f"{self.lon},{self.lat}",
            "spn": f"{self.spn},{self.spn}",
            "size": "650,450",
            "l": "map",
            "apikey": APIKEY
        }
        response = requests.get(
            "https://static-maps.yandex.ru/1.x/", params=params)
        if response.status_code != 200:
            return
        with open(MAP_FILE, "wb") as f:
            f.write(response.content)
        self.background = arcade.load_texture(MAP_FILE)

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


def main():
    app = MapApp()
    arcade.run()
    if os.path.exists(MAP_FILE):
        os.remove(MAP_FILE)


if __name__ == "__main__":
    main()

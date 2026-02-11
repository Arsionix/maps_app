import os
import requests
import arcade
from config import *


class MapApp(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Maps App - Версия 1")
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
                         10, 50, arcade.color.BLACK, 14)
        arcade.draw_text(f"Lat: {float(self.lat):.4f}",
                         10, 30, arcade.color.BLACK, 14)
        arcade.draw_text(f"SPN: {self.spn:.4f}", 10,
                         10, arcade.color.BLACK, 14)

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


def main():
    app = MapApp()
    arcade.run()
    if os.path.exists(MAP_FILE):
        os.remove(MAP_FILE)


if __name__ == "__main__":
    main()

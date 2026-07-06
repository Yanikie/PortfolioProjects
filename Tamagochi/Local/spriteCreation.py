from PIL import Image
import sys
import cv2
import numpy as np

class Sprite:
    def __init__(self,pokedexId:int, generation:int = 0, screenWidth: int = 298, screenHeight: int = 128):
        self.pokedexId = pokedexId
        self.generation = generation
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.sprite = None
    
    def show(self):
        if self.sprite == None:
            return
        self.sprite.show()

    def load(self):
        try:
            self.sprite = Image.open(f"D:/PokemonSprites/sprites/pokemon/{self.pokedexId}.png")
            return True
        except:
            return False

    def outlineSprite(self):
        numpySprite = np.array(self.sprite.convert("L"))
        numpySprite = cv2.adaptiveThreshold(
            numpySprite,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,9,3
        )
        numpySprite = cv2.bitwise_not(numpySprite)
        self.sprite = Image.fromarray(numpySprite)

    def bitmap(self):
        if self.sprite == None: return
        bitmap = self.sprite.convert("1").tobytes()
        print(", ".join(f"0x{b:02X}" for b in bitmap))
    
if __name__ == "__main__":
    sprite = Sprite(1020)
    sprite.load()
    sprite.outlineSprite()
    sprite.show()
    sprite.bitmap()
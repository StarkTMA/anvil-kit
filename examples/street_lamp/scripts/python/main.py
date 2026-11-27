from anvil import ANVIL
from street_lamp import register_street_lamp, register_street_lamp_generation

if __name__ == "__main__":
    lamp = register_street_lamp()
    register_street_lamp_generation(lamp)
    ANVIL.compile()

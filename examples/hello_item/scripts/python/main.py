from anvil import ANVIL

from ruby import register_ruby

if __name__ == "__main__":
    register_ruby()
    ANVIL.compile()

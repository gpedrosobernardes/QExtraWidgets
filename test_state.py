
from PySide6.QtWidgets import QStyleOptionViewItem, QStyle

def test():
    option = QStyleOptionViewItem()
    option.state = QStyle.StateFlag.State_None
    option.state |= QStyle.StateFlag.State_Enabled
    print(f"State: {option.state}")

if __name__ == "__main__":
    test()

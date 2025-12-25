
import sys
import os

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from PyQt6.QtWidgets import QApplication
from ui.tabs.smart_selection import SmartSelectionTab

def test_instantiation():
    app = QApplication(sys.argv)
    try:
        tab = SmartSelectionTab()
        print("SmartSelectionTab instantiated successfully")
    except Exception as e:
        print(f"Error instantiating SmartSelectionTab: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_instantiation()

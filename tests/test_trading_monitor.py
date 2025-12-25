
import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication, QTableWidgetItem
from PyQt6.QtCore import Qt

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ui.tabs.trading_monitor import TradingMonitorTab

class TestTradingMonitor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_stock_selection_updates_label(self):
        tab = TradingMonitorTab()
        
        # Verify initial state
        self.assertEqual(tab.current_stock_label.text(), "未选择股票")
        
        # Simulate click on first row (000001 平安银行)
        # We need to simulate the item click. 
        # Since we connected itemClicked, we can just emit it or call the slot directly if we pass an item.
        # But let's try to emit the signal if possible, or just call the slot to test logic.
        
        # Get the item at 0,0
        item = tab.watchlist_table.item(0, 0)
        self.assertIsNotNone(item)
        
        # Manually trigger the slot (simulating the signal connection)
        tab.on_stock_selected(item)
        
        # Check if label updated
        expected_text = "当前分析: 平安银行 (000001)"
        self.assertEqual(tab.current_stock_label.text(), expected_text)
        
        # Check color/style
        self.assertIn("color: #4CAF50", tab.current_stock_label.styleSheet())

if __name__ == '__main__':
    unittest.main()

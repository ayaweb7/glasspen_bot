import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import main

def test_main_output(capsys):
    """Тест, что main.py выводит ожидаемый текст"""
    main.main()
    captured = capsys.readouterr()
    assert "проект" in captured.out.lower()

if __name__ == "__main__":
    test_main_output()
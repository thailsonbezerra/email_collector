VENV_DIR = venv

install:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && python3 -m pip install --upgrade pip
	. $(VENV_DIR)/bin/activate && pip install -r requirements.txt

run:
	. $(VENV_DIR)/bin/activate && python3 main.py

clean:
	rm -rf output/*
	rm -rf $(VENV_DIR)
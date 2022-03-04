VENV=venv
BIN=$(VENV)/bin

create_venv:
	python3 -m venv $(VENV)

bootstrap: create_venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

format: create_venv
	$(BIN)/pip install black
	$(BIN)/black --config=pyproject.toml --exclude venv .

lint: create_venv
	$(BIN)/pip install flake8
	$(BIN)/flake8 --config=pyproject.toml --exclude venv .

test: bootstrap
	$(BIN)/pip install pytest
	$(BIN)/pytest tests

clean:
	rm -rf $(VENV)


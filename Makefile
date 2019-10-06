.PHONY: build clean

build: .venv

.venv:
	`which python3` -m venv $(CURDIR)/.venv
	$(CURDIR)/.venv/bin/pip install -r requirements.txt

clean:
	rm -rf $(CURDIR)/.venv
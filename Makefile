PYTHON ?= python3

DATASET ?= rx.json

.PHONY: total update-readme extract sync setup-email

total:
	$(PYTHON) reader.py --dataset $(DATASET) --total-only

update-readme:
	$(PYTHON) readmeupdater.py --dataset $(DATASET)

extract:
	$(PYTHON) reader.py --dataset $(DATASET)

sync:
	$(PYTHON) rxsync.py --dataset $(DATASET)

setup-email:
	$(PYTHON) setup_email.py

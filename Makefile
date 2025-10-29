PYTHON ?= python3

DATASET ?= rx.json

.PHONY: total update-readme extract

total:
	$(PYTHON) reader.py --dataset $(DATASET) --total-only

update-readme:
	$(PYTHON) readmeupdater.py --dataset $(DATASET)

extract:
	$(PYTHON) reader.py --dataset $(DATASET)

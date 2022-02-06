SHELL := /bin/bash
PYTHON := python3.9
DST := ./out
SRC := inequality growth

.PHONY: $(SRC) index

all: index $(SRC)

$(SRC):
	mkdir -pv $(DST)
	PYTHONPATH=./lib $(PYTHON) ./src/$@/main.py $@ > $(DST)/$@.html

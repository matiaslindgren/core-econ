SHELL := /bin/bash
PYTHON := python3.9

LIB := lib
SRC := src
DST := out
MODULES := index inequality growth
LIB_DEPS := base.j2 macros.j2 common.py style.css

OUT_FILES := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES)))
LIB_FILES := $(addprefix $(LIB)/,$(LIB_DEPS))

vpath %.py $(SRC)
vpath %.j2 $(SRC)

.PHONY: all clean dirs


all: $(OUT_FILES)

clean:
	rm -rfv $(DST)

dirs: $(DST)

$(DST):
	mkdir -pv $(DST)

$(OUT_FILES): $(DST)/%.html: $(SRC)/%.py $(SRC)/%.j2 metadata/%.yaml $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< $(filter-out index,$(MODULES)) > $@

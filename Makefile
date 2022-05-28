SHELL  := /bin/bash
PYTHON ?= python3.9

LIB  := lib
SRC  := src
META := metadata
DST  ?= out

INDEX    := index
MODULES  := $(shell cat modules.txt)
LIB_DEPS := base.j2 common.py style.css chart.js

LIB_FILES  := $(addprefix $(LIB)/,$(LIB_DEPS))
SRC_FILES  := $(addprefix $(SRC)/,$(addsuffix .py,$(MODULES)))
META_FILES := $(addprefix $(META)/,$(addsuffix .yaml,$(MODULES)))

MODULES_JS     := $(basename $(notdir $(wildcard $(SRC)/*.js)))
MODULES_NOJS   := $(filter-out $(MODULES_JS),$(MODULES))
DST_FILES_JS   := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES_JS)))
DST_FILES_NOJS := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES_NOJS)))
DST_FILES      := $(DST_FILES_NOJS) $(DST_FILES_JS)


.PHONY: all clean dirs install run new_module


all: $(DST)/$(INDEX).html $(DST_FILES)

clean:
	rm -rfv $(DST) cache

dirs: $(DST)

install:
	$(PYTHON) -m pip install --user -r requirements.txt

$(DST):
	mkdir -pv $(DST)

$(DST)/$(INDEX).html: $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(SRC)/%.j2 $(LIB_FILES) $(SRC_FILES) $(META_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< $(MODULES) > $@

$(DST_FILES_NOJS): $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< > $@

$(DST_FILES_JS): $(DST)/%.html: $(addprefix $(SRC)/,%.py %.j2 %.js) $(META)/%.yaml $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< > $@

run: $(DST_FILES) | install
	$(PYTHON) -m http.server --directory $(DST)

new_module:
	@if [[ -z "$(ARG)" ]]; then echo 'usage: make ARG=name new_module'; exit 2; fi
	touch src/$(ARG).{js,py}
	echo "{% extends 'base.j2' %}" > src/$(ARG).j2
	echo 'title: $(ARG)' > metadata/$(ARG).yaml
	echo $(ARG) >> modules.txt

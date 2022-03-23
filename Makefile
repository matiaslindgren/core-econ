SHELL  := /bin/bash
PYTHON := python3.9

LIB  := lib
SRC  := src
META := metadata
DST  := out

INDEX    := index
MODULES  := inequality growth global_warming comparative_advantage
LIB_DEPS := base.j2 common.py style.css

LIB_FILES  := $(addprefix $(LIB)/,$(LIB_DEPS))
SRC_FILES  := $(addprefix $(SRC)/,$(addsuffix .py,$(MODULES)))
META_FILES := $(addprefix $(META)/,$(addsuffix .yaml,$(MODULES)))

MODULES_WITH_JS   := $(basename $(notdir $(wildcard $(SRC)/*.js)))
DST_FILES_WITH_JS := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES_WITH_JS)))
MODULES   := $(filter-out $(MODULES_WITH_JS),$(MODULES))
DST_FILES := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES)))


vpath %.py   $(SRC)
vpath %.j2   $(SRC)
vpath %.js   $(SRC)
vpath %.yaml $(META)

.PHONY: all clean dirs install run


all: $(DST)/$(INDEX).html $(DST_FILES) $(DST_FILES_WITH_JS)

clean:
	rm -rfv $(DST)

dirs: $(DST)

install:
	$(PYTHON) -m pip install --user -r requirements.txt

$(DST):
	mkdir -pv $(DST)

$(DST)/$(INDEX).html: $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(LIB_FILES) $(SRC_FILES) $(META_FILES) %.j2 | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< $(MODULES) $(MODULES_WITH_JS) > $@

$(DST_FILES): $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< > $@

$(DST_FILES_WITH_JS): $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(SRC)/%.j2 $(SRC)/%.js $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< > $@

run: install $(DST_FILES) $(DST_FILES_WITH_JS)
	$(PYTHON) -m http.server --directory $(DST)

SHELL  := /bin/bash
PYTHON ?= python3.9

LIB  := lib
SRC  := src
META := metadata
DST  ?= out

INDEX    := index
MODULES  := inequality growth global_warming comparative_advantage the_two_germanies tech_and_cost malthus_escape marginal_product
LIB_DEPS := base.j2 common.py style.css chart.js

LIB_FILES  := $(addprefix $(LIB)/,$(LIB_DEPS))
SRC_FILES  := $(addprefix $(SRC)/,$(addsuffix .py,$(MODULES)))
META_FILES := $(addprefix $(META)/,$(addsuffix .yaml,$(MODULES)))

MODULES_JS     := $(basename $(notdir $(wildcard $(SRC)/*.js)))
MODULES_NOJS   := $(filter-out $(MODULES_JS),$(MODULES))
DST_FILES_JS   := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES_JS)))
DST_FILES_NOJS := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES_NOJS)))
DST_FILES      := $(DST_FILES_NOJS) $(DST_FILES_JS)


vpath %.py   $(SRC)
vpath %.j2   $(SRC)
vpath %.js   $(SRC)
vpath %.yaml $(META)

.PHONY: all clean dirs install run


all: $(DST)/$(INDEX).html $(DST_FILES)

clean:
	rm -rfv $(DST)

dirs: $(DST)

install:
	$(PYTHON) -m pip install --user -r requirements.txt

$(DST):
	mkdir -pv $(DST)

$(DST)/$(INDEX).html: $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(LIB_FILES) $(SRC_FILES) $(META_FILES) %.j2 | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< $(MODULES) > $@

$(DST_FILES_NOJS): $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< > $@

$(DST_FILES_JS): $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(SRC)/%.j2 $(SRC)/%.js $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< > $@

run: $(DST_FILES) | install
	$(PYTHON) -m http.server --directory $(DST)

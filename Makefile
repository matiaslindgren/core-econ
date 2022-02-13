SHELL  := /bin/bash
PYTHON := python3.9

LIB  := lib
SRC  := src
META := metadata
DST  := out

INDEX    := index
MODULES  := inequality growth global_warming
LIB_DEPS := base.j2 common.py style.css

LIB_FILES  := $(addprefix $(LIB)/,$(LIB_DEPS))
SRC_FILES  := $(addprefix $(SRC)/,$(addsuffix .py,$(MODULES)))
META_FILES := $(addprefix $(META)/,$(addsuffix .yaml,$(MODULES)))
DST_FILES  := $(addprefix $(DST)/,$(addsuffix .html,$(MODULES)))

vpath %.py   $(SRC)
vpath %.j2   $(SRC)
vpath %.yaml $(META)

.PHONY: all clean dirs


all: $(DST)/$(INDEX).html $(DST_FILES)

clean:
	rm -rfv $(DST)

dirs: $(DST)

$(DST):
	mkdir -pv $(DST)

$(DST)/$(INDEX).html: $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(LIB_FILES) $(SRC_FILES) $(META_FILES) %.j2 | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< $(MODULES) > $@

$(DST_FILES): $(DST)/%.html: $(SRC)/%.py $(META)/%.yaml $(LIB_FILES) | dirs
	PYTHONPATH=./$(LIB) $(PYTHON) $< > $@

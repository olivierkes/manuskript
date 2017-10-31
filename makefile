UI := $(wildcard manuskript/ui/*.ui) $(wildcard manuskript/ui/*/*.ui) $(wildcard manuskript/ui/*/*/*.ui) $(wildcard manuskript/ui/*.qrc) 
UIs= $(UI:.ui=.py) $(UI:.qrc=_rc.py)
TS := $(wildcard i18n/*.ts)
QMs= $(TS:.ts=.qm)

ui: $(UIs)

run: $(UIs)
# 	python3 manuskript/main.py
	bin/manuskript

debug: $(UIs)
	gdb --args python3 bin/manuskript

lineprof:
	kernprof -l -v bin/manuskript

profile:
	python3 -m cProfile -s 'cumtime' bin/manuskript | more

compile:
	cd manuskript && python3 setup.py build_ext --inplace
	
callgraph:
	cd manuskript; pycallgraph myoutput -- main.py

translation:
	pylupdate5 -noobsolete i18n/manuskript.pro
	
linguist:
	linguist i18n/manuskript_fr.ts
	lrelease i18n/manuskript_fr.ts
	
i18n: $(QMs)

pyinstaller:
	python3 /usr/local/bin/pyinstaller manuskript.spec

stats:
	python3 libs/gh-release-stats.py olivierkes manuskript -d

%_rc.py : %.qrc
	pyrcc5 "$<" -o "$@" 

%.py : %.ui
# 	pyuic4  "$<" > "$@" 
	pyuic5  "$<" > "$@" 
	
%.qm:  %.ts
	lrelease "$<"


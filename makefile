UI := $(wildcard src/ui/*.ui) $(wildcard src/ui/*/*.ui) $(wildcard src/ui/*.qrc) 
UIs= $(UI:.ui=.py) $(UI:.qrc=_rc.py)


ui: $(UIs)

run: $(UIs)
	python3 src/main.py

debug: $(UIs)
	gdb --args python src/main.py

lineprof:
	kernprof -l -v src/main.py

profile:
	python3 -m cProfile -s 'cumtime' src/main.py | more

compile:
	cd src && python3 setup.py build_ext --inplace

%_rc.py : %.qrc
	pyrcc5 "$<" -o "$@" 

%.py : %.ui
# 	pyuic4  "$<" > "$@" 
	pyuic5  "$<" > "$@" 
	


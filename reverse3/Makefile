all:
	cd zzvm && make clean && make
	python3 gen.py
	rm -r dist
	mkdir dist
	cp game.zz dist/oo
	cp ./zzvm/oovm dist/vm

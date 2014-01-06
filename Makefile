
all:
	python3 coin/coin.py

install:
	sudo cp resources/org.nil.indicator.coinprice.gschema.xml /usr/share/glib-2.0/schemas/
	sudo glib-compile-schemas --strict /usr/share/glib-2.0/schemas/
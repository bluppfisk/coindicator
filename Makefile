
all:
	python3 coin/coin.py

install:
	sudo apt-get install python3-gi python3-requests python3-yaml python3-notify2
	sudo cp resources/org.nil.indicator.coinprice.gschema.xml /usr/share/glib-2.0/schemas/
	sudo glib-compile-schemas --strict /usr/share/glib-2.0/schemas/
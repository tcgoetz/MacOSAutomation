

deps:
	pip install --upgrade --requirement scripts/requirements.txt

install: deps
	cp -R services/*.workflow ~/Library/Services

clean:
	rm -f scripts/*.pyc
	rm -f *.zip

release: zip_packages

PLATFORM=$(shell uname)
VERSION=$(shell cat version.txt)
zip_packages:
	zip -r EvernoteAutomation_$(PLATFORM)_$(VERSION).zip readme.txt scripts/requirements.txt services/*

WORKDIR = .
MANAGE = python $(WORKDIR)/manage.py

style:
	black -S -l 79 $(WORKDIR)
	isort $(WORKDIR)
	flake8 $(WORKDIR)/gob/

.PHONY: setkey build

setkey:
	eval `ssh-agent -s`; \
	ssh-add ~/.ssh/id_rsa_github

build:
	python manage.py collectstatic; \
	python manage.py makemigrations; \
	python manage.py migrate; \
	sudo supervisorctl restart wedding-website; \
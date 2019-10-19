.PHONY: setkey update build

setkey:
	eval `ssh-agent -s`; \
	ssh-add ~/.ssh/id_rsa_github

update:
	git pull origin master

build:
	python manage.py collectstatic; \
	python manage.py makemigrations; \
	python manage.py migrate; \
	sudo supervisorctl restart wedding-website; \
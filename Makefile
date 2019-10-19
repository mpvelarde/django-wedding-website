.PHONY: setkey update build activate

setkey:
	eval `ssh-agent -s`; \
	ssh-add ~/.ssh/id_rsa_github

update:
	git pull origin master

activate:
	source venv/bin/activate

build:
	python manage.py collectstatic; \
	python manage.py makemigrations; \
	python manage.py migrate; \
	sudo supervisorctl restart wedding-website; \
# Deployment Using Nginx + Supervisor + Gunicorn in Digital Ocean

Deployed the site using:
* https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04#step-5-setting-up-server-blocks-(recommended)
* https://simpleisbetterthancomplex.com/tutorial/2016/10/14/how-to-deploy-to-digital-ocean.html
* https://www.digitalocean.com/community/tutorials/how-to-set-up-a-scalable-django-app-with-digitalocean-managed-databases-and-spaces
* https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04

The main pieces to setup are:
- Firewall
- Nginx
- Gunicorn
- Supervisor


To update remote applicate

```
cd django-wedding-website
source venv/bin/activate
git pull origin master
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
sudo supervisorctl restart wedding-website
exit
```

If can't connect to github
```
eval `ssh-agent -s`
ssh-add ~/.ssh/id_rsa_github
```
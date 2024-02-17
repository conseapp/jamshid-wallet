# jamshid Wallet Backend
base wallet backend for jamshid app <br>
with authentication of requested user per request<br>
all data has been stored on postgresql running on main server

### Built With
* ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
* ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
* ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
* ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

## Admin

admin panel
* https://wallet.jamshid.app/admin

## Usage

method = POST

### Deposit
```http request
http://wallet.jamshid.app/api/deposit/?user_id=<user_id>&amount=<amount>
```

### Get Balance
```http request
http://wallet.jamshid.app/api/getbalance/?user_id=<user_id>
```

### Purchase
```http request
http://wallet.jamshid.app/api/purchase/?user_id=<user_id>&amount=<amount>&event_id=<event_id>
```

## be sure to pass jwt token as "token" in headers
jwt token example:
```console
Bearer <token>
```

## Deploy

### 1. install python environment
```console
sudo apt install python3.10-venv
```
### 2. initialize environment
```console
python3 -m venv venv
```
### 3. activate environment
```console
source venv/bin/activate
```
### 4. install requirements
```console
pip3 install -r requirements.txt
```
### 5. make migrations
```console
python3 manage.py makemigrations
```
### 6. migrate
```console
python3 manage.py migrate
```
### 7. create admin user
```console
python2 manage.py createsuperuser
```
### 8. run
```console
python manage.py runserver
```

Developed By Hexoder

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

run:
	python manage.py runserver 0.0.0.0:8000

pip:
	pip install -r requirements.txt

pip-win:
	pip install -r requirements.win.txt

shell:
	python manage.py shell

up:
	docker-compose -f docker-compose.local.yml up --remove-orphans --build

down:
	docker-compose -f docker-compose.local.yaml down

format:
	black **/*.py

lint:
	flake8
	black **/*.py --check

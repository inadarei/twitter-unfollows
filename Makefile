default: redis-server logs-db

service:=ms-unfollows

.PHONY: stop
stop:
	docker-compose down

.PHONY: app
app:
	docker-compose run ${service} python service.py show

.PHONY: check
check:
	docker-compose run ${service} python service.py run

.PHONY: restart
restart: stop redis-server

.PHONY: ps
ps:
	docker-compose ps

.PHONY: logs
logs:
	docker-compose logs -f

.PHONY: logs-db
logs-db:
	docker-compose logs -f unfollows-redis

.PHONY: logs-app
logs-app:
	docker-compose logs -f ${service}

.PHONY: redis-server
redis-server:
	docker-compose up -d unfollows-redis

# connect to redis cli for debugging
.PHONY: redis-cli
redis-cli:
	docker exec -it unfollows-redis redis-cli -a 4n_ins3cure_P4ss

# connect to the app cli for debugging
.PHONY: shell
shell:
	docker-compose exec ${service} bash

.PHONY: build
build:
	docker-compose build --no-cache

.PHONY: clean
clean: stop build app

.PHONY: install-package-in-container
install-package-in-container:
	docker-compose exec ${service} pip install ${package}
	docker-compose exec ${service} pip freeze > requirements.txt

.PHONY: add
add: app install-package-in-container build

.PHONY: deps
deps:
	docker-compose exec ${service} pip install -r requirements.txt

.PHONY: lint
lint:
	docker-compose exec ${service} pylint service.py src/*.py tests/**/*.py

.PHONY: test
test: app test-run-only

.PHONY: test-run-only
test-run-only:
	docker-compose exec ${service} pytest

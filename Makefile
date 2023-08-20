build:
	docker build --tag device-readings .

run: build
	docker run -it -v ${PWD}:/app -p 8000:8000 -e FLASK_DEBUG=true device-readings

test: build
	docker run -it -v ${PWD}:/app device-readings python -m pytest -v -p no:cacheprovider
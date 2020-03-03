#!make
include .env
export

serve:
	flask run

lint:
	isort -rc .
	black .

tests:
	python -m unittest discover tests

run:
	python -m run_n_jump

lint:
	python -m pylint run_n_jump

type_check:
	python -m mypy run_n_jump

install:
	pip install -r requirements.txt

.PHONY: run tests

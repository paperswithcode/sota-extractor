.PHONY: help default notebook test check format
.DEFAULT_GOAL := help
PROJECT := sota_extractor

help:                      ## Show help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


notebook:                ## Run Jupyter notebook.
	@jupyter notebook


test:                    ## Run tests.
	@py.test -n 4 --cov "$(PROJECT)"


check:                   ## Run code checks.
	@flake8 "$(PROJECT)"
	@pydocstyle "$(PROJECT)"


format:                  ## Format the code.
	@black --target-version=py37 --safe --line-length=79 "$(PROJECT)"

build:               ## Build the source and wheel distribution packages.
	@python3 setup.py sdist bdist_wheel


release: build       ## Build and upload the package to PyPI.
	@twine upload --repository-url  https://upload.pypi.org/legacy/ dist/*
	@rm -fr build dist sota_extractor.egg-info

.PHONY: install test dev ami clean

install:
	pip install -e "."

test:
	pytest

dev:
	# Run both API and Dashboard in dev mode (placeholder)
	@echo "Starting development environment..."
	python -m axle.web.api.app

ami:
	packer build build/packer/axle-ami.pkr.hcl

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

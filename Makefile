.PHONY: check catalog test package
catalog:
	python3 scripts/build_manifest.py
check:
	python3 scripts/build_manifest.py
	python3 scripts/build_manifest.py --check
	python3 scripts/validate.py
test:
	python3 -m unittest discover -s tests -v
package: check test
	python3 scripts/package.py --output-dir dist

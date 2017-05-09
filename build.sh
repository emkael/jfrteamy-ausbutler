#!/bin/bash
rm -rf build dist/*
pyinstaller ausbutler.spec
cp -a config template dist
mv dist/config/db.json.EXAMPLE dist/config/db.json
cp README.*.md dist
cp LICENSE dist

#! /bin/bash

pip install -r requirements.txt -r dev_requirements.txt

pushd frontend
yarn install
yarn run build
popd

honcho start


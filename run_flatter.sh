#!/usr/bin/bash
docker run --env-file ./env_file --name avito_yar flatter avito_spider -a region='yaroslavl'

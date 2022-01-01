#!/bin/bash

for region in $(cat regions);do
	echo "Запускаем парсер $region"
	docker run --env-file ./env_file \
	       	   --name "avito_$region" \
		   flatter avito_spider \
		   -a region=$region 2>&1 | tee "res_$region"
done

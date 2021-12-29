#!/bin/bash

scrapy crawl proxy_picker && scrapy crawl "$@"

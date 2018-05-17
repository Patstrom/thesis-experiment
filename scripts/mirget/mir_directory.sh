#!/bin/bash

variations=$1

for variation in $variations*
do
	echo $variation
	cargo run --release $variation
done

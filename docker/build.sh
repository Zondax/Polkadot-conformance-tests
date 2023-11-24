#!/bin/bash
if [ ! -d 'polkadot-sdk' ]; then
	git clone -b zondax https://github.com/Zondax/polkadot-sdk
else
	echo 'Polkadot sdk repo cloned already'
fi
cd polkadot-sdk
echo 'Compiling polkadot binary'
cargo build --features specs-tests

cd polkadot-sdk/polkadot/runtime/polkadot
echo 'Compiling custom runtime binary'
cargo build --release

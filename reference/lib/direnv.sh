# $1 ... path to .envrc
# $2 ... verbose if set
write_direnv() {
	if [[ ! -z "$2" ]]; then
		echo " * Writing .envrc"
	fi

	cat << EOF > "$1"
export PREFIX=$PREFIX
export PREFIX_DIR=$PREFIX_DIR
export PKG_CONFIG_PATH=$PREFIX_DIR/$PREFIX/lib/pkgconfig
export PATH=$PREFIX_DIR/$PREFIX/sbin:$PREFIX_DIR/$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX_DIR/$PREFIX/lib
export CC="$CC"
export CXX="$CXX"
export CFLAGS="$CFLAGS"
export CXXFLAGS="$CXXFLAGS"
export LDFLAGS="$LDFLAGS"
export ASAN_OPTIONS="$ASAN_OPTIONS"
export UBSAN_OPTIONS="$UBSAN_OPTIONS"
export TSAN_OPTIONS="$TSAN_OPTIONS"
EOF
	direnv allow "$(dirname $1)"
}

# $1 ... source dir
# $2 ... build dir
# $3 ... config
cmake_init() {
	local SOURCE_DIR="$(realpath $1)"
	local BUILD_DIR

	if [[ -z "$2" ]]; then
		BUILD_DIR="$(pwd)"
		if [[ -e "CMakeCache.txt" ]]; then
			echo "Directory already has initialized CMake"
			exit 1
		fi
	else
		BUILD_DIR="$2"
		if [[ -d "$BUILD_DIR" ]]; then
			echo "Directory already exists"
			exit 1
		fi
		mkdir $BUILD_DIR
	fi

	local PREFIX="$3"
	if [[ -z "$3" ]]; then
		PREFIX="$(detect_prefix_from_dirname $(basename BUILD_DIR))"
		echo " * Detected prefix '$PREFIX'"
	fi

	local CC="$(env_from_prefix CC $PREFIX)"
	local CXX="$(env_from_prefix CXX $PREFIX)"
	local CFLAGS="$(env_from_prefix CFLAGS $PREFIX)"
	local CXXFLAGS="$(env_from_prefix CXXFLAGS $PREFIX)"
	local LDFLAGS="$(env_from_prefix LDFLAGS $PREFIX)"
    local ASAN_OPTIONS="intercept_tls_get_addr=0,log_to_syslog=true,handle_abort=2"
    local UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"
    local TSAN_OPTIONS="suppressions=/home/tomas/zdrojaky/cesnet/dependencies/ci/tsan.supp"

	write_direnv "$BUILD_DIR/.envrc" verbose

	echo " * Running CMake"
	set -x
	CC=$CC CXX=$CXX CFLAGS=$CFLAGS CXXFLAGS=$CXXFLAGS LDFLAGS="$LDFLAGS" \
		cmake -GNinja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_PREFIX_PATH="$PREFIX_DIR/$PREFIX" -S "$SOURCE_DIR" -B "$BUILD_DIR"
}

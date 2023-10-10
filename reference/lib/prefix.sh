# $1 ... dirname
detect_prefix_from_dirname() {
	case "$BUILD_DIR" in
		*gcc-asan*)
			echo "gcc-asan"
			;;
		*gcc-tsan*)
			echo "gcc-tsan"
			;;
		*gcc-clean*)
			echo "gcc-clean"
			;;
		*clang-asan*)
			echo "clang-asan"
			;;
		*clang-tsan*)
			echo "clang-tsan"
			;;
		*clang-clean*)
			echo "clang-clean"
			;;
		*)
			echo "Could not determine prefix."
			exit 1
			;;
	esac
	return 0
}

# $1 ... env
# $2 ... prefixname
env_from_prefix() {
	local compiler="$(echo $PREFIX | cut -d"-" -f1)"
	local sanitizer="$(echo $PREFIX | cut -d"-" -f2)"

	local CC
	local CFLAGS
	local CXX
	local CXXFLAGS
    local LDFLAGS

	case "$compiler" in
		gcc)
			CC=gcc
			CXX=g++
			;;
		clang)
			CC=clang
			CXX=clang++
			;;
	esac

	case "$sanitizer" in
		clean)
			CFLAGS="-g"
			;;
		tsan)
			CFLAGS="-fsanitize=thread -g"
            LDFLAGS="-fsanitize=thread"
			;;
		asan)
			CFLAGS="-fsanitize=address -fsanitize=undefined -g"
            LDFLAGS="-fsanitize=address -fsanitize=undefined"
			;;
	esac
	CXXFLAGS="$CFLAGS"

	case "$1" in
		CC)
			echo "$CC"
			;;
		CXX)
			echo "$CXX"
			;;
		CFLAGS)
			echo "$CFLAGS"
			;;
		CXXFLAGS)
			echo "$CXXFLAGS"
			;;
		LDFLAGS)
			echo "$LDFLAGS"
			;;
	esac
}

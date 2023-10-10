# $1 - prefix_dir
# $2 - source directory
# $3... - additional options passed to CMake
build_and_install_cmake() {
	local SOURCE_DIR="$2"
	local BUILD_DIR="${BUILD_PREFIX}/$(basename $SOURCE_DIR)/"

	echo " * Building $(basename $SOURCE_DIR)"

	clean_sysrepo_state "${SYSREPO_DIR}"
	rm -fr "${BUILD_DIR}"
	mkdir -p "${BUILD_DIR}"

	shift 2
	write_direnv "${BUILD_DIR}/.envrc"

	pushd "${BUILD_DIR}" >/dev/null

	echo "   -> CMake"
	env \
		CC="$CC" \
		CXX="$CXX" \
		CFLAGS="$CFLAGS" \
		CXXFLAGS="$CXXFLAGS" \
		LDFLAGS="$LDFLAGS" \
		cmake "${SOURCE_DIR}" -GNinja \
            -DCMAKE_BUILD_TYPE=Debug \
            -DCMAKE_EXPORT_COMPILE_COMMANDS=YES \
            -DCMAKE_INSTALL_PREFIX:PATH="${INSTALL_PREFIX}" \
            -DCMAKE_PREFIX_PATH:PATH="${INSTALL_PREFIX}" \
			-DHAVE_PTHREAD_MUTEX_TIMEDLOCK=OFF -DHAVE_PTHREAD_MUTEX_CLOCKLOCK=OFF -DHAVE_PTHREAD_RWLOCK_CLOCKRDLOCK=OFF -DHAVE_PTHREAD_RWLOCK_CLOCKWRLOCK=OFF -DHAVE_PTHREAD_COND_CLOCKWAIT=OFF \
            $@ \
            $CMAKE_FLAGS \
            1> ${LOGFILE_OUT} 2> ${LOGFILE_ERR}
    if [[ $? != 0 ]]; then
        echo "Failure. See logs at $LOGFILE_OUT $LOGFILE_ERR"
        exit 1
    fi

	echo "   -> Build"
	> $LOGFILE_OUT
	> $LOGFILE_ERR
    if ! ninja > $LOGFILE_OUT 2> $LOGFILE_ERR; then
        echo "Failure. See logs at $LOGFILE_OUT $LOGFILE_ERR"
        exit 1
    fi

    if false; then
        echo "   -> Test"
        > $LOGFILE_OUT
        > $LOGFILE_ERR
        TSAN_OPTIONS=$TSAN_OPTIONS ASAN_OPTIONS=$ASAN_OPTIONS UBSAN_OPTIONS=$UBSAN_OPTIONS \
            LD_LIBRARY_PATH=$LD_LIBRARY_PATH ctest -j$(nproc) --output-on-failure > $LOGFILE_OUT 2> $LOGFILE_ERR
        if [[ $? != "0" ]]; then
            echo "Failure. See logs at $LOGFILE_OUT $LOGFILE_ERR"
            exit 1
        fi
    fi

	echo "   -> Install"
	> $LOGFILE_OUT
	> $LOGFILE_ERR
	PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH ninja install > $LOGFILE_OUT 2> $LOGFILE_ERR

	popd > /dev/null
}

# $1 - prefix name
build_prefix() {
	local INSTALL_PREFIX="${PREFIX_DIR}/$1"
	local BUILD_PREFIX="${BUILD_DIR}/$1"
	local SYSREPO_DIR="${INSTALL_PREFIX}/${SYSREPO_DIR_NAME}"

	local LD_LIBRARY_PATH="${INSTALL_PREFIX}/lib:${LD_LIBRARY_PATH}"
	local PATH="${INSTALL_PREFIX}/bin:${PATH}"

	echo "Prefix $1 (CC=$CC | CXX=$CXX | CFLAGS=$CFLAGS | CXXFLAGS=$CXXFLAGS | LDFLAGS=$LDFLAGS)"
	echo " - Build prefix   $BUILD_PREFIX"
	echo " - Install prefix $INSTALL_PREFIX"
	echo " - Sysrepo dir    $SYSREPO_DIR"

	rm -fr ${INSTALL_PREFIX}
	rm -fr ${SYSREPO_DIR}

	pushd "$DEPENDENCIES" > /dev/null

	build_and_install_cmake "$1" "${DEPENDENCIES}/libyang" \
        ${COMMON_CMAKE[@]} \
        -DENABLE_VALGRIND_TESTS=OFF
	build_and_install_cmake "$1" "${DEPENDENCIES}/sysrepo" \
        ${COMMON_CMAKE[@]} \
        -DENABLE_VALGRIND_TESTS=OFF \
		-DREPO_PATH=${SYSREPO_DIR}/repository \
        -DPLUGINS_PATH=${SYSREPO_DIR}/plugins
	build_and_install_cmake "$1" "${DEPENDENCIES}/libnetconf2" \
        ${COMMON_CMAKE[@]} \
        -DENABLE_VALGRIND_TESTS=OFF
    build_and_install_cmake "$1" "${DEPENDENCIES}/Netopeer2" \
        ${COMMON_CMAKE[@]} \
        -DENABLE_VALGRIND_TESTS=OFF \
		-DINSTALL_MODULES=ON \
		-DGENERATE_HOSTKEY=ON \
		-DMERGE_LISTEN_CONFIG=ON
	build_and_install_cmake "$1" "${DEPENDENCIES}/doctest" \
        -DDOCTEST_WITH_TESTS=OFF
	build_and_install_cmake "$1" "${DEPENDENCIES}/trompeloeil" \
        -DCMAKE_BUILD_TYPE=Release
	build_and_install_cmake "$1" "${DEPENDENCIES}/libyang-cpp"
	build_and_install_cmake "$1" "${DEPENDENCIES}/sysrepo-cpp"
	build_and_install_cmake "$1" "${DEPENDENCIES}/libnetconf2-cpp"
	build_and_install_cmake "$1" "${DEPENDENCIES}/sdbus-cpp"
	build_and_install_cmake "$1" "${DEPENDENCIES}/replxx"

    build_and_install_cmake "$1" "${CESNET_DIR}/netconf-cli"
	build_and_install_cmake "$1" "${CESNET_DIR}/nghttp2-asio"

	popd > /dev/null
}

build_all_prefixes() {
	for compiler in gcc clang; do
		for sanitizer in clean tsan asan; do
			local PREFIX="${compiler}-${sanitizer}"
			if [[ ! -z "$1" && ! "$PREFIX" =~ "$1" ]]; then
				continue
			fi

			trap 'printf "\e[31mRETCODE=%s STDOUT in %s STDERR in %s\e[m\n" $? "$LOGFILE_OUT" "$LOGFILE_ERR"' ERR

			local CC="$(env_from_prefix CC $PREFIX)"
			local CXX="$(env_from_prefix CXX $PREFIX)"
			local CFLAGS="$(env_from_prefix CFLAGS $PREFIX)"
			local CXXFLAGS="$(env_from_prefix CXXFLAGS $PREFIX)"
			local LDFLAGS="$(env_from_prefix LDFLAGS $PREFIX)"
            local ASAN_OPTIONS="intercept_tls_get_addr=0,log_to_syslog=true,handle_abort=2"
            local UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"
            local TSAN_OPTIONS="suppressions=/home/tomas/zdrojaky/cesnet/dependencies/ci/tsan.supp"

			build_prefix "${PREFIX}"
            echo "Build of $PREFIX done"
		done
	done
}


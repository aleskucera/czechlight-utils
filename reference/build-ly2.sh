#!/run/current-system/sw/bin/env bash

if [[ -z "${PREFIX}" ]]; then
  echo "This needs some magic, enter a subshell via ./enter.sh first"
  exit 1
fi
  
set -eux -o pipefail
shopt -s failglob

mkdir -p ${PREFIX} ${RUNDIR}

HACK_COMPAT_PTHREAD="-DHAVE_PTHREAD_MUTEX_TIMEDLOCK=OFF -DHAVE_PTHREAD_MUTEX_CLOCKLOCK=OFF -DHAVE_PTHREAD_RWLOCK_CLOCKRDLOCK=OFF -DHAVE_PTHREAD_RWLOCK_CLOCKWRLOCK=OFF -DHAVE_PTHREAD_COND_CLOCKWAIT=OFF"

CMAKE_OPTIONS="${CMAKE_OPTIONS} -DENABLE_TESTS=ON" build_dep_cmake ${PROJECT_ROOT}/../github/CESNET/libyang
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DREPO_PATH=${PREFIX}/etc-sysrepo -DENABLE_TESTS=ON -DENABLE_VALGRIND_TESTS=OFF ${HACK_COMPAT_PTHREAD}" build_dep_cmake ${PROJECT_ROOT}/../github/sysrepo/sysrepo
# create the sysrepo directory
sysrepoctl --list
CMAKE_OPTIONS="${CMAKE_OPTIONS} ${HACK_COMPAT_PTHREAD}" build_dep_cmake ${PROJECT_ROOT}/../github/CESNET/libnetconf2
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DPIDFILE_PREFIX=${RUNDIR} ${HACK_COMPAT_PTHREAD}" build_dep_cmake ${PROJECT_ROOT}/../github/CESNET/Netopeer2

build_dep_cmake ${PROJECT_ROOT}/../github/onqtam/doctest
CMAKE_BUILD_TYPE=Release build_dep_cmake ${PROJECT_ROOT}/../github/rollbear/trompeloeil
build_dep_cmake ${PROJECT_ROOT}/../github/AmokHuginnsson/replxx
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DBUILD_DOC=OFF -DBUILD_CODE_GEN=ON" build_dep_cmake ${PROJECT_ROOT}/../github/Kistler-Group/sdbus-cpp
build_dep_cmake ${PROJECT_ROOT}/../github/nghttp2/nghttp2-asio

build_dep_cmake ${PROJECT_ROOT}/libyang-cpp
build_dep_cmake ${PROJECT_ROOT}/sysrepo-cpp
build_dep_cmake ${PROJECT_ROOT}/libnetconf2-cpp

build_dep_cmake_slow ${PROJECT_ROOT}/netconf-cli
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DMOUNT_EXECUTABLE=/run/current-system/sw/bin/mount" build_dep_cmake ${PROJECT_ROOT}/velia
build_dep_cmake ${PROJECT_ROOT}/rousette
build_dep_cmake ${PROJECT_ROOT}/cla-sysrepo
build_dep_cmake ${PROJECT_ROOT}/sysrepo-ietf-alarms

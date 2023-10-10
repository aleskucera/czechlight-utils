#1 - sysrepo directory. If not specified then delete all
clean_sysrepo_state() {
	rm -fr /dev/shm/*

	if [[ ! -z "$1" ]]; then
		rm -fr $1/repository
	else
		for sysrepo_dir in $(find $PREFIX_DIR -name $SYSREPO_DIR_NAME -type d); do
			local del="${sysrepo_dir}/repository"
			echo "Removing $del"
			rm -fr "$del"
		done
        #TODO delete test_repositories
	fi
}

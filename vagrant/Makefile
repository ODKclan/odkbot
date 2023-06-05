name = odkbot
hostname = win-$(name)
watch_exclude = \.git|\.venv|vagrant/\.vagrant|.idea
ssh_config_file = ssh_config
rsync_base_cmd = rsync -ah -e 'ssh -F $(ssh_config_file)'
sync_cmd = $(rsync_base_cmd) --progress --exclude-from=.rsyncignore ../ $(hostname):../../$(name)
mounted_dir = mounted
check_mounted = grep -qs `realpath $(mounted_dir)` /proc/mounts


.PHONY: all up redist clean shell check sync watch download_lock mount umount
.SILENT: all up redist clean shell check sync watch download_lock mount umount


#
# vagrant lifecycle
#
all: up

up:
	vagrant up

clean:
	vagrant destroy -f

#
# ssh
#
ssh_config:
	vagrant ssh-config > $(ssh_config_file)

shell:
	vagrant ssh

#
# code sync
#
check: ssh_config
	$(sync_cmd) -vun --stats | grep 'Number of regular files transferred' | awk -F ": " '{print $$2}'

sync: ssh_config
	$(sync_cmd)

watch: ssh_config
	echo -e "\n>> STARTING CONTINUOUS SYNC <<\n" && \
		$(sync_cmd) && echo "" && \
		while inotifywait -r -e modify,create,delete --exclude "$(watch_exclude)" .. ; do \
				$(sync_cmd) && echo ""; \
		done

download_lock: ssh_config
		$(rsync_base_cmd) $(hostname):../../$(name)/Pipfile.lock ../. && chmod 644 ../Pipfile.lock

#
# workdir mounting
#
mount: ssh_config
	if not $(check_mounted); then \
		mkdir -p $(mounted_dir) && \
			sshfs -v -F `realpath $(ssh_config_file)` $(hostname):/C:/$(name) $(mounted_dir) && \
			echo "Folder mounted!"; \
	else \
		echo "Already mounted!"; \
	fi

umount:
	if $(check_mounted); then \
		umount $(mounted_dir) && rm -rf $(mounted_dir) && echo "Folder umounted!"; \
	else \
		echo "Nothing to do."; \
	fi

# EC2 distributed deployment Makefile
SSH_KEY_PATH ?=
SSH_USER ?= ubuntu
BASH_BIN ?= bash


# Parse node0~3 public IPs from hosts.txt automatically
NODES := $(shell grep -E 'node[0-9]+$$' hosts.txt | awk '{print "$(SSH_USER)@"$$1}')
NODE0 := $(shell awk '$$2=="node0" {print "$(SSH_USER)@"$$1}' hosts.txt)
# Parse the client public IP from hosts.txt
CLIENT := $(shell grep -E 'client$$' hosts.txt | awk '{print "$(SSH_USER)@"$$1}')
# Parse all public IPs from hosts.txt
HOST_IPS := $(shell grep -v private hosts.txt | awk '{print $$1}')

SSH_OPTS = -i $(SSH_KEY_PATH) -o StrictHostKeyChecking=accept-new -o BatchMode=yes -o ConnectTimeout=8

# Adversary deployment helpers
ADV_COMPOSE_FILE ?= docker-compose-adv.yml
ADV_NODE_FILE := .adv-node
ADV_REMOTE_DIR := ~/hotstuff
ADV_REMOTE_COMPOSE := docker-compose.yml
ADV_REMOTE_ENV := .env


.PHONY: check-ssh-key init deploy start stop logs known_hosts ping hosts-clean \
	clean-ec2 clean clean-images deploy-adv start-adv start-dev

check-ssh-key:
	@if [ -z "$(strip $(SSH_KEY_PATH))" ]; then \
		echo "SSH_KEY_PATH is required for E3 (for example: make SSH_KEY_PATH=\$$HOME/.ssh/my-ec2-key.pem <target>)" >&2; \
		exit 1; \
	fi
	@if [ ! -r "$(SSH_KEY_PATH)" ]; then \
		echo "SSH private key is not readable: $(SSH_KEY_PATH)" >&2; \
		exit 1; \
	fi

known_hosts:
	@echo "Initializing known_hosts..."
	@ssh-keyscan -H $(HOST_IPS) >> $$HOME/.ssh/known_hosts 2>/dev/null || true
	@echo "known_hosts updated"

ping: check-ssh-key
	@for host in $(NODES) $(CLIENT); do \
	  echo "↪︎ Testing $$host"; \
	  ssh $(SSH_OPTS) $$host 'echo OK' || echo "$$host connection failed"; \
	done

init: check-ssh-key
	@SSH_KEY_PATH="$(SSH_KEY_PATH)" SSH_USER="$(SSH_USER)" $(BASH_BIN) init-ec2.sh

deploy: check-ssh-key
	@SSH_KEY_PATH="$(SSH_KEY_PATH)" SSH_USER="$(SSH_USER)" $(BASH_BIN) deploy-ec2.sh



pull: check-ssh-key
	@echo "Pulling node and client images..."
	@status=0; pids=""; \
	for node in $(NODES); do \
		( \
			echo "Pulling hotstuff-node image on $${node}..."; \
			if ! ssh $(SSH_OPTS) $${node} "cd ~/hotstuff && docker compose pull hotstuff-node"; then \
				echo "Warning: failed to pull on $${node}"; \
				exit 1; \
			fi \
		) & \
		pids="$$pids $$!"; \
	done; \
	for pid in $$pids; do \
		if ! wait $$pid; then status=1; fi; \
	done; \
	if [ $$status -ne 0 ]; then \
		echo "Warning: one or more node pulls failed"; \
	fi
	@echo "Pulling client image ($(CLIENT)) ..."
	@ssh $(SSH_OPTS) $(CLIENT) "cd ~/hotstuff && docker compose pull hotstuff-client" || true
	@echo "Image pull complete"
# 	@$(MAKE) deploy-adv

start: check-ssh-key
	@$(MAKE) hosts-clean
	@echo "Starting the experiment..."
	@status=0; pids=""; \
	for node in $(NODES); do \
		( \
			ssh $(SSH_OPTS) $${node} "cd ~/hotstuff && docker compose --profile consensus up -d" \
		) & \
		pids="$$pids $$!"; \
	done; \
	for pid in $$pids; do \
		if ! wait $$pid; then status=1; fi; \
	done; \
		if [ $$status -ne 0 ]; then \
			echo "Failed to start consensus nodes"; \
		exit 1; \
	fi
	@sleep 20
	@ssh $(SSH_OPTS) $(CLIENT) "cd ~/hotstuff && docker compose --profile client up -d" || { echo "Failed to start client"; exit 1; }
	@echo "Experiment startup complete"
	@echo "Waiting 2 minutes before automatically stopping..."
	@sleep 120
	@$(MAKE) stop


stop: check-ssh-key
	@echo "Stopping the experiment..."
	@status=0; pids=""; \
	for node in $(NODES); do \
		echo "→ $$node"; \
		( \
			ssh $(SSH_OPTS) $$node "cd ~/hotstuff && docker compose --profile consensus down" \
		) & \
		pids="$$pids $$!"; \
	done; \
	for pid in $$pids; do \
		if ! wait $$pid; then status=1; fi; \
	done; \
		if [ $$status -ne 0 ]; then \
			echo "Failed to stop consensus nodes"; \
		exit 1; \
	fi
	@ssh $(SSH_OPTS) $(CLIENT) "cd ~/hotstuff && docker compose --profile client down" || { echo "Failed to stop client"; exit 1; }
	@echo "Experiment stopped; preparing to collect logs"
	@$(MAKE) logs-core

logs: check-ssh-key
	@echo "Collecting logs..."
	@mkdir -p ec2-logs
	@status=0; pids=""; \
	for node in $(NODES); do \
		host=$${node##*@}; \
		( scp $(SSH_OPTS) -r $$node:~/hotstuff/logs/* ./ec2-logs/logs-$$host ) & \
		pids="$$pids $$!"; \
	done; \
	( scp $(SSH_OPTS) -r $(CLIENT):~/hotstuff/logs ./ec2-logs/logs-client ) & \
	pids="$$pids $$!"; \
	for pid in $$pids; do \
		if ! wait $$pid; then status=1; fi; \
	done; \
	if [ $$status -ne 0 ]; then \
		echo "Failed to collect logs"; \
		exit 1; \
	fi
	@echo "Log collection complete"
	@$(MAKE) clean

logs-core: check-ssh-key
# 	@echo "Collecting node0, node1, and client logs..."
	@echo "Collecting node1, and client logs..."
	@mkdir -p ec2-logs
	@status=0; pids=""; \
	node0="$(NODE0)"; \
	node1=$$(awk '$$2=="node1" {print "$(SSH_USER)@"$$1; exit}' hosts.txt); \
	if [ -n "$$node0" ]; then \
		host=$${node0##*@}; \
		( \
			if ssh $(SSH_OPTS) $$node0 'test -d ~/hotstuff/logs && ls -A ~/hotstuff/logs >/dev/null 2>&1'; then \
				scp $(SSH_OPTS) -r $$node0:~/hotstuff/logs/* ./ec2-logs/logs-$$host; \
			else \
				echo "No logs present on $$node0, skipping copy"; \
			fi \
		) & \
		pids="$$pids $$!"; \
	else \
		echo "Warning: node0 public IP not found, skipping node0 log collection"; \
	fi; \
	if [ -n "$$node1" ]; then \
		host=$${node1##*@}; \
		( \
			if ssh $(SSH_OPTS) $$node1 'test -d ~/hotstuff/logs && ls -A ~/hotstuff/logs >/dev/null 2>&1'; then \
				scp $(SSH_OPTS) -r $$node1:~/hotstuff/logs/* ./ec2-logs/logs-$$host; \
			else \
				echo "No logs present on $$node1, skipping copy"; \
			fi \
		) & \
		pids="$$pids $$!"; \
	else \
		echo "Warning: node1 public IP not found, skipping node1 log collection"; \
	fi; \
	( \
		if ssh $(SSH_OPTS) $(CLIENT) 'test -d ~/hotstuff/logs && ls -A ~/hotstuff/logs >/dev/null 2>&1'; then \
			scp $(SSH_OPTS) -r $(CLIENT):~/hotstuff/logs ./ec2-logs/logs-client; \
		else \
			echo "No logs present on $(CLIENT), skipping copy"; \
		fi \
	) & \
	pids="$$pids $$!"; \
	for pid in $$pids; do \
		if ! wait $$pid; then status=1; fi; \
	done; \
	if [ $$status -ne 0 ]; then \
		echo "Failed to collect core logs"; \
		exit 1; \
	fi
	@echo "Core log collection complete"
	@$(MAKE) clean

hosts-clean:
	@echo "Cleaning old known_hosts entries (EC2 IPs only)..."
	@for ip in $$(awk '{print $$1}' hosts.txt | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$$'); do \
		ssh-keygen -R $$ip >/dev/null 2>&1; \
	done
	@echo "EC2 IP cleanup done"

clean: check-ssh-key
	@echo "Cleaning log directories..."
	@for ip in $$(awk '{if ($$1 !~ /^172\./ && ($$2 ~ /^node/ || $$2 ~ /^client/)) print $$1}' hosts.txt); do \
		( \
			echo "→ Cleaning $$ip ..."; \
			if ssh $(SSH_OPTS) $(SSH_USER)@$$ip "sudo rm -rf ~/hotstuff/logs/*"; then \
				echo "$$ip cleanup complete"; \
			else \
				echo "Warning: $$ip cleanup failed"; \
			fi \
		) & \
	done; \
	wait
	@echo "Cleanup finished"
	@$(MAKE) hosts-clean
	@./stop_instances.sh

clean-ec2: check-ssh-key
	@echo "Cleaning EC2 node data (public IPs only)..."
	@for ip in $$(awk '{if ($$1 !~ /^172\./ && ($$2 ~ /^node/ || $$2 ~ /^client/)) print $$1}' hosts.txt); do \
		echo "→ Cleaning $$ip ..."; \
		ssh $(SSH_OPTS) $(SSH_USER)@$$ip "sudo rm -rf ~/hotstuff" || echo "Warning: $$ip cleanup failed"; \
	done
	@echo "Cleanup finished"

clean-images: check-ssh-key
	@echo "Cleaning old images on EC2 nodes..."
	@for node in $(NODES) $(CLIENT); do \
		( \
			echo "→ $$node"; \
			if ssh $(SSH_OPTS) $$node "docker system prune -a -f --volumes"; then \
				echo "$$node image cleanup complete"; \
			else \
				echo "Warning: $$node image cleanup failed"; \
			fi \
		) & \
	done; \
	wait
	@echo "Image cleanup complete"

deploy-adv: check-ssh-key
	@node=$$(awk '$$2 ~ /^node[0-9]+$$/ {print "$(SSH_USER)@"$$1; exit}' hosts.txt); \
	if [ -z "$$node" ]; then \
		echo "No eligible nodes found in hosts.txt"; \
		exit 1; \
	fi; \
	echo "$$node" > $(ADV_NODE_FILE); \
		host_ip=$${node##*@}; \
		node_name=$$(awk -v ip="$$host_ip" '$$1==ip {print $$2}' hosts.txt); \
		if [ -z "$$node_name" ]; then \
			echo "Failed to map $$host_ip to a node name from hosts.txt"; \
			exit 1; \
		fi; \
	echo "Deploying docker-compose-adv.yml to $$node_name ($$host_ip)..."; \
		ssh $(SSH_OPTS) $$node "mkdir -p $(ADV_REMOTE_DIR)/logs"; \
		scp $(SSH_OPTS) $(ADV_COMPOSE_FILE) $$node:$(ADV_REMOTE_DIR)/$(ADV_REMOTE_COMPOSE); \
		env_file="envs/$$node_name.env"; \
		if [ ! -f "$$env_file" ]; then \
			echo "Env file $$env_file not found"; \
			exit 1; \
		fi; \
		scp $(SSH_OPTS) "$$env_file" $$node:$(ADV_REMOTE_DIR)/$(ADV_REMOTE_ENV); \
	echo "Adversary compose + env deployed to $${node_name:-$$host_ip}. Target recorded in $(ADV_NODE_FILE)."; \
	echo "Selected adversary node: $$node_name ($$host_ip)"

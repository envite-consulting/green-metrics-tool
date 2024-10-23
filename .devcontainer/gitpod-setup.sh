#!/bin/bash
set -euxo pipefail

# Sometimes in Gitpod the path to our repo is `/workspaces/green-metrics-tool`, sometimes it is `/workspaces/workspaces`
# To not rely on absolute paths we use relative paths instead
MY_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
GMT_DIR=$(builtin cd $MY_DIR/../; pwd)

# We have to rename this makefile as it doesn't compile in Codespaces/Gitpod
if [ -f "${GMT_DIR}/metric_providers/lm_sensors/Makefile" ]; then
    mv "${GMT_DIR}/metric_providers/lm_sensors/Makefile" "${GMT_DIR}/metric_providers/lm_sensors/Makefile.bak"
fi

# Install Green Metrics Tool
# Using public ports (https://www.gitpod.io/docs/flex/integrations/ports) didn't worked with Gitpod Flex (tested on 2024-10-24)
"${GMT_DIR}/install_linux.sh" -p testpw -a "http://localhost:9142" -m "http://localhost:9143" -t -i -s
source venv/bin/activate

# make edits to ports so we can use 9143 to access the front end
sed -i 's/listen \[::\]:9142;/listen [::]:9143;/; s/listen 9142;/listen 9143;/' $GMT_DIR/docker/nginx/frontend.conf
sed -i '/green-coding-nginx:/,/green-coding-gunicorn:/ s/\(- 9142:80\)/- 9142:9142\n      - 9143:9143/' $GMT_DIR/docker/compose.yml

# Also add XGBoost, as we need it
python3 -m pip install -r $GMT_DIR/metric_providers/psu/energy/ac/xgboost/machine/model/requirements.txt

# Disable unavailable metric providers
python3 $GMT_DIR/disable_metric_providers.py --categories CPU GPU RAPL Machine Sensors Debug --providers NetworkIoCgroupContainerProvider NetworkConnectionsProxyContainerProvider PsuEnergyAcSdiaMachineProvider

git clone https://github.com/green-coding-berlin/example-applications.git --depth=1 --single-branch $GMT_DIR/example-applications || true

# Start GMT containers
docker compose -f $GMT_DIR/docker/compose.yml down
docker compose -f $GMT_DIR/docker/compose.yml up -d

#!/bin/bash
set -euxo pipefail

# Sometimes in Gitpod the path to our repo is `/workspaces/green-metrics-tool`, sometimes it is `/workspaces/workspaces`
# To not rely on absolute paths we use relative paths instead
MY_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
GMT_DIR=$(builtin cd $MY_DIR/../; pwd)

# Install Green Metrics Tool
# Using public ports (https://www.gitpod.io/docs/flex/integrations/ports) didn't worked with Gitpod Flex (tested on 2024-10-24)
"${GMT_DIR}/install_linux.sh" -p testpw -a "http://localhost:9142" -m "http://localhost:9143" -t -i -s -l
source venv/bin/activate

# Also add XGBoost, as we need it
python3 -m pip install -r $GMT_DIR/metric_providers/psu/energy/ac/xgboost/machine/model/requirements.txt

# make edits to ports so we can use 9143 to access the front end
sed -i 's/listen \[::\]:9142;/listen [::]:9143;/; s/listen 9142;/listen 9143;/' $GMT_DIR/docker/nginx/frontend.conf
sed -i 's/- 9142:9142/- 9142:9142\n      - 9143:9143/' $GMT_DIR/docker/compose.yml
sed -i 's|- ./nginx/block.conf|#- ./nginx/block.conf|' $GMT_DIR/docker/compose.yml

# activate XGBoost provider with sane values for GitHub Codespaces
sed -i 's/common:/common:\n      psu.energy.ac.xgboost.machine.provider.PsuEnergyAcXgboostMachineProvider:\n        resolution: 99\n        CPUChips: 1\n        HW_CPUFreq: 2800\n        CPUCores: 32\n        CPUThreads: 64\n        TDP: 270\n        HW_MemAmountGB: 256\n        VHost_Ratio: 0.03125\n/' /workspaces/green-metrics-tool/config.yml


git clone https://github.com/green-coding-solutions/example-applications.git --depth=1 --single-branch $GMT_DIR/example-applications || true

# Start GMT containers
docker compose -f $GMT_DIR/docker/compose.yml down
docker compose -f $GMT_DIR/docker/compose.yml up -d

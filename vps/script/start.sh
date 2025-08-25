#!/bin/bash

# Source common variables and functions
source /script/common.sh

# Run installation scripts
/script/install-mono.sh
/script/install-mt5.sh

# Keep the script running
tail -f /dev/null
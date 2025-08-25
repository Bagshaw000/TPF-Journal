#!/bin/bash

# Source common variables and functions
source /scripts/common.sh

# Run installation scripts
/scripts/install-mono.sh
/scripts/install-mt5.sh

# Keep the script running
tail -f /dev/null
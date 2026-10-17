#!/usr/bin/env bash
# Prepares a fresh Linux server (e.g. vast.ai, Ubuntu) to run the analyses of the package:
# clones the repository, creates a Python environment with the exact package versions and
# downloads the PEtab benchmark problems. Run once, as root, from any folder:
#   curl -sL https://raw.githubusercontent.com/monicammr/archivos/main/reproducibility/scripts/setup_servidor.sh | bash
# or, after cloning:  bash archivos/reproducibility/scripts/setup_servidor.sh
set -euo pipefail
cd /root
if [ ! -d archivos ]; then
  git clone -q --depth 1 https://github.com/monicammr/archivos.git
fi
cd archivos && git pull -q || true
cd reproducibility
if [ ! -x /root/venv/bin/python ]; then
  python3 -m venv /root/venv 2>/dev/null || { apt-get -qq update && apt-get -qq install -y python3-venv git >/dev/null && python3 -m venv /root/venv; }
fi
/root/venv/bin/pip -q install --upgrade pip
/root/venv/bin/pip -q install -r requirements.txt
bash scripts/get_benchmark.sh
/root/venv/bin/python -c "import roadrunner, scipy, numpy; print('Python ready: libRoadRunner', roadrunner.__version__)"
echo "Ready. Cores: $(nproc). Next: export PATH=/root/venv/bin:\$PATH; cd /root/archivos/reproducibility"

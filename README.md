# debug-bench

sudo apt install build-essential python3-dev

./setup_dbgbench.sh

python3.10 -m venv venv
source venv/bin/activate

pip install -e .[test]

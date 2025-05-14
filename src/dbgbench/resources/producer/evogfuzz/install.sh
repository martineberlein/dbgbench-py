cd /root/Desktop
git clone https://github.com/martineberlein/evogfuzz
cd evogfuzz

python3 -m venv venv
. venv/bin/activate

pip install --upgrade pip

pip install -e .[dev]
pip install -r requirements.txt

deactivate
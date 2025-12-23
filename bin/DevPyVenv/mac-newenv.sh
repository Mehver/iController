cd ../..
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Virtual environment has been created and activated."
read -p "Press any key to continue... " -n1 -s
echo

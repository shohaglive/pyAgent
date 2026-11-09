echo "Setting up virtual environment.."
python3 -m venv venv
echo "Done, Now activating virtual environment..."
source venv/bin/activate
echo "Done! Installing components..."
pip install -r requirements.txt
echo "Done! Agent is ready. Run: python3 claude_agent.py to continue."

PYTHONPATH := ./src
run_tg:
	PYTHONPATH=$(PYTHONPATH) python3 src/app.py	
run_binance:
	PYTHONPATH=$(PYTHONPATH) python3 src/binance_api.
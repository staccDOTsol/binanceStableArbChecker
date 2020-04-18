from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from unicorn_fy.unicorn_fy import UnicornFy
from time import sleep
binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com")

markets = ['paxtusd', 'usdcpax','usdctusd','paxusdt','busdusdt','tusdusdt','usdcusdt','usdsusdt']
channels = ['ticker']

fee = 0.0240 * 2
fee = fee * 0.6
print(fee)
binance_websocket_api_manager.create_stream(channels, markets)
bids = {}
bidAmts = {}
asks = {}
askAmts = {}
alreadyDone = []
while True:
	oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
	if oldest_stream_data_from_stream_buffer:
		unicorn_fied_stream_data = UnicornFy.binance_com_websocket(oldest_stream_data_from_stream_buffer)
		
		if 'data' in unicorn_fied_stream_data:
			for d in unicorn_fied_stream_data['data']:
				bids[d['symbol']] = (d['best_bid_price'])
				asks[d['symbol']] = (d['best_ask_price'])
				bidAmts[d['symbol']] = (d['best_bid_quantity'])
				askAmts[d['symbol']] = (d['best_ask_quantity'])
	for order in bids:
		arb = (float(asks[order]) / float(bids[order]) - 1) * 100#/  1.1 / 0.9
		
		if arb > fee:
			if {'askAmts': askAmts[order], 'bidAmts': bidAmts[order]} not in alreadyDone:
				alreadyDone.append({'askAmts': askAmts[order], 'bidAmts': bidAmts[order]})
				print(order + ': ' + str(arb))
				if float(bidAmts[order]) < float(askAmts[order]):	
					print(str(bidAmts[order]) + ' available at this price!')
				else:
					print(str(askAmts[order]) + ' available at this price!')
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from unicorn_fy.unicorn_fy import UnicornFy
from time import sleep
binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com")

markets = ['paxtusd', 'usdcpax','usdctusd','paxusdt','busdusdt','tusdusdt','usdcusdt','usdsusdt']
channels = ['ticker']

tiers = {3: 0.06 * 0.6, 4: 0.054, 5: 0.048, 6: 0.042, 7:0.036, 8: 0.030, 9: 0.024}


winnersCounts = {}
winnersArbs = {}
winnersVols = {}
winnersArbsAvg = {}
for fee in tiers:
	tiers[fee] = tiers[fee] * 2
	winnersCounts[fee] = 0
	winnersArbs[fee] = []
	winnersVols[fee] = 0
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
		for tier in tiers:
			fee = tiers[tier]
			if arb > fee:
				if {fee: {'askAmts': askAmts[order], 'bidAmts': bidAmts[order]}} not in alreadyDone:
					alreadyDone.append({fee: {'askAmts': askAmts[order], 'bidAmts': bidAmts[order]}})

					winnersCounts[tier] = winnersCounts[tier] + 1
					winnersArbs[tier].append(arb)
					t = 0
					for winarb in winnersArbs[tier]:
						t = t + winarb
					winnersArbsAvg[tier] = t / winnersCounts[tier]
					
					print(order + ': ' + str(arb))
					if float(bidAmts[order]) < float(askAmts[order]):	
						winnersVols[tier] = winnersVols[tier]  + float(bidAmts[order])
					else:	
						winnersVols[tier] = winnersVols[tier]  + float(askAmts[order])
					print('winnerCounts')
					print(winnersCounts)
					print('winnerArbsAvg')
					print(winnersArbsAvg)
					print('winnerVols')
					print(winnersVols)
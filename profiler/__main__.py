from datamodel import TradingState, Observation, Listing, OrderDepth, Trade
import importlib.util as iu
from cProfile import Profile, run
import sys, os, pstats, io

def load_trader_class(file_path):
    '''
    returns the Trader object from a given file
    '''
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = iu.spec_from_file_location(module_name, file_path)
    module = iu.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "Trader"):
        raise AttributeError(f"Trader class not found in {file_path}")
    else:
        return getattr(module, "Trader")

def create_fake_state():
    fake_state = TradingState(
        traderData='{"test": "test"}',
        timestamp=1300,
        listings={
            "KELP": Listing(symbol="KELP", product="KELP", denomination=1),
            "RAINFOREST_RESIN": Listing(symbol="RAINFOREST_RESIN", product="RAINFOREST_RESIN", denomination=1),
        },
        order_depths={
            "KELP": OrderDepth(),
            "RAINFOREST_RESIN": OrderDepth(),
        },
        own_trades={},
        market_trades={
            "KELP": [
                Trade(symbol="KELP", price=2029, quantity=13, buyer="", seller="", timestamp=0),
                Trade(symbol="KELP", price=2029, quantity=1, buyer="", seller="", timestamp=0),
            ],
            "RAINFOREST_RESIN": [
                Trade(symbol="RAINFOREST_RESIN", price=9996, quantity=2, buyer="", seller="", timestamp=1100),
            ],
        },
        position={},
        observations=Observation(plainValueObservations={}, conversionObservations={}),
    )
    fake_state.order_depths["KELP"].buy_orders = {2024: 31}
    fake_state.order_depths["KELP"].sell_orders = {2028: -31}
    fake_state.order_depths["RAINFOREST_RESIN"].buy_orders = {9995: 30, 9996: 1, 10002: 1}
    fake_state.order_depths["RAINFOREST_RESIN"].sell_orders = {10004: -1, 10005: -30}

    return fake_state

def main():
    file_path = sys.argv[1]
    trader_class = load_trader_class(file_path)
    trader_class_instance = trader_class()
    
    fake_state = create_fake_state()

    #generate prof file for visualizations with snakeviz (pip install snakeviz)
    run("trader_class_instance.run(fake_state)", "prof.prof")
    #generate prof stats
    profiler = Profile()
    profiler.enable()
    trader_class_instance.run(fake_state)
    profiler.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

from profiler.datamodel import TradingState, Observation, Listing, OrderDepth, Trade
from pathlib import Path
from importlib import import_module, metadata, reload
import importlib.util as iu
from cProfile import Profile, runctx
import sys, os, pstats, io, subprocess

def load_trader_class(algorithm: str):
    algorithm_path = Path(algorithm).expanduser().resolve()
    if not algorithm_path.is_file():
        raise ModuleNotFoundError(f"{algorithm_path} is not a file")

    sys.path.append(str(algorithm_path.parent))
    return import_module(algorithm_path.stem)

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
    trader_instance = load_trader_class(file_path).Trader()
    fake_state = create_fake_state()

    # Define a known directory for the profiling file
    profile_dir = Path("./profiles")
    profile_dir.mkdir(exist_ok=True)  # Create if it doesn’t exist

    prof_file = profile_dir / "prof.prof"

    # Generate profiling file for SnakeViz
    runctx("trader_instance.run(fake_state)", globals(), locals(), filename=str(prof_file))

    # Generate profiling stats
    profiler = Profile()
    profiler.enable()
    trader_instance.run(fake_state)
    profiler.disable()

    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

    # Run SnakeViz automatically
    print(f"\nOpening SnakeViz for {prof_file}...\n")
    subprocess.run(["snakeviz", str(prof_file)])  # Launch SnakeViz visualization

if __name__ == "__main__":
    main()

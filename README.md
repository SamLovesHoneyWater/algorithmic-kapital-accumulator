# algorithmic-kapital-accumulator
Algorithmic Kapital Accumulator, aka "AKA", aims at delivering cutting-edge wealth management strategies designed to achieve rapid capital accumulation.
AKA understands that capital lies at the center of portfolio growth.
We make use of capital to enable a wide range of accumulation options: ~~domination~~ leveraging market influence, ~~dispossession~~ optimizing resource reallocation, ~~extraction~~ capitalizing on value extraction, and ~~oppression~~ enhancing competitive positioning.

## Getting Started

First install dependencies, listed in requirements.txt

Second, go to Alpaca's website and apply for a trading account. Then obtain the secrets for your trading and paper accounts and add them to environment variables.

You are ready! Code is at src/main.py

## Understanding the Code

Look in src/models for objects used in the code. 

An **Investor** represents a person that is investing, and it can have multiple **BrokerAccount**s.

Each **Asset**, such as NVDA stock, should only be instantiated once.
When instantiating an asset, we need to define a quote_fn that is used to get this asset's latest quote.
This function should be defined in the main program an fed to an Asset object upon instantiation.
Notice that this function takes in an asset_name variable, so assets of the same type can use the same quote_fn.

Each **Order** has an **OrderType** and an **OrderSide**, these are from the Alpaca SDK: https://alpaca.markets/sdks/python/api_reference/trading/enums.html.

Some objects are either not used or under development. These include: **HeldAsset**, **Strategy**, and **Transaction**.

## Modifying the Code

The code is heavily typed. Since the code might be used to trade real money, typechecking is employed to ensure the correctness of the code.
When writing functions and methods, make sure to provide type definitions that specify the types of the inputs and output.

Before starting, you need to install static type checker mypy. A plugin is available for VSCode.
To type check a piece of code, run "mypy main.py" in a terminal. If it fails, you have to fix your code or type declarations accordingly.

*Code that fails type check will not be accepted into the main branch.*

In src/models/datatypes, you will see several basic types defined, such as numeric types "Capital", "Quantity", "Price" as well as enum types such as "AssetType".
Use those types when writing code to avoid confusion between variables of different types.
For typing support, visit https://docs.python.org/3/library/typing.html.
For type errors in importing external modules, see https://mypy.readthedocs.io/en/stable/running_mypy.html.

A "# type ignore" comment can be added to the end of a line of code to prevent the type checker from checking it.
"Type ignore" should only be used in the case of a "Missing library stubs or py.typed marker" error, when all viable fixes have been exhausted.
Remember, **A Type Check error usually means a mistake in the code!**

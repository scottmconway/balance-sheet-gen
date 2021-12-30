# Balance Sheet Gen
This repo contains a script to fetch (and one day cleanly output) balance information from a variety of financial institutions, for the purpose of automating adding entries to a balance sheet.

## Requirements
* python >= 3.6
* see requirements.txt

## Usage
`python3 balance_sheet_gen --config $PATH_TO_CONFIG_FILE`

If `--config` is not provided, the local file `./config.json` is read.

## Configuration
See config.json.example for an example configuration.

Eventually, I want to feed data into a CSV (or similar spreadsheet format) balance sheet,
so "columns" are used. Each column has an institution type, name, and configuration.

For example, if you have multiple accounts with the same provider, this configuration allows them to be tracked separately, by making multiple columns of the same type, but with differing configurations.

## Institutions
Institutions are the objects that can be defined under the "type" field in a given column. They are an interface with one method - `get_balance()`. Simply put, the institution returns its balance for the user-defined configuration.

`get_balance()` should always return USD, unless otherwise specified.

### Bitcoin Institution
This institution checks a series of wallet addresses against blockchain.info's API and returns the sum of BTC in USD, according to coingecko.

#### Configuration
|Name|Type|Description|
|-|-|-|
|`wallet_addrs`|List[str]|A list of valid BTC addresses to check|

### Chia Institution
This institution checks a series of wallet addresses against xchscan's API and returns the sum of BTC in USD, according to coingecko.

#### Configuration
|Name|Type|Description|
|-|-|-|
|`wallet_addrs`|List[str]|A list of valid XCH addresses to check|

### Coinbase Institution
This institution uses the Coinbase API to pull the total USD value of all assets summed together. The USD value is provided directly by Coinbase's API.

The provided API token must have the `wallet:accounts:read` scope for this Insitution to function. API tokens can be generated here: [https://www.coinbase.com/settings/api](https://www.coinbase.com/settings/api)

Note that this Institution does _not_ get accounts / balances from Coinbase Pro.

#### Configuration
|Name|Type|Description|
|-|-|-|
|`api_key`|str|A valid API key for Coinbase's API|
|`api_secret`|str|A valid API secret for Coinbase's API|

### Helium Institution
This institution checks a series of Helium (HNT) wallet addresses against helium.io's API and returns the sum of BTC in USD, according to coingecko.

#### Configuration
|Name|Type|Description|
|-|-|-|
|`wallet_addrs`|List[str]|A list of valid HNT addresses to check|

### Discover Bank Institution
Coming soon!

### Venmo Institution
Coming soon!

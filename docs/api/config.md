# Configuration Reference

## API Configuration

::: osmdiff.config.API_CONFIG
    options:
      heading_level: 2
      show_source: true

## AugmentedDiff Defaults

::: osmdiff.config.AUGMENTED_DIFF_CONFIG
    options:
      heading_level: 2
      show_source: true

## HTTP Settings

::: osmdiff.config.DEFAULT_HEADERS
    options:
      heading_level: 2
      show_source: true

::: osmdiff.config.USER_AGENT
    options:
      heading_level: 2
      show_source: true

## Overriding Configuration

```python
from osmdiff import AugmentedDiff
from osmdiff.config import API_CONFIG

# Modify configuration before use
API_CONFIG["overpass"]["timeout"] = 60  # Increase timeout

adiff = AugmentedDiff()  # Will use updated configuration
```

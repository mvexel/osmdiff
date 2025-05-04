# Changelog

## v0.4.6 (2025-05-04)

**This version fixes some critical bugs in 0.4.5, existing users should upgrade immediately**

### ✅ Testing Improvements
- Added comprehensive tests for OSM object geo interfaces (Node, Way, Relation)
- Added coordinate validation tests for Node class
- Added tests for Member class parsing and geo interface
- Improved test coverage for Way.length() method
- Added equality comparison tests for Node objects

### 🐛 Bug Fixes
- Fixed critical bugs in `AugmentedDiff` and `ContinuousAugmentedDiff`
    - state fetching
    - iteration
- Fixed coordinate validation in Node class to properly handle edge cases
- Improved error messages for invalid coordinates

### 📖 Documentation
- Added more detailed docstrings for geo interface methods
- Improved examples in OSM object class documentation

## v0.4.5 (2025-05-03)

### 🚀 Features
- Add `ContinuousAugmentedDiff` to package exports
- Add continuous augmented-diff fetcher with back-off strategy
- Add `actions` property to `OSMChange` and `AugmentedDiff`
- Update Overpass API base URL to the new endpoint
- Provide `__geo_interface__` example

### 🐛 Bug Fixes
- Properly return deleted features (fixes #43)
- Correct state-parsing and response handling in diff APIs
- Capture metadata for deleted objects in `AugmentedDiff` parser
- Fix various API-test mocks (raw streams, gzipped responses, missing imports)
- Clean up test assertions and fixtures for all API scenarios

### ♻️ Refactoring
- Convert `test_augmenteddiff.py` to pytest + fixtures
- Switch Overpass base-URL code to use a sequence template
- Switch from PDM to hatchling build system
- Enforce Black formatting

### 📖 Documentation
- Add "Continuous Augmented Diff" section to README
- Update docstring & class docs for `ContinuousAugmentedDiff`

### ✅ Testing Improvements
- Continue increasing overall test coverage
- Add tests for continuous augmented-diff, metadata capture & plumbbin
- Improve API tests with better mocks, error cases & assertions

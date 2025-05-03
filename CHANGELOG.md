# Changelog

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

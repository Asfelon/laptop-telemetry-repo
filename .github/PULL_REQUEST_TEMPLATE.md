## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test updates
- [ ] CI/CD changes
- [ ] Dependency updates

## Related Issues

Closes #(issue number)
Relates to #(issue number)

## Changes Made

- Change 1
- Change 2
- Change 3

## Testing

- [ ] Unit tests pass (`pytest`)
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing performed (describe below)

### Manual Testing Steps

1. Step 1
2. Step 2
3. Verify expected behavior

### Test Configuration Used

```yaml
# Paste config used for testing
collection:
  interval_seconds: 10
collectors:
  cpu:
    enabled: true
```

## Checklist

### Code Quality
- [ ] Code follows project style guidelines (Ruff, MyPy)
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings from linter/type checker

### Documentation
- [ ] README.md updated (if user-facing changes)
- [ ] docs/configuration.md updated (if config changes)
- [ ] docs/hardware_support.md updated (if sensor changes)
- [ ] docs/troubleshooting.md updated (if known issues)
- [ ] Docstrings added/updated for public APIs

### Changelog
- [ ] CHANGELOG.md updated under `[Unreleased]` section

### Tests
- [ ] Tests added for new functionality
- [ ] Tests updated for changed behavior
- [ ] Edge cases covered

### Configuration
- [ ] Config schema updated (if new options)
- [ ] Default config updated (if applicable)
- [ ] Environment variable overrides documented

## Screenshots / Logs

If applicable, add screenshots or log output demonstrating the changes.

## Additional Notes

Any additional information, concerns, or context for reviewers.
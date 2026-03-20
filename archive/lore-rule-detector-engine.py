# Lore Validation Engine

class LoreRuleDetectorEngine:
    def __init__(self, rules):
        self.rules = rules

    def validate(self, lore):
        for rule in self.rules:
            if not rule(lore):
                return False
        return True

# Example usage
if __name__ == '__main__':
    def example_rule(lore):
        return 'ancient' in lore.lower()

    engine = LoreRuleDetectorEngine([example_rule])
    print(engine.validate('This is an ancient lore.'))  # Should print True
    print(engine.validate('This is a modern lore.'))   # Should print False

class Config:
    def __init__(self):
        self.operator_data_file = "data/operators.json"
        self.default_rarity = [3, 4, 5]
        self.default_classes = ["Guard", "Sniper", "Caster", "Medic"]
        self.enable_randomizer = True
        self.enable_filter = True

    def load_config(self):
        # Load configuration from a file or environment variables if needed
        pass

    def save_config(self):
        # Save current configuration to a file
        pass
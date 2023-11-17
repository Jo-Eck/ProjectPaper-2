from pathlib import Path

class Categorizer:
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
    def can_handle(self, file_path: str) -> bool:
        raise NotImplementedError
    
    def categorize(self, file_path: str, categorized_files: dict) -> None:
        raise NotImplementedError

class AuxiliaryCategorizer(Categorizer):
    def __init__(self, auxiliary_pattern):
        self.auxiliary_pattern = auxiliary_pattern

    def can_handle(self, file_path: str) -> bool:
        return self.auxiliary_pattern(file_path)
    
    def categorize(self, file_path: str, categorized_files: dict) -> None:
        categorized_files.setdefault("auxiliaries", []).append(file_path)

class LanguageCategorizer(Categorizer):
    def can_handle(self, file_path: str) -> bool:
        return True
    
    def categorize(self, file_path: str, categorized_files: dict) -> None:
        lang = detect_language(file_path)
        if lang:
            categorized_files.setdefault("code", {}).setdefault(lang, []).append(file_path)

class ExtensionCategorizer(Categorizer):
    def __init__(self, language_config):
        self.language_config = language_config
    
    def can_handle(self, file_path: str) -> bool:
        file_extension = Path(file_path).suffix
        return any(config.get("file_extension") == file_extension for config in self.language_config.values())
    
    def categorize(self, file_path: str, categorized_files: dict) -> None:
        file_extension = Path(file_path).suffix
        for language, config in self.language_config.items():
            if config.get("file_extension") == file_extension:
                categorized_files.setdefault("code", {}).setdefault(language, []).append(file_path)
                break

class YamlCategorizer(Categorizer):
    def can_handle(self, file_path: str) -> bool:
        return Path(file_path).suffix in ['.yaml', '.yml']
    
    def categorize(self, file_path: str, categorized_files: dict) -> None:
        with open(file_path, 'r') as file:
            content = file.read()
            if '"pipeline":' in content:
                categorized_files.setdefault("pipeline", []).append(file_path)
            else:
                categorized_files.setdefault("unknown", []).append(file_path)

class JsonCategorizer(Categorizer):
    def can_handle(self, file_path: str) -> bool:
        return Path(file_path).suffix == '.json'
    
    def categorize(self, file_path: str, categorized_files: dict) -> None:
        with open(file_path, 'r') as file:
            content = file.read()
            if '"repo":' in content:
                categorized_files.setdefault("datasource", []).append(file_path)
            else:
                categorized_files.setdefault("unknown", []).append(file_path)

from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self) -> None:
        self._storage: list[tuple[int, str]] = []
        self._processed: int = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def _store(self, item: str) -> None:
        self._storage.append((self._processed, item))
        self._processed += 1

    def output(self) -> tuple[int, str]:
        if len(self._storage) == 0:
            raise IndexError("No data left on processor")
        return self._storage.pop(0)


class NumericProcessor(DataProcessor):
    def _is_number(self, value: Any) -> bool:
        if isinstance(value, bool):
            return False
        return isinstance(value, (int, float))

    def validate(self, data: Any) -> bool:
        if self._is_number(data):
            return True
        if isinstance(data, list) and len(data) > 0:
            for item in data:
                if not self._is_number(item):
                    return False
            return True
        return False

    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")
        if isinstance(data, list):
            for item in data:
                self._store(str(item))
        else:
            self._store(str(data))


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        if isinstance(data, list) and len(data) > 0:
            for item in data:
                if not isinstance(item, str):
                    return False
            return True
        return False

    def ingest(self, data: str | list[str]) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")
        if isinstance(data, list):
            for item in data:
                self._store(item)
        else:
            self._store(data)


class LogProcessor(DataProcessor):
    def _is_log(self, value: Any) -> bool:
        if not isinstance(value, dict) or len(value) == 0:
            return False
        for key, content in value.items():
            if not isinstance(key, str) or not isinstance(content, str):
                return False
        return True

    def validate(self, data: Any) -> bool:
        if self._is_log(data):
            return True
        if isinstance(data, list) and len(data) > 0:
            for item in data:
                if not self._is_log(item):
                    return False
            return True
        return False

    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")
        if isinstance(data, list):
            for entry in data:
                self._store(": ".join(entry.values()))
        else:
            self._store(": ".join(data.values()))


def extract(processor: DataProcessor, amount: int, label: str) -> None:
    if amount == 1:
        print(" Extracting 1 value...")
    else:
        print(f" Extracting {amount} values...")
    for _ in range(amount):
        rank, value = processor.output()
        print(f" {label} {rank}: {value}")


def test_numeric() -> None:
    print("Testing Numeric Processor...")
    numeric: NumericProcessor = NumericProcessor()
    print(f" Trying to validate input '42': {numeric.validate(42)}")
    print(f" Trying to validate input 'Hello': {numeric.validate('Hello')}")
    print(" Test invalid ingestion of string 'foo' without prior validation:")
    try:
        numeric.ingest("foo")
    except ValueError as e:
        print(f" Got exception: {e}")
    data: list[int | float] = [1, 2, 3, 4, 5]
    print(f" Processing data: {data}")
    numeric.ingest(data)
    extract(numeric, 3, "Numeric value")


def test_text() -> None:
    print("Testing Text Processor...")
    text: TextProcessor = TextProcessor()
    print(f" Trying to validate input '42': {text.validate(42)}")
    data: list[str] = ["Hello", "Nexus", "World"]
    print(f" Processing data: {data}")
    text.ingest(data)
    extract(text, 1, "Text value")


def test_log() -> None:
    print("Testing Log Processor...")
    log: LogProcessor = LogProcessor()
    print(f" Trying to validate input 'Hello': {log.validate('Hello')}")
    data: list[dict[str, str]] = [
        {"log_level": "NOTICE", "log_message": "Connection to server"},
        {"log_level": "ERROR", "log_message": "Unauthorized access!!"},
    ]
    print(f" Processing data: {data}")
    log.ingest(data)
    extract(log, 2, "Log entry")


def main() -> None:
    print("=== Code Nexus - Data Processor ===")
    print()
    test_numeric()
    print()
    test_text()
    print()
    test_log()


if __name__ == "__main__":
    main()

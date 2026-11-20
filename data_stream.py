from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self, name: str) -> None:
        self._name: str = name
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

    def get_name(self) -> str:
        return self._name

    def get_processed(self) -> int:
        return self._processed

    def get_remaining(self) -> int:
        return len(self._storage)


class NumericProcessor(DataProcessor):
    def __init__(self) -> None:
        super().__init__("Numeric Processor")

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
    def __init__(self) -> None:
        super().__init__("Text Processor")

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
    def __init__(self) -> None:
        super().__init__("Log Processor")

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


class DataStream:
    def __init__(self) -> None:
        self._processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self._processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        for element in stream:
            handled: bool = False
            for proc in self._processors:
                if proc.validate(element):
                    try:
                        proc.ingest(element)
                        handled = True
                    except ValueError as e:
                        print(f"DataStream error - {e}")
                    break
            if not handled:
                print("DataStream error - "
                      f"Can't process element in stream: {element}")

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if len(self._processors) == 0:
            print("No processor found, no data")
        for proc in self._processors:
            print(f"{proc.get_name()}: total {proc.get_processed()} "
                  f"items processed, remaining {proc.get_remaining()} "
                  "on processor")


def consume(proc: DataProcessor, amount: int) -> None:
    for _ in range(amount):
        if proc.get_remaining() == 0:
            return
        proc.output()


def main() -> None:
    print("=== Code Nexus - Data Stream ===")
    print()
    print("Initialize Data Stream...")
    stream: DataStream = DataStream()
    stream.print_processors_stats()
    print()
    print("Registering Numeric Processor")
    numeric: NumericProcessor = NumericProcessor()
    stream.register_processor(numeric)
    print()
    batch: list[Any] = [
        "Hello world",
        [3.14, -1, 2.71],
        [
            {"log_level": "WARNING",
             "log_message": "Telnet access! Use ssh instead"},
            {"log_level": "INFO",
             "log_message": "User wil is connected"},
        ],
        42,
        ["Hi", "five"],
    ]
    print(f"Send first batch of data on stream: {batch}")
    stream.process_stream(batch)
    stream.print_processors_stats()
    print()
    print("Registering other data processors")
    text: TextProcessor = TextProcessor()
    log: LogProcessor = LogProcessor()
    stream.register_processor(text)
    stream.register_processor(log)
    print("Send the same batch again")
    stream.process_stream(batch)
    stream.print_processors_stats()
    print()
    print("Consume some elements from the data processors: "
          "Numeric 3, Text 2, Log 1")
    consume(numeric, 3)
    consume(text, 2)
    consume(log, 1)
    stream.print_processors_stats()


if __name__ == "__main__":
    main()

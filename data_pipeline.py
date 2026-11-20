from abc import ABC, abstractmethod
from typing import Any, Protocol


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


class ExportPlugin(Protocol):
    def process_output(self, data: list[tuple[int, str]]) -> None:
        ...


class CSVExportPlugin:
    def _escape(self, value: str) -> str:
        if "," in value or '"' in value or "\n" in value:
            return '"' + value.replace('"', '""') + '"'
        return value

    def process_output(self, data: list[tuple[int, str]]) -> None:
        values: list[str] = [self._escape(value) for _, value in data]
        print("CSV Output:")
        print(",".join(values))


class JSONExportPlugin:
    def _escape(self, value: str) -> str:
        escaped: str = value.replace("\\", "\\\\").replace('"', '\\"')
        return escaped.replace("\n", "\\n").replace("\t", "\\t")

    def process_output(self, data: list[tuple[int, str]]) -> None:
        pairs: list[str] = [f'"item_{rank}": "{self._escape(value)}"'
                            for rank, value in data]
        print("JSON Output:")
        print("{" + ", ".join(pairs) + "}")


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

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        for proc in self._processors:
            data: list[tuple[int, str]] = []
            while len(data) < nb and proc.get_remaining() > 0:
                data.append(proc.output())
            if len(data) > 0:
                plugin.process_output(data)


def main() -> None:
    print("=== Code Nexus - Data Pipeline ===")
    print()
    print("Initialize Data Stream...")
    print()
    stream: DataStream = DataStream()
    stream.print_processors_stats()
    print()
    print("Registering Processors")
    stream.register_processor(NumericProcessor())
    stream.register_processor(TextProcessor())
    stream.register_processor(LogProcessor())
    print()
    first_batch: list[Any] = [
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
    print(f"Send first batch of data on stream: {first_batch}")
    stream.process_stream(first_batch)
    print()
    stream.print_processors_stats()
    print()
    print("Send 3 processed data from each processor to a CSV plugin:")
    stream.output_pipeline(3, CSVExportPlugin())
    print()
    stream.print_processors_stats()
    print()
    second_batch: list[Any] = [
        21,
        ["I love AI", "LLMs are wonderful", "Stay healthy"],
        [
            {"log_level": "ERROR", "log_message": "500 server crash"},
            {"log_level": "NOTICE",
             "log_message": "Certificate expires in 10 days"},
        ],
        [32, 42, 64, 84, 128, 168],
        "World hello",
    ]
    print(f"Send another batch of data: {second_batch}")
    stream.process_stream(second_batch)
    print()
    stream.print_processors_stats()
    print()
    print("Send 5 processed data from each processor to a JSON plugin:")
    stream.output_pipeline(5, JSONExportPlugin())
    print()
    stream.print_processors_stats()


if __name__ == "__main__":
    main()

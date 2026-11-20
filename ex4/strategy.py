from abc import ABC, abstractmethod

from ex3.capability import TransformCapability
from ex3.creature import Creature


class InvalidStrategyError(Exception):
    def __init__(self, message: str = "Invalid strategy") -> None:
        super().__init__(message)


class BattleStrategy(ABC):
    def __init__(self, name: str) -> None:
        self._name: str = name

    @abstractmethod
    def is_valid(self, creature: Creature) -> bool:
        pass

    @abstractmethod
    def act(self, creature: Creature) -> None:
        pass

    def get_name(self) -> str:
        return self._name


class NormalStrategy(BattleStrategy):
    def __init__(self) -> None:
        super().__init__("Normal")

    def is_valid(self, creature: Creature) -> bool:
        return isinstance(creature, Creature)

    def act(self, creature: Creature) -> None:
        if not self.is_valid(creature):
            raise InvalidStrategyError(
                f"Invalid Creature '{creature.get_name()}' "
                "for this normal strategy")
        print(creature.attack())


class AggressiveStrategy(BattleStrategy):
    def __init__(self) -> None:
        super().__init__("Aggressive")

    def is_valid(self, creature: Creature) -> bool:
        return isinstance(creature, TransformCapability)

    def act(self, creature: Creature) -> None:
        if not isinstance(creature, TransformCapability):
            raise InvalidStrategyError(
                f"Invalid Creature '{creature.get_name()}' "
                "for this aggressive strategy")
        print(creature.transform())
        print(creature.attack())
        print(creature.revert())

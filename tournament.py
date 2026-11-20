from ex3 import CreatureFactory, FlameFactory, TransformCreatureFactory
from ex4 import (AggressiveStrategy, BattleStrategy, InvalidStrategyError,
                 NormalStrategy)


def battle(opponents: list[tuple[CreatureFactory, BattleStrategy]]) -> None:
    fighters = [(factory.create_base(), strategy)
                for factory, strategy in opponents]
    roster: list[str] = [f"({creature.get_name()}+{strategy.get_name()})"
                         for creature, strategy in fighters]
    print(f" [ {', '.join(roster)} ]")
    print("*** Tournament ***")
    print(f"{len(fighters)} opponents involved")
    try:
        for i in range(len(fighters)):
            for j in range(i + 1, len(fighters)):
                first, first_strategy = fighters[i]
                second, second_strategy = fighters[j]
                print()
                print("* Battle *")
                print(first.describe())
                print(" vs.")
                print(second.describe())
                print(" now fight!")
                first_strategy.act(first)
                second_strategy.act(second)
    except InvalidStrategyError as e:
        print(f"Battle error, aborting tournament: {e}")


def main() -> None:
    flame: FlameFactory = FlameFactory()
    transform: TransformCreatureFactory = TransformCreatureFactory()
    normal: NormalStrategy = NormalStrategy()
    aggressive: AggressiveStrategy = AggressiveStrategy()
    print("Tournament 0 (basic)")
    battle([(flame, normal), (transform, aggressive)])
    print()
    print("Tournament 1 (error)")
    battle([(transform, aggressive), (flame, aggressive)])
    print()
    print("Tournament 2 (multiple)")
    battle([(flame, normal), (transform, aggressive), (transform, normal)])


if __name__ == "__main__":
    main()

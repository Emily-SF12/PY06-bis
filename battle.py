from ex3 import CreatureFactory, FlameFactory, TransformCreatureFactory


def test_factory(factory: CreatureFactory) -> None:
    print("Testing factory")
    base = factory.create_base()
    evolved = factory.create_evolved()
    print(base.describe())
    print(base.attack())
    print(evolved.describe())
    print(evolved.attack())


def test_battle(first: CreatureFactory, second: CreatureFactory) -> None:
    print("Testing battle")
    fighter_one = first.create_base()
    fighter_two = second.create_base()
    print(fighter_one.describe())
    print(" vs.")
    print(fighter_two.describe())
    print(" fight!")
    print(fighter_one.attack())
    print(fighter_two.attack())


def main() -> None:
    flame: FlameFactory = FlameFactory()
    transform: TransformCreatureFactory = TransformCreatureFactory()
    test_factory(flame)
    print()
    test_factory(transform)
    print()
    test_battle(flame, transform)


if __name__ == "__main__":
    main()

from pytest import CaptureFixture

from .main import main


def test_main(capsys: CaptureFixture[str]) -> None:
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello World!\n"
